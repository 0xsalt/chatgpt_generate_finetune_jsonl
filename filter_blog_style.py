#!/usr/bin/env python3
"""
Filter Blog Style Content

A Python script to filter JSONL files and keep only blog-style content.
Works with OpenAI chat format JSONL files for fine-tuning.

Usage:
    python filter_blog_style.py input.jsonl output.jsonl
    ./filter_blog_style.py input.jsonl output.jsonl
"""

import json
import sys
import re

def is_bloggy(text):
    text = text.strip()
    if len(text) < 40:
        return False
    if len(re.findall(r'[.!?]', text)) < 3:
        return False
    if text.lower().startswith(("how ", "what ", "when ", "where ", "why ", "can ", "could ", "should ")):
        return False
    if any(keyword in text.lower() for keyword in ["$ ", "openai ", "jsonl", "flag", "--help", "curl", "python "]):
        return False
    return True

def extract_assistant_content(obj):
    """Extract assistant content from chat format structure."""
    messages = obj.get("messages", [])
    for message in messages:
        if message.get("role") == "assistant":
            return message.get("content", "").strip()
    return ""

def filter_file(input_path, output_path):
    kept = 0
    total = 0
    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            total += 1
            try:
                obj = json.loads(line)
                # Extract assistant content from chat format
                text = extract_assistant_content(obj)
                if is_bloggy(text):
                    outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")
                    kept += 1
            except json.JSONDecodeError:
                continue
    print(f"Filtered {kept} blog-style entries out of {total} total lines.")
    print(f"Output written to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python filter_blog_style.py input.jsonl output.jsonl")
        sys.exit(1)
    filter_file(sys.argv[1], sys.argv[2]) 