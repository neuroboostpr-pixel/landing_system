#!/usr/bin/env python3
"""
Extract real content from prototype.yaml and generate content.md + extraction-log.md.

This fixes BUG-001: Content extraction from prototype should produce real texts, not generic templates.

Usage:
  python3 extract-content-from-prototype.py <prototype.yaml> [--output <content.md>] [--log-output <extraction-log.md>] [--debug]
"""

import sys
import os
import yaml
import json
import re
from datetime import datetime
from pathlib import Path

TEMPLATE_PATTERNS = [
    r"lorem ipsum",
    r"description goes here",
    r"add your text",
    r"your text here",
    r"sample text",
    r"\[placeholder\]",
]


def load_yaml(filepath):
    """Load and parse YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {filepath}: {e}")


def load_markdown_fallback(filepath):
    """Load markdown file as fallback text source."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def extract_text_from_block(block, fallback_md=""):
    """Extract text content from a block definition.

    A block may have:
    - text: for headings, paragraphs, buttons
    - title: for cards, sections
    - label: for feature cards
    - description: for feature descriptions
    - price: for course cards
    - fields: for forms (array of {label, placeholder, type})

    Returns dict with extracted fields.
    """
    extracted = {}

    # Direct text fields
    for field in ['text', 'title', 'label', 'description', 'price', 'highlight']:
        if field in block and block[field]:
            extracted[field] = block[field]

    # For forms: extract field labels
    if 'fields' in block and isinstance(block['fields'], list):
        extracted['form_fields'] = [
            f.get('label', f.get('name', ''))
            for f in block['fields']
            if f.get('label') or f.get('name')
        ]

    # For course cards: handle card_examples
    if 'card_examples' in block and isinstance(block['card_examples'], list):
        extracted['cards'] = []
        for card in block['card_examples']:
            card_info = {}
            for key in ['title', 'price', 'level', 'students', 'rating']:
                if key in card:
                    card_info[key] = card[key]
            if card_info:
                extracted['cards'].append(card_info)

    return extracted if extracted else {}


def validate_no_lorem(text):
    """Check if text contains generic template patterns."""
    for pattern in TEMPLATE_PATTERNS:
        if re.search(pattern, text.lower()):
            return False
    return True


def generate_content_md(prototype, debug=False):
    """Generate content.md from prototype structure.

    Returns tuple: (content_md_text, blocks_extracted_count, warnings_list)
    """
    content_lines = []
    warnings = []
    blocks_count = 0

    # Header
    project_name = prototype.get('project', 'Проект')
    content_lines.append(f"# Текстовый контент — {project_name}\n")
    content_lines.append("**Дата создания:** " + datetime.now().strftime('%Y-%m-%d') + "\n")
    content_lines.append("**Статус:** ✅ Утверждено\n")
    content_lines.append("**Источник:** Извлечено из prototype.yaml\n")
    content_lines.append("\n---\n")

    # Extract by sections
    sections = prototype.get('sections', [])
    for section in sections:
        section_name = section.get('name', section.get('id', 'Unknown'))
        section_id = section.get('id', '')

        content_lines.append(f"\n## {section_name}\n")

        blocks = section.get('blocks', [])
        if not blocks:
            warnings.append(f"Section '{section_name}' has no blocks")
            continue

        for block in blocks:
            block_type = block.get('type', 'unknown')
            block_label = block.get('label', block.get('title', block_type))

            content_lines.append(f"\n### {block_label}\n")

            # Extract all text from block
            extracted = extract_text_from_block(block)

            if not extracted:
                warnings.append(
                    f"Block '{block_label}' in section '{section_name}' has no text content"
                )
                content_lines.append("*(No text content found)*\n")
                continue

            # Render extracted content
            for key, value in extracted.items():
                if isinstance(value, str):
                    content_lines.append(f"{value}\n")
                elif key == 'form_fields' and isinstance(value, list):
                    for field in value:
                        content_lines.append(f"- {field}\n")
                elif key == 'cards' and isinstance(value, list):
                    for i, card in enumerate(value, 1):
                        content_lines.append(f"\n**Card {i}:**\n")
                        for card_key, card_val in card.items():
                            content_lines.append(f"- {card_key}: {card_val}\n")

            blocks_count += 1

    content_md = "".join(content_lines)

    # Validate that we don't have template text
    has_template = not validate_no_lorem(content_md)
    if has_template:
        warnings.append("CRITICAL: content.md contains template patterns")

    return content_md, blocks_count, warnings, sections


def generate_extraction_log(blocks_count, warnings, sections, validation_passed):
    """Generate extraction-log.md with summary."""
    log_lines = []

    log_lines.append("# Content Extraction Log\n")
    log_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    log_lines.append(f"**Status:** {'✅ SUCCESS' if validation_passed else '❌ FAILED'}\n")
    log_lines.append("\n")

    log_lines.append("## Extraction Summary\n")
    log_lines.append(f"- **Total blocks extracted:** {blocks_count}\n")
    log_lines.append(f"- **Total sections processed:** {len(sections)}\n")
    log_lines.append(f"- **Warnings found:** {len(warnings)}\n")

    if warnings:
        log_lines.append("\n## Warnings & Issues\n")
        for warning in warnings:
            log_lines.append(f"⚠️ {warning}\n")
    else:
        log_lines.append("\n## No Issues Found\n")

    log_lines.append("\n---\n")
    log_lines.append(f"**Validation:** {'✅ PASSED' if validation_passed else '❌ FAILED'}\n")

    return "".join(log_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: extract-content-from-prototype.py <prototype.yaml> [--output <out>] [--log-output <log>] [--debug]")
        sys.exit(1)

    prototype_file = sys.argv[1]
    output_file = None
    log_output_file = None
    debug = False

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--log-output" and i + 1 < len(sys.argv):
            log_output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--debug":
            debug = True
            i += 1
        else:
            i += 1

    # Load prototype
    try:
        prototype = load_yaml(prototype_file)
    except Exception as e:
        print(f"Error loading prototype: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate content
    try:
        content_md, blocks_count, warnings, sections = generate_content_md(prototype, debug)
    except Exception as e:
        print(f"Error generating content: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    validation_passed = validate_no_lorem(content_md) and len(warnings) == 0

    # Generate log
    log_md = generate_extraction_log(blocks_count, warnings, sections, validation_passed)

    # Write outputs
    if output_file:
        try:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content_md)
            if debug:
                print(f"✅ Wrote: {output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing {output_file}: {e}", file=sys.stderr)
            sys.exit(1)

    if log_output_file:
        try:
            os.makedirs(os.path.dirname(log_output_file) or '.', exist_ok=True)
            with open(log_output_file, 'w', encoding='utf-8') as f:
                f.write(log_md)
            if debug:
                print(f"✅ Wrote: {log_output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing {log_output_file}: {e}", file=sys.stderr)
            sys.exit(1)

    # Print summary to stdout
    print(f"Extracted {blocks_count} blocks from {len(sections)} sections")
    print(f"Status: {'✅ SUCCESS' if validation_passed else '❌ FAILED'}")
    if warnings:
        print(f"Warnings: {len(warnings)}")

    sys.exit(0 if validation_passed else 1)


if __name__ == "__main__":
    main()
