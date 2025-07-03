#!/usr/bin/env python3
"""
Estimate Fine-tuning Cost

Calculate estimated costs for OpenAI fine-tuning based on token count.
Works with OpenAI chat format JSONL files.

Usage:
    python estimate_finetune_cost.py <file.jsonl>
    ./estimate_finetune_cost.py <file.jsonl>
"""

import json
import sys
import os
import tiktoken

def extract_content_from_messages(data):
    """Extract all content from messages array in chat format."""
    messages = data.get("messages", [])
    content = ""
    for message in messages:
        content += message.get("content", "")
    return content

def estimate_tokens_and_cost(filepath, model_name="gpt-3.5-turbo"):
    encoding = tiktoken.get_encoding("cl100k_base")

    total_tokens = 0
    total_lines = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                
                # Handle new chat format
                if "messages" in data:
                    text = extract_content_from_messages(data)
                # Handle old prompt/completion format for backward compatibility
                else:
                    prompt = data.get("prompt", "")
                    completion = data.get("completion", "")
                    text = prompt + completion
                
                tokens = len(encoding.encode(text))
                total_tokens += tokens
                total_lines += 1
            except json.JSONDecodeError:
                print("Warning: Skipping invalid JSON line.")
                continue

    # Pricing for gpt-3.5-turbo fine-tuning
    epochs = 2
    price_train_per_1k = 0.012  # Training cost per 1K tokens
    price_infer_per_1k = 0.008  # Inference cost per 1K tokens

    tokens_per_epoch = total_tokens
    total_train_tokens = tokens_per_epoch * epochs
    estimated_train_cost = (total_train_tokens / 1000) * price_train_per_1k
    estimated_infer_cost = (total_tokens / 1000) * price_infer_per_1k

    print(f"\nFile: {filepath}")
    print(f"Lines processed: {total_lines}")
    print(f"Estimated total tokens (1 epoch): {tokens_per_epoch:,}")
    print(f"Estimated training cost (2 epochs): ${estimated_train_cost:.2f} @ ${price_train_per_1k}/1K")
    print(f"Estimated inference cost only: ${estimated_infer_cost:.2f} @ ${price_infer_per_1k}/1K")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python estimate_finetune_cost.py <file.jsonl>")
        sys.exit(1)

    estimate_tokens_and_cost(sys.argv[1]) 