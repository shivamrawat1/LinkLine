# LinkLine - AI-Powered Participant Recruitment

LinkLine is an intelligent platform that helps researchers find potential participants for their studies using AI-powered search and analysis, with built-in email composition and sending capabilities.

## Features

- **AI-Powered Study Analysis**: Uses Google Gemini to analyze study descriptions and extract inclusion/exclusion criteria
- **Intelligent Participant Search**: Uses Exa API to search for potential participants based on processed criteria
- **Real-time Results**: Displays top 10 potential participants with contact information
- **AI Email Composition**: Uses Crew AI (Gemini) to generate professional recruitment emails based on study descriptions
- **Email Management**: Edit, save, and send emails to all participants with one click
- **Modern UI**: Clean, responsive interface with loading states and error handling

## How It Works

1. **Study Description Input**: Researchers describe their study, including purpose, methodology, and participant requirements
2. **AI Processing**: Gemini AI analyzes the description to extract:
   - Search queries for finding participants
   - Target roles and industries
   - Inclusion and exclusion criteria
3. **Intelligent Search**: Exa API searches for potential participants using the processed criteria
4. **Results Display**: Shows participants with names, emails, LinkedIn profiles, and relevant information
5. **Email Composition**: AI generates a professional recruitment email based on the study description
6. **Email Management**: Researchers can edit the email draft and send it to all participants

## Setup

### Prerequisites

- Python 3.8+
- Exa API key
- Google Gemini API key
- Email account for sending recruitment emails (Gmail recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LinkLine
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys and email configuration:
```bash
# API Keys
EXA_API_KEY=your_exa_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Email Configuration (for sending emails to participants)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password. [Learn how to create an App Password](https://support.google.com/accounts/answer/185833).

### Running the Application

1. Start the Flask application:
```bash
python run.py
```

2. Open your browser and navigate to `http://localhost:5000`

### Testing

Run the test suite to verify functionality:
```bash
python test_exa_agent.py
```

## API Endpoints

- `GET /`: Main application page
- `POST /submit`: Submit study description and search for participants
- `GET /results`: Display search results page
- `POST /compose-email`: Generate email draft using Crew AI
- `POST /save-email`: Save edited email draft
- `POST /send-emails`: Send emails to all participants

## File Structure

```
LinkLine/
├── app/
│   ├── agents/
│   │   ├── exa_agent.py          # AI processing and search logic
│   │   └── compose_email.py      # Email composition using Crew AI
│   ├── static/
│   │   └── script.js             # Frontend JavaScript
│   ├── templates/
│   │   ├── index.html            # Main application page
│   │   └── results.html          # Results display page with email functionality
│   ├── __init__.py
│   └── routes.py                 # Flask routes including email endpoints
├── requirements.txt
├── run.py
├── test_exa_agent.py
└── README.md
```

## Usage Example

1. **Enter Study Description**:
   ```
   We are conducting a study on AI adoption in healthcare. 
   We need healthcare professionals who have experience with 
   AI tools in their practice. Participants should be working 
   in hospitals or clinics and have used AI-powered diagnostic 
   tools or patient management systems.
   ```

2. **AI Processing**: The system automatically extracts:
   - Search query: "healthcare professionals AI tools diagnostic systems"
   - Target roles: ["doctors", "nurses", "healthcare administrators"]
   - Target industries: ["healthcare", "medical technology"]
   - Inclusion criteria: ["experience with AI tools", "working in hospitals/clinics"]

3. **Search Results**: The system finds and displays potential participants with:
   - Name and professional title
   - Email address (if available)
   - LinkedIn profile link
   - Relevant background information

4. **Email Composition**: Click "Compose Email" to generate a professional recruitment email using Crew AI

5. **Email Management**: 
   - Edit the generated email draft
   - Save the draft
   - Send to all participants with one click

## Email Features

- **AI-Generated Content**: Professional recruitment emails based on study descriptions
- **Editable Drafts**: Modify email content before sending
- **Bulk Sending**: Send emails to all participants simultaneously
- **Success Tracking**: Monitor email delivery status
- **Professional Templates**: Pre-formatted emails with proper structure

## Technologies Used

- **Backend**: Flask, Python
- **AI Processing**: Google Gemini API (Crew AI)
- **Search**: Exa API
- **Email**: SMTP with Gmail integration
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with modern design principles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 