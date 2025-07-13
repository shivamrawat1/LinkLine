# Email Reply MCP Server

This document describes the Email Reply MCP (Model Context Protocol) server that automatically listens to Gmail and sends contextual replies based on incoming emails.

## Overview

The Email Reply MCP Server is designed to:
1. Listen to incoming emails in your Gmail account
2. Analyze email content and subject lines
3. Generate contextual auto-replies based on predefined rules
4. Send automatic responses using Gmail API

## Features

- **Contextual Replies**: Replies are generated based on keywords and context in `data/data.json`
- **Gmail API Integration**: Uses Gmail API for reading and sending emails
- **MCP Protocol**: Implements Model Context Protocol for tool-based interactions
- **Background Processing**: Continuously monitors emails in the background
- **Duplicate Prevention**: Tracks processed emails to avoid duplicate replies
- **Configurable Settings**: Easy to customize reply contexts and settings

## Files Structure

```
app/agents/
├── email_reply.py          # Main MCP server implementation
├── email_reply_server.py   # Standalone MCP server script
└── email_reply_client.py   # Client for testing the MCP server

data/
└── data.json              # Reply contexts and settings

app/routes.py              # Updated with email reply server integration
```

## Configuration

### data/data.json

The `data.json` file contains reply contexts and settings:

```json
{
  "email_contexts": [
    {
      "trigger_keywords": ["study", "research", "participate"],
      "response_template": "Thank you for your interest in our research study...",
      "subject": "Research Study Inquiry - Thank You"
    }
  ],
  "default_response": {
    "subject": "Thank You for Your Message",
    "template": "Thank you for contacting us..."
  },
  "auto_reply_settings": {
    "enabled": true,
    "check_interval_minutes": 5,
    "max_replies_per_email": 1,
    "exclude_senders": ["noreply@", "no-reply@"]
  }
}
```

## Usage

### 1. Automatic Integration

The email reply server is automatically started when you send emails through the main application:

1. Go through the normal flow: Submit study → Compose email → Send emails
2. After emails are sent successfully, the email reply server starts automatically
3. The server begins listening for incoming emails and sending auto-replies

### 2. Manual Control

You can manually control the email reply server using these endpoints:

```bash
# Check server status
GET /email-reply/status

# Start the server manually
POST /email-reply/start

# Stop the server
POST /email-reply/stop
```

### 3. Testing the MCP Server

You can test the MCP server directly:

```bash
# Run the standalone server
python app/agents/email_reply_server.py

# Test with the client
python app/agents/email_reply_client.py
```

## MCP Tools Available

The MCP server provides these tools:

- `initialize_gmail`: Initialize Gmail service with credentials
- `start_email_listener`: Start listening for incoming emails
- `stop_email_listener`: Stop the email listener
- `check_incoming_emails`: Manually check for emails
- `get_email_stats`: Get statistics about processed emails
- `reload_reply_contexts`: Reload contexts from data.json
- `test_gmail_connection`: Test Gmail API connection

## How It Works

1. **Email Monitoring**: The server checks for new emails every 5 minutes (configurable)
2. **Content Analysis**: Analyzes email subject and body for trigger keywords
3. **Context Matching**: Matches email content with predefined reply contexts
4. **Reply Generation**: Generates appropriate reply based on matched context
5. **Auto-Reply**: Sends the reply using Gmail API
6. **Tracking**: Keeps track of processed emails to avoid duplicates

## Security Features

- **Sender Exclusion**: Automatically excludes emails from noreply addresses
- **Duplicate Prevention**: Tracks processed emails to prevent spam
- **Error Handling**: Graceful error handling for API failures
- **Rate Limiting**: Built-in delays between email checks

## Customization

### Adding New Reply Contexts

Edit `data/data.json` to add new reply contexts:

```json
{
  "trigger_keywords": ["your", "keywords"],
  "response_template": "Your custom reply message",
  "subject": "Custom Subject"
}
```

### Modifying Settings

Adjust the auto-reply settings in `data/data.json`:

```json
{
  "auto_reply_settings": {
    "enabled": true,
    "check_interval_minutes": 10,  // Check every 10 minutes
    "max_replies_per_email": 1,
    "exclude_senders": ["noreply@", "no-reply@", "donotreply@"]
  }
}
```

## Troubleshooting

### Common Issues

1. **Authentication Required**: Make sure you're authenticated with Gmail API
2. **Server Not Starting**: Check if the MCP server script is executable
3. **No Replies Sent**: Verify that email content matches trigger keywords
4. **Duplicate Replies**: Check the processed emails tracking

### Debug Mode

To enable debug logging, modify the server script to include more verbose output.

## Dependencies

The email reply server requires these additional dependencies:

```
mcp==1.0.0
nest-asyncio==1.6.0
```

## API Endpoints

### Email Reply Server Management

- `GET /email-reply/status` - Get server status
- `POST /email-reply/start` - Start the server
- `POST /email-reply/stop` - Stop the server

### Integration with Main App

The email reply server is automatically integrated with the main email sending flow:

- When emails are sent via `/send-emails`, the reply server starts automatically
- The server status is included in the response
- The server continues running in the background

## Example Response

When sending emails, you'll see a response like:

```json
{
  "success": true,
  "sent_count": 5,
  "failed_count": 0,
  "errors": [],
  "message": "Successfully sent 5 emails. 0 failed.",
  "email_reply_server": "Email reply server started successfully"
}
```

This indicates that both the emails were sent and the auto-reply server is now active and listening for incoming emails. 