#!/usr/bin/env python3
"""
Client for testing the Email Reply MCP Server
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any
from google.oauth2.credentials import Credentials
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class EmailReplyMCPClient:
    """Client for interacting with the Email Reply MCP server"""
    
    def __init__(self, server_script_path: str = "app/agents/email_reply_server.py"):
        self.server_script_path = server_script_path
        self.session = None
        self.stdio = None
        self.write = None
    
    async def connect_to_server(self):
        """Connect to the email reply MCP server"""
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
    
    async def initialize_gmail(self, credentials: Credentials) -> str:
        """Initialize Gmail service with credentials"""
        creds_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        result = await self.session.call_tool("initialize_gmail", arguments={"credentials_dict": creds_dict})
        return result.content[0].text
    
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
    
    async def test_connection(self) -> str:
        """Test Gmail connection"""
        result = await self.session.call_tool("test_gmail_connection", arguments={})
        return result.content[0].text
    
    async def reload_contexts(self) -> str:
        """Reload reply contexts"""
        result = await self.session.call_tool("reload_reply_contexts", arguments={})
        return result.content[0].text


async def main():
    """Main function for testing the email reply MCP server"""
    client = EmailReplyMCPClient()
    
    try:
        # Connect to the server
        await client.connect_to_server()
        
        # Test the connection
        print("\nTesting Gmail connection...")
        connection_result = await client.test_connection()
        print(f"Connection result: {connection_result}")
        
        # Get initial stats
        print("\nGetting initial stats...")
        stats = await client.get_stats()
        print(f"Stats: {stats}")
        
        # Test reloading contexts
        print("\nReloading reply contexts...")
        reload_result = await client.reload_contexts()
        print(f"Reload result: {reload_result}")
        
        # Test manual email check
        print("\nChecking for incoming emails...")
        check_result = await client.check_emails()
        print(f"Check result: {check_result}")
        
        # Get updated stats
        print("\nGetting updated stats...")
        updated_stats = await client.get_stats()
        print(f"Updated stats: {updated_stats}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client.session:
            await client.session.close()


if __name__ == "__main__":
    asyncio.run(main()) 