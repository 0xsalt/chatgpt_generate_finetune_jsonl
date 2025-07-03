#!/usr/bin/env python3
"""
Generate Fine-tuning JSONL

A lightweight Python script to extract user messages from OpenAI conversation exports
and format them for AI model fine-tuning in JSONL format.

Usage:
    python generate_finetune_jsonl.py input.json output.jsonl
    python generate_finetune_jsonl.py --help
"""

import json
import sys
import argparse
import os
import tiktoken


def display_usage_help():
    """Display comprehensive usage instructions."""
    help_text = """
Generate Fine-tuning JSONL
==========================

Extract user messages from OpenAI conversation exports for fine-tuning.

USAGE:
    python generate_finetune_jsonl.py <input_file> <output_file>
    python generate_finetune_jsonl.py --help

OPTIONS:
    --max-tokens <number>     Maximum tokens per completion (default: 2048)
    --no-remove-duplicates    Disable duplicate removal (default: enabled)

ARGUMENTS:
    input_file    Path to your conversations.json file from OpenAI export
    output_file   Path for the output JSONL file (will be created/overwritten)

EXAMPLES:
    python generate_finetune_jsonl.py conversations.json output.jsonl

OUTPUT FORMAT:
    Each line in the output file will be a JSON object with:
    {
        "messages": [
            { "role": "user", "content": "Write a blog post in my voice." },
            { "role": "assistant", "content": " Your extracted user message\\n" }
        ]
    }
    
    The output is OpenAI-compliant for GPT-3.5-turbo fine-tuning with:
    - Chat format with user/assistant messages
    - Token limit enforcement (default: 2048 tokens)
    - Duplicate removal (enabled by default)
    - Empty entry filtering
    - Proper newline handling
    - Leading whitespace in assistant content for better tokenization

REQUIREMENTS:
    - Python 3.x
    - Valid conversations.json file from OpenAI export
    - tiktoken library for token counting (install with: pip install tiktoken)

ERROR HANDLING:
    - Clear error messages for missing files
    - Graceful handling of malformed JSON
    - Warnings for skipped malformed conversations
    - Permission error handling for output files
"""
    print(help_text)


def load_conversations(file_path):
    """Load and parse conversations from JSON file with error handling."""
    try:
        with open(file_path, "r") as infile:
            conversations = json.load(infile)
        return conversations
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        print("Please check the file path and try again.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{file_path}'.")
        print(f"JSON Error: {e}")
        print("Please ensure the file contains valid JSON data.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error reading '{file_path}': {e}")
        sys.exit(1)


def extract_user_messages(conversations_data, errors_file_path=None):
    """Extract user messages from conversations with defensive error handling and error logging."""
    all_user_messages = []
    skipped_conversations = 0
    error_entries = []
    
    for i, convo in enumerate(conversations_data):
        try:
            mapping = convo.get("mapping", {})
            if not mapping:
                warning = f"Warning: Conversation {i} has no mapping, skipping..."
                print(warning)
                error_entries.append({
                    "type": "missing_mapping",
                    "conversation_index": i,
                    "conversation": convo,
                    "warning": warning
                })
                skipped_conversations += 1
                continue
            
            conversation_messages = []
            for node_id, node in mapping.items():
                message = node.get("message")
                if not message:
                    continue
                author = message.get("author", {})
                if author.get("role") != "user":
                    continue
                content = message.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, str):
                        if part.strip():
                            conversation_messages.append(part.strip())
                    elif isinstance(part, dict):
                        # Handle audio transcriptions
                        if part.get("content_type") == "audio_transcription":
                            text = part.get("text", "").strip()
                            if text:
                                conversation_messages.append(text)
                        # Skip other non-text content (images, audio files, etc.)
                        else:
                            content_type = part.get("content_type", "unknown")
                            error_entries.append({
                                "type": "non_text_content",
                                "conversation_index": i,
                                "node_id": node_id,
                                "content_type": content_type,
                                "part": part,
                                "warning": f"Warning: Conversation {i}, node {node_id} - skipping non-text content: {content_type}"
                            })
                    else:
                        warning = f"Warning: Conversation {i}, node {node_id} - part is not a string or dict, skipping."
                        print(warning)
                        error_entries.append({
                            "type": "non_string_part",
                            "conversation_index": i,
                            "node_id": node_id,
                            "part": part,
                            "warning": warning
                        })
            all_user_messages.extend(conversation_messages)
        except Exception as e:
            warning = f"Warning: Error processing conversation {i}, skipping... Error: {e}"
            print(warning)
            error_entries.append({
                "type": "exception",
                "conversation_index": i,
                "conversation": convo,
                "error": str(e),
                "warning": warning
            })
            skipped_conversations += 1
            continue
    if skipped_conversations > 0:
        print(f"Warning: Skipped {skipped_conversations} malformed conversations")
    print(f"Successfully extracted {len(all_user_messages)} user messages")
    # Write errors to file if requested
    if errors_file_path and error_entries:
        try:
            with open(errors_file_path, "w", encoding="utf-8") as ef:
                for entry in error_entries:
                    ef.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"Warnings for non-exporting of non-text content written to {errors_file_path}")
        except Exception as e:
            print(f"Error: Could not write errors to {errors_file_path}: {e}")
    return all_user_messages


