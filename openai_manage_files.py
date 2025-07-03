#!/usr/bin/env python3
"""
OpenAI File Management Script

This script provides functionality to list and delete files from OpenAI's API.
Supports both listing all files and deleting specific files by ID.

Usage:
    python openai_manage_files.py --list                    # List all files
    python openai_manage_files.py --delete <file_id>        # Delete specific file
    python openai_manage_files.py --help                    # Show help
"""

import os
import sys
import subprocess


def display_help():
    """Display usage information and help."""
    print(__doc__)
    print("\nExamples:")
    print("  python openai_manage_files.py --list")
    print("  python openai_manage_files.py --delete file-abc123")
    print("  python openai_manage_files.py --help")


def check_openai_api_key() -> bool:
    """Check if OpenAI API key is set in environment."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    return True


def list_files() -> None:
    """List all files in OpenAI API using openai CLI command."""
    try:
        print("Fetching files from OpenAI API...")
        result = subprocess.run(
            ['openai', 'api', 'files.list'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output to check if there are any files
        output = result.stdout.strip()
        
        if not output or output == "[]":
            print("No files found in OpenAI API")
            return
        
        # Try to parse as JSON to format nicely
        try:
            import json
            data = json.loads(output)
            
            # Handle single file object
            if isinstance(data, dict) and data.get("object") == "file":
                files = [data]
            # Handle array of files
            elif isinstance(data, list):
                files = data
            # Handle response with data field
            elif isinstance(data, dict) and "data" in data:
                files = data["data"]
            else:
                files = [data]
            
            if not files:
                print("No files found in OpenAI API")
                return
            
            print(f"Found {len(files)} file(s) in OpenAI API:")
            print()
            
            for file in files:
                if isinstance(file, dict) and file.get("object") == "file":
                    file_id = file.get("id", "Unknown")
                    filename = file.get("filename", "Unknown")
                    bytes_size = file.get("bytes", 0)
                    status = file.get("status", "Unknown")
                    purpose = file.get("purpose", "Unknown")
                    created_at = file.get("created_at", 0)
                    
                    # Convert bytes to MB
                    size_mb = bytes_size / (1024 * 1024)
                    
                    # Convert timestamp to readable date
                    from datetime import datetime
                    created_date = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S") if created_at else "Unknown"
                    
                    print(f"File: {filename}")
                    print(f"   ID: {file_id}")
                    print(f"   Size: {size_mb:.2f} MB ({bytes_size:,} bytes)")
                    print(f"   Status: {status}")
                    print(f"   Purpose: {purpose}")
                    print(f"   Created: {created_date}")
                    print()
                else:
                    print(f"File: {file}")
                    print()
            
        except json.JSONDecodeError:
            # Fallback to raw output if JSON parsing fails
            print("Files in OpenAI API:")
            print(output)
        
    except subprocess.CalledProcessError as e:
        print(f"Error listing files: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'openai' CLI command not found")
        print("Please install OpenAI CLI: pip install openai")
        sys.exit(1)


def delete_file(file_id: str) -> None:
    """Delete a specific file from OpenAI API."""
    try:
        from openai import OpenAI
        
        client = OpenAI()
        
        print(f"Deleting file: {file_id}")
        response = client.files.delete(file_id)
        
        if response.deleted:
            print(f"File deleted successfully: {file_id}")
            print(f"Response: {response}")
        else:
            print(f"Failed to delete file: {file_id}")
            sys.exit(1)
            
    except ImportError:
        print("Error: OpenAI Python SDK not installed")
        print("Please install: pip install openai")
        sys.exit(1)
    except Exception as e:
        print(f"Error deleting file: {e}")
        sys.exit(1)


def main():
    """Main function to handle CLI arguments and execute operations."""
    # Handle help cases first
    if len(sys.argv) == 1 or '--help' in sys.argv:
        display_help()
        return
    
    # Handle list operation
    if '--list' in sys.argv:
        if not check_openai_api_key():
            sys.exit(1)
        list_files()
        return
    
    # Handle delete operation
    if '--delete' in sys.argv:
        try:
            delete_index = sys.argv.index('--delete')
            if delete_index + 1 >= len(sys.argv):
                print("Error: No file ID provided for --delete")
                print("Usage: python openai_manage_files.py --delete <file_id>")
                sys.exit(1)
            
            file_id = sys.argv[delete_index + 1]
            if not check_openai_api_key():
                sys.exit(1)
            delete_file(file_id)
            return
        except ValueError:
            print("Error: Invalid --delete usage")
            print("Usage: python openai_manage_files.py --delete <file_id>")
            sys.exit(1)
    
    # If we get here, no valid operation was specified
    print("Error: No valid operation specified")
    print("Use --list to list files or --delete <file_id> to delete a file")
    print("Use --help for more information")
    sys.exit(1)


if __name__ == "__main__":
    main() 