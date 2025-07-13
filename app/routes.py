from flask import render_template, request, jsonify, redirect, url_for, session
from app.agents.exa_agent import search_participants
from app.agents.compose_email import compose_recruitment_email
from app.gmail_service import GmailService
from app import app
import os
import sys
import asyncio
import subprocess
import threading
import time
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Global variable to track email reply server process
email_reply_server_process = None
email_reply_server_active = False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_study():
    """Handle study submission and start search"""
    try:
        description = request.form.get('description')
        if not description:
            return jsonify({"error": "Study description is required"}), 400
        
        # Start the search process
        results = search_participants(description)
        
        # Store results and study description in session for the results page
        session['search_results'] = results
        session['study_description'] = description
        
        return jsonify({
            "success": True,
            "redirect": "/results"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/results")
def show_results():
    """Display search results page"""
    results = session.get('search_results', None)
    study_description = session.get('study_description', None)
    email_draft = session.get('email_draft', None)
    email_sent = session.get('email_sent', False)
    # Always render with these variables for the new flow
    return render_template("results.html", 
                         results=results, 
                         study_description=study_description,
                         email_draft=email_draft,
                         email_sent=email_sent)

@app.route("/compose-email", methods=["POST"])
def compose_email():
    """Generate email draft using Crew AI"""
    try:
        study_description = session.get('study_description')
        if not study_description:
            return jsonify({"error": "Study description not found"}), 400
        
        # Generate email draft using Crew AI
        email_content = compose_recruitment_email(study_description)
        
        # Store email draft in session
        session['email_draft'] = email_content
        
        return jsonify({
            "success": True,
            "email_content": email_content
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-email", methods=["POST"])
def save_email():
    """Save the edited email draft"""
    try:
        email_content = request.json.get('email_content')
        if not email_content:
            return jsonify({"error": "Email content is required"}), 400
        
        # Store the edited email draft in session
        session['email_draft'] = email_content
        
        return jsonify({
            "success": True,
            "message": "Email draft saved successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/start-auth", methods=["GET", "POST"])
def start_auth():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    print(auth_url)
    session['state'] = state
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Store as dict, not pickled object
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return "authenticated is complete"

def get_gmail_credentials_from_session():
    creds_dict = session.get('credentials')
    if not creds_dict:
        return None
    return Credentials(
        creds_dict['token'],
        refresh_token=creds_dict.get('refresh_token'),
        token_uri=creds_dict['token_uri'],
        client_id=creds_dict['client_id'],
        client_secret=creds_dict['client_secret'],
        scopes=creds_dict['scopes']
    )

def start_email_reply_server(credentials):
    """Start the email reply MCP server in a separate process"""
    global email_reply_server_process, email_reply_server_active
    
    if email_reply_server_active:
        return "Email reply server is already running"
    
    try:
        # Start the MCP server process
        server_script = os.path.join(os.path.dirname(__file__), "agents", "email_reply_server.py")
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

@app.route("/send-emails", methods=["POST"])
def send_emails():
    credentials = get_gmail_credentials_from_session()
    if not credentials:
        return jsonify({"auth_required": True, "auth_url": url_for('start_auth', _external=True)}), 401
    results = session.get('search_results')
    email_draft = session.get('email_draft')
    if not results or not email_draft:
        return jsonify({"error": "Missing search results or email draft"}), 400
    # Extract subject line from email draft (first line after "Subject:")
    lines = email_draft.split('\n')
    subject = "Invitation to Participate in Research Study"  # Default subject
    for i, line in enumerate(lines):
        if line.strip().startswith('Subject:'):
            subject = line.strip().replace('Subject:', '').strip()
            # Remove subject line from body
            email_body = '\n'.join(lines[:i] + lines[i+1:])
            break
    else:
        # If no subject line found, use the entire draft as body
        email_body = email_draft
    # Send emails to participants with valid email addresses using GmailService
    participants = results.get('participants', [])
    try:
        send_results = GmailService.send_bulk_emails_with_credentials(credentials, participants, subject, email_body)
        session['email_sent'] = True
        
        # Start email reply server after successfully sending emails
        email_reply_status = initialize_email_reply_server(credentials)
        
        return jsonify({
            "success": True,
            "sent_count": send_results['sent_count'],
            "failed_count": send_results['failed_count'],
            "errors": send_results['errors'],
            "message": f"Successfully sent {send_results['sent_count']} emails. {send_results['failed_count']} failed.",
            "email_reply_server": email_reply_status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/email-reply/status", methods=["GET"])
def get_email_reply_status():
    """Get the status of the email reply server"""
    global email_reply_server_active, email_reply_server_process
    
    status = {
        "active": email_reply_server_active,
        "process_running": email_reply_server_process is not None and email_reply_server_process.poll() is None if email_reply_server_process else False
    }
    
    return jsonify(status)

@app.route("/email-reply/start", methods=["POST"])
def start_email_reply():
    """Manually start the email reply server"""
    credentials = get_gmail_credentials_from_session()
    if not credentials:
        return jsonify({"error": "Authentication required"}), 401
    
    status = initialize_email_reply_server(credentials)
    return jsonify({"message": status})

@app.route("/email-reply/stop", methods=["POST"])
def stop_email_reply():
    """Manually stop the email reply server"""
    status = stop_email_reply_server()
    return jsonify({"message": status})


