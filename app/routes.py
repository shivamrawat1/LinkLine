from flask import render_template, request, jsonify, redirect, url_for, session
from app.agents.exa_agent import search_participants
from app import app
import json

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
        
        # Store results in session for the results page
        session['search_results'] = results
        
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
    if results:
        # Clear the session data after retrieving it
        session.pop('search_results', None)
        return render_template("results.html", results=results)
    else:
        return redirect(url_for('home'))


