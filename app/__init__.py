from flask import Flask

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session support

from app import routes
