import asyncio
import json
import os
import time
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

class EmailReplyMCP:
    """MCP Server for automatic email replies using Gmail API"""
    
    def __init__(self, credentials: Credentials, data_file: str = "data/data.json"):
        """Initialize the email reply MCP server
        
        Args:
            credentials: Gmail API credentials
            data_file: Path to the data.json file with reply contexts
        """
        self.credentials = credentials
        self.data_file = data_file
        self.gmail_service = build('gmail', 'v1', credentials=credentials)
        self.reply_contexts = self._load_reply_contexts()
        self.processed_emails = set()  # Track processed emails to avoid duplicates
        self.is_listening = False
        self.listen_thread = None
        
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
        def start_email_listener() -> str:
            """Start listening for incoming emails and auto-reply"""
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
                "auto_reply_enabled": self.reply_contexts.get("auto_reply_settings", {}).get("enabled", False)
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


# Client code for testing and integration
class EmailReplyClient:
    """Client for interacting with the Email Reply MCP server"""
    
    def __init__(self, server_script_path: str = "app/agents/email_reply.py"):
        self.server_script_path = server_script_path
        self.session = None
        self.stdio = None
        self.write = None
    
    async def connect_to_server(self, credentials: Credentials):
        """Connect to the email reply MCP server"""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
        )
        
        # Connect to the server
        stdio_transport = await stdio_client(server_params)
        self.stdio, self.write = stdio_transport
        self.session = await ClientSession(self.stdio, self.write)
        
        # Initialize the connection
        await self.session.initialize()
        
        # List available tools
        tools_result = await self.session.list_tools()
        print("\nConnected to Email Reply MCP server with tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
    
    async def start_listener(self) -> str:
        """Start the email listener"""
        result = await self.session.call_tool("start_email_listener", arguments={})
        return result.content[0].text
    
    async def stop_listener(self) -> str:
        """Stop the email listener"""
        result = await self.session.call_tool("stop_email_listener", arguments={})
        return result.content[0].text
    
    async def check_emails(self) -> str:
        """Manually check for emails"""
        result = await self.session.call_tool("check_incoming_emails", arguments={})
        return result.content[0].text
    
    async def get_stats(self) -> str:
        """Get email statistics"""
        result = await self.session.call_tool("get_email_stats", arguments={})
        return result.content[0].text


# Example usage and testing
if __name__ == "__main__":
    # This would be used when running the server directly
    # In practice, the server will be started by the main application
    print("Email Reply MCP Server")
    print("This server should be started by the main application with proper credentials")
