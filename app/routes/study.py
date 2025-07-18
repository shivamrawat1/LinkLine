from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.agents.exa_agent import search_participants
import datetime

study_bp = Blueprint('study', __name__)

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

@study_bp.route("/submit", methods=["POST"])
def submit_study():
    """Handle study submission and start search"""
    # Check authentication first
    is_authenticated, auth_reason = check_authentication()
    if not is_authenticated:
        return jsonify({
            "error": "Authentication required",
            "auth_required": True,
            "auth_reason": auth_reason
        }), 401
    
    try:
        description = request.form.get('description')
        if not description:
            return jsonify({"error": "Study description is required"}), 400
        
        # Start the search process
        results = search_participants(description)
        
        # Store results and study description in session for the results page
        session['search_results'] = results
        session['study_description'] = description
        session['search_time'] = datetime.datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "redirect": "/results"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 