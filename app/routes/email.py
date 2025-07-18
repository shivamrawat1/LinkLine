from flask import Blueprint, request, jsonify, session, url_for
from app.agents.compose_email import compose_recruitment_email
from app.gmail_service import GmailService
from .auth import get_gmail_credentials_from_session, initialize_email_reply_server

email_bp = Blueprint('email', __name__)

@email_bp.route("/compose-email", methods=["POST"])
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

@email_bp.route("/save-email", methods=["POST"])
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

@email_bp.route("/send-emails", methods=["POST"])
def send_emails():
    credentials = get_gmail_credentials_from_session()
    if not credentials:
        return jsonify({"auth_required": True, "auth_url": url_for('auth.start_auth', _external=True)}), 401
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