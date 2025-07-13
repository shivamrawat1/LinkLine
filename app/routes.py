from flask import render_template, request, jsonify, redirect, url_for, session
from app.agents.exa_agent import search_participants
from app.agents.compose_email import compose_recruitment_email
from app import app
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

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
    
    if results:
        return render_template("results.html", 
                             results=results, 
                             study_description=study_description,
                             email_draft=email_draft,
                             email_sent=email_sent)
    else:
        return redirect(url_for('home'))

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

@app.route("/send-emails", methods=["POST"])
def send_emails():
    """Send emails to all participants"""
    try:
        results = session.get('search_results')
        email_draft = session.get('email_draft')
        
        if not results or not email_draft:
            return jsonify({"error": "Missing search results or email draft"}), 400
        
        # Load email configuration
        load_dotenv()
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_address or not email_password:
            return jsonify({"error": "Email configuration not found"}), 500
        
        # Send emails to participants with valid email addresses
        sent_count = 0
        failed_count = 0
        
        for participant in results.get('participants', []):
            if participant.get('email') and participant['email'] != 'Not found':
                try:
                    # Create email message
                    msg = MIMEMultipart()
                    msg['From'] = email_address
                    msg['To'] = participant['email']
                    msg['Subject'] = "Invitation to Participate in Research Study"
                    
                    # Add body
                    msg.attach(MIMEText(email_draft, 'plain'))
                    
                    # Send email
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(email_address, email_password)
                    server.send_message(msg)
                    server.quit()
                    
                    sent_count += 1
                    
                except Exception as e:
                    print(f"Failed to send email to {participant['email']}: {e}")
                    failed_count += 1
        
        # Mark emails as sent in session
        session['email_sent'] = True
        
        return jsonify({
            "success": True,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "message": f"Successfully sent {sent_count} emails. {failed_count} failed."
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


