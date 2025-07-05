# Generate Fine-tuning JSONL

## Quickstart

```bash
# 1. Generate chat format from conversations
python generate_finetune_jsonl.py conversations.json chat_output.jsonl

# 2. Filter for blog-style content only  
python filter_blog_style.py chat_output.jsonl blog_filtered.jsonl

# 3. Estimate costs (optional)
python estimate_finetune_cost.py blog_filtered.jsonl
```

## Overview

The **Generate Fine-tuning JSONL** script is a lightweight Python tool that extracts user messages from OpenAI conversation exports and formats them for AI model fine-tuning. It handles the complexity of large `conversations.json` files by intelligently extracting text content while properly handling multimedia elements.

## Features

This script provides essential functionality for fine-tuning data preparation:

* **Smart Text Extraction**: Extracts user messages, including audio transcriptions, while skipping non-text content (images, audio files)
* **JSONL Format Output**: Generates fine-tuning-ready JSONL with proper prompt/completion structure
* **Robust Error Handling**: Graceful handling of malformed data with detailed error reporting
* **Comprehensive Help**: Clear usage instructions and examples

## Getting Started

### Prerequisites

* Python 3.x (already installed on most systems).
* Your `conversations.json` file, obtained from an OpenAI data export.
* Virtual environment (recommended): `python -m venv .venv && source .venv/bin/activate`
* OpenAI CLI (for file management): `pip install openai`

### Installation

1. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Workflow: Three-Step Process

This project consists of three Python scripts that work together to create fine-tuning data:

#### Step 1: Generate Chat Format JSONL
```bash
# Extract user messages and convert to OpenAI chat format
python generate_finetune_jsonl.py conversations.json chat_output.jsonl
```

#### Step 2: Filter for Blog-Style Content
```bash
# Filter the chat output to keep only blog-style entries
python filter_blog_style.py chat_output.jsonl filtered_output.jsonl
```

#### Step 3: Estimate Fine-tuning Costs (Optional)
```bash
# Calculate estimated costs for OpenAI fine-tuning
python estimate_finetune_cost.py filtered_output.jsonl
```

#### Step 4: Manage OpenAI Files (Optional)
```bash
# List all files in your OpenAI account
python openai_manage_files.py --list

# Delete a specific file by ID
python openai_manage_files.py --delete file-abc123
```

This utility helps you manage files uploaded to OpenAI for fine-tuning.

### Complete Example Workflow

```bash
# 1. Generate chat format from conversations
python generate_finetune_jsonl.py conversations.json chat_output.jsonl

# 2. Filter for blog-style content only
python filter_blog_style.py chat_output.jsonl blog_filtered.jsonl

# 3. Estimate costs (optional)
python estimate_finetune_cost.py blog_filtered.jsonl

# 4. Your final output is ready: blog_filtered.jsonl
```

### Output Format

Each line in the output JSONL file contains a fine-tuning example in OpenAI chat format:
```json
{
    "messages": [
        {"role": "user", "content": "Write a blog post in my voice."},
        {"role": "assistant", "content": " Your extracted user message\n"}
    ]
}
```

This format is compatible with OpenAI GPT-3.5-turbo fine-tuning and includes:
- **User role**: Consistent prompt for blog post generation
- **Assistant role**: Your extracted content with leading whitespace for better tokenization
- **Proper newline handling**: Maintains formatting for better training

### Error Handling

The script intelligently handles various content types:
- Text messages: Extracted for fine-tuning
- Audio transcriptions: Extracted for fine-tuning  
- Images: Skipped (logged to errors file)
- Audio files: Skipped (logged to errors file)
- Malformed data: Skipped with warnings

### Content Filtering

The `filter_blog_style.py` script applies intelligent filtering to keep only blog-style content:

**Keeps content that:**
- Has at least 40 characters
- Contains at least 3 sentences (punctuation marks)
- Doesn't start with question words (how, what, when, where, why, can, could, should)
- Doesn't contain technical keywords ($, openai, jsonl, flag, --help, curl, python)

**Example filtering results:**
- Input: 796 lines from sample data
- Output: 380 blog-style entries (48% retention rate)

Future Enhancements
We envision expanding this script's capabilities in future iterations to include:

- **Flexible Message Extraction**: Options to export assistant-only messages, or both user and assistant messages
- **Conversation Filtering**: Filter conversations by specific date ranges or keywords  
- **Progress Indicators**: Display progress for very large input files to provide better user feedback
- **Content Type Filtering**: Selective extraction of specific content types
- **Batch Processing**: Handle multiple conversation files at once

Contributing
Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, please open an issue or submit a pull request on the GitHub repository.

License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## Roadmap

Planned features for upcoming releases:

- [ ] Add default `--help` usage output for each script
- [ ] Include sample data for immediate testing out of the box
- [ ] Implement unit tests for core functionality

---

## Version History

- **v1.1.0** - OpenAI compliance, chat format, token limits, duplicate removal
- **v1.0.0** - Initial release with completion format and basic extraction
