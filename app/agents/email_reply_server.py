#!/usr/bin/env python3
"""
Standalone MCP Server for Email Auto-Replies
This server listens to Gmail and automatically replies based on context in data.json
"""

import asyncio
import json
import os
import sys
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import threading
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

load_dotenv()

class EmailReplyMCPServer:
    """Standalone MCP Server for automatic email replies using Gmail API"""
    
    def __init__(self, data_file: str = "data/data.json"):
        """Initialize the email reply MCP server
        
        Args:
            data_file: Path to the data.json file with reply contexts
        """
        self.data_file = data_file
        self.reply_contexts = self._load_reply_contexts()
        self.processed_emails = set()  # Track processed emails to avoid duplicates
        self.is_listening = False
        self.listen_thread = None
        self.credentials = None
        self.gmail_service = None
        
        # Create MCP server
        self.mcp = FastMCP(
            name="EmailReplyServer",
            host="0.0.0.0",
            port=8051,
            stateless_http=True,
        )
        
        # Register MCP tools
        self._register_tools()
    
    def _load_reply_contexts(self) -> Dict[str, Any]:
        """Load reply contexts from data.json file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.data_file} not found. Using default contexts.")
            return {
                "email_contexts": [],
                "default_response": {
                    "subject": "Thank You for Your Message",
                    "template": "Thank you for contacting us. We have received your message and will respond within 24-48 hours."
                },
                "auto_reply_settings": {
                    "enabled": True,
                    "check_interval_minutes": 5,
                    "max_replies_per_email": 1,
                    "exclude_senders": ["noreply@", "no-reply@", "donotreply@"]
                }
            }
    
    def _register_tools(self):
        """Register MCP tools for email operations"""
        
        @self.mcp.tool()
        def initialize_gmail(credentials_dict: Dict[str, Any]) -> str:
            """Initialize Gmail service with credentials
            
            Args:
                credentials_dict: Dictionary containing Gmail API credentials
            """
            try:
                self.credentials = Credentials(
                    credentials_dict['token'],
                    refresh_token=credentials_dict.get('refresh_token'),
                    token_uri=credentials_dict['token_uri'],
                    client_id=credentials_dict['client_id'],
                    client_secret=credentials_dict['client_secret'],
                    scopes=credentials_dict['scopes']
                )
                self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
                return "Gmail service initialized successfully"
            except Exception as e:
                return f"Error initializing Gmail service: {str(e)}"
        
        @self.mcp.tool()
        def start_email_listener() -> str:
            """Start listening for incoming emails and auto-reply"""
            if not self.gmail_service:
                return "Gmail service not initialized. Call initialize_gmail first."
            
            if self.is_listening:
                return "Email listener is already running"
            
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_for_emails, daemon=True)
            self.listen_thread.start()
            return "Email listener started successfully"
        
        @self.mcp.tool()
        def stop_email_listener() -> str:
            """Stop listening for incoming emails"""
            if not self.is_listening:
                return "Email listener is not running"
            
            self.is_listening = False
            if self.listen_thread:
                self.listen_thread.join(timeout=5)
            return "Email listener stopped successfully"
        
        @self.mcp.tool()
        def check_incoming_emails() -> str:
            """Manually check for incoming emails and send auto-replies"""
            if not self.gmail_service:
                return "Gmail service not initialized. Call initialize_gmail first."
            
            try:
                emails_processed = self._process_incoming_emails()
                return f"Processed {emails_processed} new emails"
            except Exception as e:
                return f"Error processing emails: {str(e)}"
        
        @self.mcp.tool()
        def get_email_stats() -> str:
            """Get statistics about processed emails"""
            stats = {
                "processed_emails_count": len(self.processed_emails),
                "is_listening": self.is_listening,
                "reply_contexts_count": len(self.reply_contexts.get("email_contexts", [])),
                "auto_reply_enabled": self.reply_contexts.get("auto_reply_settings", {}).get("enabled", False),
                "gmail_initialized": self.gmail_service is not None
            }
            return json.dumps(stats, indent=2)
        
        @self.mcp.tool()
        def reload_reply_contexts() -> str:
            """Reload reply contexts from data.json file"""
            try:
                self.reply_contexts = self._load_reply_contexts()
                return "Reply contexts reloaded successfully"
            except Exception as e:
                return f"Error reloading contexts: {str(e)}"
        
        @self.mcp.tool()
        def test_gmail_connection() -> str:
            """Test Gmail API connection"""
            if not self.gmail_service:
                return "Gmail service not initialized"
            
            try:
                # Try to get user profile
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                return f"Gmail connection successful. Email: {profile.get('emailAddress', 'Unknown')}"
            except Exception as e:
                return f"Gmail connection failed: {str(e)}"
    
    def _should_exclude_sender(self, sender: str) -> bool:
        """Check if sender should be excluded from auto-replies"""
        exclude_patterns = self.reply_contexts.get("auto_reply_settings", {}).get("exclude_senders", [])
        sender_lower = sender.lower()
        return any(pattern in sender_lower for pattern in exclude_patterns)
    
    def _find_matching_context(self, email_content: str, subject: str) -> Optional[Dict[str, Any]]:
        """Find matching reply context based on email content and subject"""
        content_lower = (email_content + " " + subject).lower()
        
        for context in self.reply_contexts.get("email_contexts", []):
            keywords = context.get("trigger_keywords", [])
            if any(keyword.lower() in content_lower for keyword in keywords):
                return context
        
        return None
    
    def _generate_reply(self, email_content: str, subject: str, sender: str) -> Optional[Dict[str, str]]:
        """Generate auto-reply based on email content"""
        # Check if sender should be excluded
        if self._should_exclude_sender(sender):
            return None
        
        # Find matching context
        context = self._find_matching_context(email_content, subject)
        
        if context:
            return {
                "subject": context["subject"],
                "body": context["response_template"]
            }
        else:
            # Use default response
            default = self.reply_contexts.get("default_response", {})
            return {
                "subject": default.get("subject", "Thank You for Your Message"),
                "body": default.get("template", "Thank you for contacting us. We will respond within 24-48 hours.")
            }
    
    def _send_reply(self, thread_id: str, reply_subject: str, reply_body: str, original_sender: str) -> bool:
        """Send reply to email thread"""
        try:
            # Create reply message
            message = MIMEMultipart()
            message['to'] = original_sender
            message['subject'] = reply_subject
            message['in-reply-to'] = thread_id
            message['references'] = thread_id
            
            # Add body
            text_part = MIMEText(reply_body, 'plain')
            message.attach(text_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send reply
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Auto-reply sent to {original_sender} for thread {thread_id}")
            return True
            
        except HttpError as error:
            print(f"Error sending auto-reply: {error}")
            return False
        except Exception as e:
            print(f"Unexpected error sending auto-reply: {e}")
            return False
    
    def _get_email_content(self, message_data: Dict[str, Any]) -> tuple:
        """Extract email content, subject, and sender from message data"""
        headers = message_data.get('payload', {}).get('headers', [])
        
        subject = ""
        sender = ""
        
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                sender = header['value']
        
        # Extract email body
        body = ""
        payload = message_data.get('payload', {})
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body, subject, sender
    
    def _process_incoming_emails(self) -> int:
        """Process incoming emails and send auto-replies"""
        try:
            # Get recent messages (last 24 hours)
            query = "is:inbox newer_than:1d"
            results = self.gmail_service.users().messages().list(
                userId='me', q=query
            ).execute()
            
            messages = results.get('messages', [])
            processed_count = 0
            
            for message in messages:
                message_id = message['id']
                
                # Skip if already processed
                if message_id in self.processed_emails:
                    continue
                
                # Get full message details
                message_data = self.gmail_service.users().messages().get(
                    userId='me', id=message_id
                ).execute()
                
                # Extract email content
                body, subject, sender = self._get_email_content(message_data)
                
                # Generate reply
                reply = self._generate_reply(body, subject, sender)
                
                if reply:
                    # Send auto-reply
                    success = self._send_reply(
                        message_data['threadId'],
                        reply['subject'],
                        reply['body'],
                        sender
                    )
                    
                    if success:
                        self.processed_emails.add(message_id)
                        processed_count += 1
            
            return processed_count
            
        except Exception as e:
            print(f"Error processing incoming emails: {e}")
            return 0
    
    def _listen_for_emails(self):
        """Background thread to continuously listen for emails"""
        check_interval = self.reply_contexts.get("auto_reply_settings", {}).get("check_interval_minutes", 5)
        
        while self.is_listening:
            try:
                self._process_incoming_emails()
                time.sleep(check_interval * 60)  # Convert minutes to seconds
            except Exception as e:
                print(f"Error in email listener: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def run(self, transport: str = "stdio"):
        """Run the MCP server"""
        print(f"Starting Email Reply MCP server with {transport} transport")
        self.mcp.run(transport=transport)


if __name__ == "__main__":
    # Create and run the MCP server
    server = EmailReplyMCPServer()
    server.run(transport="stdio") 