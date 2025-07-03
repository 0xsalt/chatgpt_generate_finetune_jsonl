# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-01-27

### Added
- OpenAI compliance improvements (FINETUNE-002)
- Token limit enforcement with tiktoken
- Duplicate removal functionality
- Enhanced CLI options for customization
- Empty entry filtering
- Token counting and validation
- Chat format support for GPT-3.5-turbo fine-tuning

### Changed
- **BREAKING**: Output format changed from completion format to chat format
- Output now uses `messages` array with `user`/`assistant` roles
- Removed `--prompt-mode` option (no longer needed with chat format)
- Updated documentation for GPT-3.5-turbo compatibility

### Fixed
- Added minimal prompt field for OpenAI CLI compatibility
- Output format now includes both `prompt` and `completion` keys

## [1.0.0] - 2025-01-27

### Added
- Initial implementation of `generate_finetune_jsonl.py` script (FINETUNE-001)
- Smart text extraction from OpenAI conversation exports
- Audio transcription extraction support
- Automatic handling of multimedia content (images, audio files)
- JSONL output formatting with prompt/completion structure
- Robust error handling and logging to `errors.jsonl`
- Comprehensive help system and documentation
- Argument parsing with `argparse` for input/output file specification
- Graceful error handling for file operations and JSON parsing
- `--version` flag support reading from `.version` file

### Fixed
- Proper handling of non-string content types in conversation data
- Graceful skipping of malformed conversation entries
- Audio transcription text extraction (was previously skipped incorrectly) 