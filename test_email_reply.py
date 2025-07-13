#!/usr/bin/env python3
"""
Test script for the Email Reply MCP Server
"""

import asyncio
import json
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_data_json():
    """Test that data.json exists and is valid"""
    try:
        with open('data/data.json', 'r') as f:
            data = json.load(f)
        print("✓ data.json is valid JSON")
        print(f"✓ Found {len(data.get('email_contexts', []))} email contexts")
        print(f"✓ Auto-reply enabled: {data.get('auto_reply_settings', {}).get('enabled', False)}")
        return True
    except FileNotFoundError:
        print("✗ data.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ data.json is not valid JSON: {e}")
        return False

async def test_mcp_server():
    """Test the MCP server connection"""
    try:
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=["app/agents/email_reply_server.py"],
        )
        
        # Connect to the server
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                
                # List available tools
                tools_result = await session.list_tools()
                print(f"✓ Connected to MCP server with {len(tools_result.tools)} tools:")
                
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test getting stats
                stats_result = await session.call_tool("get_email_stats", arguments={})
                print(f"✓ Server stats: {stats_result.content[0].text}")
                
                return True
                
    except Exception as e:
        print(f"✗ Failed to connect to MCP server: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import mcp
        print("✓ MCP module imported successfully")
        
        from mcp.server.fastmcp import FastMCP
        print("✓ FastMCP imported successfully")
        
        from googleapiclient.discovery import build
        print("✓ Google API client imported successfully")
        
        from google.oauth2.credentials import Credentials
        print("✓ Google OAuth2 imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        'app/agents/email_reply.py',
        'app/agents/email_reply_server.py',
        'app/agents/email_reply_client.py',
        'data/data.json',
        'app/routes.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

async def main():
    """Run all tests"""
    print("Testing Email Reply MCP Server Setup")
    print("=" * 40)
    
    # Test file structure
    print("\n1. Testing file structure:")
    file_ok = test_file_structure()
    
    # Test imports
    print("\n2. Testing imports:")
    import_ok = test_imports()
    
    # Test data.json
    print("\n3. Testing data.json:")
    data_ok = test_data_json()
    
    # Test MCP server
    print("\n4. Testing MCP server connection:")
    server_ok = await test_mcp_server()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"File structure: {'✓' if file_ok else '✗'}")
    print(f"Imports: {'✓' if import_ok else '✗'}")
    print(f"Data configuration: {'✓' if data_ok else '✗'}")
    print(f"MCP server: {'✓' if server_ok else '✗'}")
    
    if all([file_ok, import_ok, data_ok, server_ok]):
        print("\n🎉 All tests passed! Email Reply MCP Server is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    asyncio.run(main()) 