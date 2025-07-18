from flask import Blueprint, render_template, redirect, url_for, session
import datetime

main_bp = Blueprint('main', __name__)

# Server start time to track restarts
SERVER_START_TIME = datetime.datetime.now()

def check_authentication():
    """Check if user is authenticated with valid credentials"""
    credentials = session.get('credentials')
    if not credentials:
        return False, "not_authenticated"
    
    # Check if credentials are from before server restart
    if 'auth_time' in credentials:
        try:
            auth_time = datetime.datetime.fromisoformat(credentials['auth_time'])
            if auth_time < SERVER_START_TIME:
                # Credentials are from before server restart, clear them
                session.pop('credentials', None)
                return False, "server_restart"
        except (ValueError, TypeError):
            # Invalid timestamp format, clear credentials
            session.pop('credentials', None)
            return False, "invalid_format"
    else:
        # Old format credentials without timestamp, clear them
        session.pop('credentials', None)
        return False, "invalid_format"
    
    return True, None

@main_bp.route("/")
def index():
    is_authenticated, auth_reason = check_authentication()
    if is_authenticated:
        credentials = session.get("credentials")
        return render_template("index.html", user=credentials)
    else:
        return redirect(url_for("main.login"))  # redirect to login if not signed in

@main_bp.route("/login")
def login():
    is_authenticated, auth_reason = check_authentication()
    if is_authenticated:
        return redirect(url_for("main.index"))  # redirect to index if already signed in

    return render_template("login.html")

@main_bp.route("/results")
def show_results():
    """Display search results page"""
    # Check if session is still valid (not expired due to server restart)
    if 'search_time' not in session:
        # Session expired, redirect to home
        return redirect(url_for('main.index'))
    
    results = session.get('search_results', None)
    study_description = session.get('study_description', None)
    email_draft = session.get('email_draft', None)
    email_sent = session.get('email_sent', False)
    credentials = session.get('credentials', None)
    
    # Check if user is authenticated and credentials are valid
    is_authenticated = False
    auth_needed_reason = None
    
    if credentials:
        # Check if credentials are from before server restart
        if 'auth_time' in credentials:
            auth_time = datetime.datetime.fromisoformat(credentials['auth_time'])
            if auth_time < SERVER_START_TIME:
                # Credentials are from before server restart, clear them
                session.pop('credentials', None)
                auth_needed_reason = "server_restart"
            else:
                is_authenticated = True
        else:
            # Old format credentials without timestamp, clear them
            session.pop('credentials', None)
            auth_needed_reason = "invalid_format"
    
    return render_template("results.html", 
                         results=results, 
                         study_description=study_description,
                         email_draft=email_draft,
                         email_sent=email_sent,
                         is_authenticated=is_authenticated,
                         auth_needed_reason=auth_needed_reason) 