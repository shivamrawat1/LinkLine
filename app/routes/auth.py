from flask import Blueprint, request, jsonify, redirect, url_for, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import datetime
import os
import sys
import subprocess
import time

auth_bp = Blueprint('auth', __name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Global variable to track email reply server process
email_reply_server_process = None
email_reply_server_active = False

# Server start time to track restarts
SERVER_START_TIME = datetime.datetime.now()

@auth_bp.route("/start_auth", methods=["GET", "POST"])
def start_auth():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type='offline', 
        include_granted_scopes='true',
        prompt='consent'  # Force consent screen to show
    )
    print(auth_url)
    session['state'] = state
    return redirect(auth_url)

@auth_bp.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    
    # Store credentials with timestamp
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'auth_time': datetime.datetime.now().isoformat()
    }
    
    # Redirect back to results page
    return redirect(url_for('main.index'))

@auth_bp.route("/logout")
def logout():
    # Alternative way to remove specific keys
    if 'credentials' in session:
        del session['credentials']

    # Method 2: Clear everything else
    session.clear()
    
    # Method 3: Force session save
    session.modified = True
    
    return redirect(url_for("main.login"))

@auth_bp.route("/status")
def auth_status():
    """Check authentication status"""
    credentials = get_gmail_credentials_from_session()
    is_authenticated = credentials is not None
    
    return jsonify({
        "authenticated": is_authenticated,
        "auth_url": url_for('auth.start_auth', _external=True) if not is_authenticated else None
    })

def get_gmail_credentials_from_session():
    """Get Gmail credentials from session, checking for expiration"""
    creds_dict = session.get('credentials')
    if not creds_dict:
        return None
    
    # Check if credentials are from before server restart
    if 'auth_time' in creds_dict:
        try:
            auth_time = datetime.datetime.fromisoformat(creds_dict['auth_time'])
            if auth_time < SERVER_START_TIME:
                # Credentials are from before server restart, clear them
                session.pop('credentials', None)
                return None
        except (ValueError, TypeError):
            # Invalid timestamp format, clear credentials
            session.pop('credentials', None)
            return None
    else:
        # Old format credentials without timestamp, clear them
        session.pop('credentials', None)
        return None
    
    try:
        return Credentials(
            creds_dict['token'],
            refresh_token=creds_dict.get('refresh_token'),
            token_uri=creds_dict['token_uri'],
            client_id=creds_dict['client_id'],
            client_secret=creds_dict['client_secret'],
            scopes=creds_dict['scopes']
        )
    except (KeyError, TypeError):
        # Invalid credentials format, clear them
        session.pop('credentials', None)
        return None

def start_email_reply_server(credentials):
    """Start the email reply MCP server in a separate process"""
    global email_reply_server_process, email_reply_server_active
    
    if email_reply_server_active:
        return "Email reply server is already running"
    
    try:
        # Start the MCP server process
        server_script = os.path.join(os.path.dirname(__file__), "..", "agents", "email_reply_server.py")
        email_reply_server_process = subprocess.Popen(
            [sys.executable, server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        if email_reply_server_process.poll() is None:
            email_reply_server_active = True
            return "Email reply server started successfully"
        else:
            return "Failed to start email reply server"
            
    except Exception as e:
        return f"Error starting email reply server: {str(e)}"

def stop_email_reply_server():
    """Stop the email reply MCP server"""
    global email_reply_server_process, email_reply_server_active
    
    if not email_reply_server_active:
        return "Email reply server is not running"
    
    try:
        if email_reply_server_process:
            email_reply_server_process.terminate()
            email_reply_server_process.wait(timeout=5)
        email_reply_server_active = False
        return "Email reply server stopped successfully"
    except Exception as e:
        return f"Error stopping email reply server: {str(e)}"

def initialize_email_reply_server(credentials):
    """Initialize the email reply server with Gmail credentials"""
    try:
        # Convert credentials to dict format for MCP server
        creds_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Here you would typically communicate with the MCP server
        # For now, we'll just start the server and it will initialize when needed
        return start_email_reply_server(credentials)
        
    except Exception as e:
        return f"Error initializing email reply server: {str(e)}"
