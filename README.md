# LinkLine - AI-Powered Participant Recruitment

LinkLine is an intelligent platform that helps researchers find potential participants for their studies using AI-powered search and analysis.

## Features

- **AI-Powered Study Analysis**: Uses Google Gemini to analyze study descriptions and extract inclusion/exclusion criteria
- **Intelligent Participant Search**: Uses Exa API to search for potential participants based on processed criteria
- **Real-time Results**: Displays top 10 potential participants with contact information
- **Modern UI**: Clean, responsive interface with loading states and error handling

## How It Works

1. **Study Description Input**: Researchers describe their study, including purpose, methodology, and participant requirements
2. **AI Processing**: Gemini AI analyzes the description to extract:
   - Search queries for finding participants
   - Target roles and industries
   - Inclusion and exclusion criteria
3. **Intelligent Search**: Exa API searches for potential participants using the processed criteria
4. **Results Display**: Shows participants with names, emails, LinkedIn profiles, and relevant information

## Setup

### Prerequisites

- Python 3.8+
- Exa API key
- Google Gemini API key

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

4. Create a `.env` file with your API keys:
```bash
EXA_API_KEY=your_exa_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

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

## File Structure

```
LinkLine/
├── app/
│   ├── agents/
│   │   └── exa_agent.py          # AI processing and search logic
│   ├── static/
│   │   └── script.js             # Frontend JavaScript
│   ├── templates/
│   │   ├── index.html            # Main application page
│   │   └── results.html          # Results display page
│   ├── __init__.py
│   └── routes.py                 # Flask routes
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

## Technologies Used

- **Backend**: Flask, Python
- **AI Processing**: Google Gemini API
- **Search**: Exa API
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