def format_to_jsonl(messages, max_tokens=2048, remove_duplicates_flag=True):
    """Format user messages into OpenAI-compliant JSONL lines for fine-tuning."""
    jsonl_lines = []
    processed_count = 0
    truncated_count = 0
    
    # Apply token limits and truncation
    token_limited_messages = []
    for msg in messages:
        if count_tokens(msg) > max_tokens:
            truncated_msg = truncate_to_tokens(msg, max_tokens)
            token_limited_messages.append(truncated_msg)
            truncated_count += 1
        else:
            token_limited_messages.append(msg)
    
    if truncated_count > 0:
        print(f"Truncated {truncated_count} messages to fit {max_tokens} token limit")
    
    # Remove duplicates if requested
    if remove_duplicates_flag:
        token_limited_messages = remove_duplicates(token_limited_messages)
    
    # Filter empty entries
    token_limited_messages = filter_empty_entries(token_limited_messages)
    
    # Format to OpenAI-compliant JSONL (chat format for GPT-3.5-turbo fine-tuning)
    for msg in token_limited_messages:
        # Ensure proper newline handling and add leading whitespace for better tokenization
        assistant_content = " " + msg.rstrip() + "\n"
        
        json_line = {
            "messages": [
                { "role": "user", "content": "Write a blog post in my voice." },
                { "role": "assistant", "content": assistant_content }
            ]
        }
        jsonl_lines.append(json.dumps(json_line, ensure_ascii=False))
        processed_count += 1
    
    print(f"Processed {processed_count} messages into OpenAI-compliant JSONL format")
    return jsonl_lines


def count_tokens(text):
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Warning: Could not count tokens for text: {e}")
        return len(text) // 4  # Rough estimate


def truncate_to_tokens(text, max_tokens):
    """Truncate text to fit within token limit."""
    if count_tokens(text) <= max_tokens:
        return text
    
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        truncated_tokens = tokens[:max_tokens]
        return encoding.decode(truncated_tokens)
    except Exception as e:
        print(f"Warning: Could not truncate text properly: {e}")
        # Fallback: truncate by characters (rough estimate)
        return text[:max_tokens * 4]


def remove_duplicates(messages):
    """Remove duplicate messages using set tracking."""
    seen = set()
    unique_messages = []
    duplicates_removed = 0
    
    for msg in messages:
        if msg not in seen:
            seen.add(msg)
            unique_messages.append(msg)
        else:
            duplicates_removed += 1
    
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate messages")
    
    return unique_messages


def filter_empty_entries(messages):
    """Filter out empty or whitespace-only messages."""
    original_count = len(messages)
    filtered_messages = [msg for msg in messages if msg.strip()]
    removed_count = original_count - len(filtered_messages)
    
    if removed_count > 0:
        print(f"Removed {removed_count} empty or whitespace-only messages")
    
    return filtered_messages


def write_jsonl_output(output_file_path, jsonl_lines):
    """Write JSONL lines to the output file with error handling."""
    try:
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            for line in jsonl_lines:
                outfile.write(line + "\n")
        print(f"Successfully wrote {len(jsonl_lines)} lines to {output_file_path}")
    except (IOError, PermissionError) as e:
        print(f"Error: Could not write to output file '{output_file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error writing to '{output_file_path}': {e}")
        sys.exit(1)


def main():
    """Main function for argument parsing and orchestration."""
    # Version handling
    if "--version" in sys.argv:
        try:
            version_file = os.path.join(os.path.dirname(__file__), ".version")
            with open(version_file, "r") as f:
                print(f.read().strip())
        except FileNotFoundError:
            print("1.0.0")
        sys.exit(0)
    
    # Help handling - use custom help for better user experience
    if "--help" in sys.argv or len(sys.argv) == 1:
        display_usage_help()
        sys.exit(0)
    
    parser = argparse.ArgumentParser(
        description="Generate fine-tuning JSONL from OpenAI conversation exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s conversations.json output.jsonl
  %(prog)s sample.json my_finetune_data.jsonl
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to conversations.json file from OpenAI export'
    )
    parser.add_argument(
        'output_file',
        help='Path for output JSONL file'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=2048,
        help='Maximum tokens per completion (default: 2048)'
    )
    parser.add_argument(
        '--no-remove-duplicates',
        action='store_true',
        help='Disable duplicate removal (default: enabled)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.1.0',
        help='show version and exit'
    )

    
    # Parse arguments
    args = parser.parse_args()
    
    # Load conversations with error handling
    print(f"Loading conversations from: {args.input_file}")
    conversations = load_conversations(args.input_file)
    print(f"Successfully loaded {len(conversations)} conversations")
    
    # Extract user messages
    print("Extracting user messages...")
    user_messages = extract_user_messages(conversations, errors_file_path='errors.jsonl')
    
    # Format to JSONL
    print("Formatting messages to OpenAI-compliant JSONL (chat format)...")
    remove_duplicates_flag = not args.no_remove_duplicates
    jsonl_lines = format_to_jsonl(user_messages, max_tokens=args.max_tokens, remove_duplicates_flag=remove_duplicates_flag)
    
    # Write output file
    print(f"Writing output to: {args.output_file}")
    write_jsonl_output(args.output_file, jsonl_lines)


if __name__ == "__main__":
    main() 