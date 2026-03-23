#!/usr/bin/env python3
"""
Scrape Hugging Face trending models and return structured data.
Usage: python3 scrape_hf_trending.py [--task <task>] [--limit <n>] [--readme]
"""

import argparse
import json
import re
import urllib.request
import urllib.error


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch content from URL with proper headers."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def fetch_trending_page(task: str = "", page: int = 0) -> str:
    """Fetch the Hugging Face models trending page."""
    url = "https://huggingface.co/models?sort=trending"
    if task:
        url += f"&pipeline_tag={task}"
    if page > 0:
        url += f"&p={page}"
    return fetch_url(url)


def fetch_model_card(model_path: str) -> str:
    """Fetch model card (README) content from a Hugging Face model."""
    raw_url = f"https://huggingface.co/{model_path}/raw/main/README.md"
    try:
        content = fetch_url(raw_url, timeout=15)
        return content
    except urllib.error.HTTPError:
        pass
    except Exception:
        pass

    # Fallback: try to extract from model page
    try:
        html = fetch_url(f"https://huggingface.co/{model_path}", timeout=15)
        card_match = re.search(
            r'<div[^>]*class="[^"]*prose[^"]*"[^>]*>(.*?)</div>',
            html,
            re.DOTALL
        )
        if card_match:
            text = re.sub(r'<[^>]+>', '', card_match.group(1))
            return text.strip()
    except Exception:
        pass

    return ""


def extract_model_summary(readme: str, max_lines: int = 40) -> str:
    """Extract a summary from model card/README content."""
    if not readme:
        return ""

    lines = readme.split("\n")
    summary_lines = []
    in_code_block = False
    code_block_count = 0

    for line in lines:
        if not summary_lines and not line.strip():
            continue

        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                code_block_count += 1
            if code_block_count > 2:
                continue
            summary_lines.append(line.rstrip())
            continue
        if in_code_block and code_block_count > 2:
            continue

        if re.match(r'^\[!\[', line) and 'badge' in line.lower():
            continue
        if re.match(r'^<img', line) and 'badge' in line.lower():
            continue

        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        cleaned = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', cleaned)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)

        if cleaned.strip():
            summary_lines.append(cleaned.rstrip())

        if len(summary_lines) >= max_lines:
            break

    return "\n".join(summary_lines[:max_lines])


def parse_trending_models(html: str) -> list[dict]:
    """Parse trending models from Hugging Face HTML."""
    models = []

    # Find all article elements containing model cards
    article_pattern = r'<article[^>]*>(.*?)</article>'
    article_matches = re.findall(article_pattern, html, re.DOTALL)

    for article in article_matches:
        model = {}

        # Extract model path from href
        href_match = re.search(r'href="/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)"', article)
        if not href_match:
            continue

        model_path = href_match.group(1)
        model["path"] = model_path
        model["url"] = f"https://huggingface.co/{model_path}"

        # Extract model name from h4
        name_match = re.search(r'<h4[^>]*>([^<]+)</h4>', article)
        if name_match:
            model["name"] = name_match.group(1).strip()
        else:
            model["name"] = model_path

        # Split into owner and model name
        parts = model_path.split("/")
        model["owner"] = parts[0] if parts else ""
        model["model_name"] = parts[1] if len(parts) > 1 else ""

        # Extract text content and parse metadata
        # Format: ModelName • Task • Params • Updated X • Downloads • Likes
        text_content = re.sub(r'<[^>]+>', ' ', article)
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        # Split by bullet separator
        meta_parts = text_content.split("•")
        if len(meta_parts) >= 2:
            meta_parts = [p.strip() for p in meta_parts]

            # First part is model name (skip)
            # Second part is usually task
            if len(meta_parts) > 1:
                task_text = meta_parts[1].strip()
                # Check if it looks like a task type
                if not re.search(r'^\d', task_text) and "updated" not in task_text.lower():
                    model["task"] = task_text

            # Look for specific patterns in remaining parts
            for part in meta_parts[2:]:
                part_lower = part.lower()

                # Updated time
                if "updated" in part_lower:
                    model["updated"] = part.strip()

                # Parameters (ends with B or M)
                elif re.search(r'^\d+\.?\d*[BM]$', part.strip()):
                    if "parameters" not in model:
                        model["parameters"] = part.strip()

                # Downloads (ends with k or M, not B)
                elif re.search(r'^\d+\.?\d*[kM]$', part.strip()) and "parameters" not in model:
                    if "downloads" not in model:
                        model["downloads"] = part.strip()

                # Likes (pure number or with k/M, usually last)
                elif re.search(r'^\d+\.?\d*[kM]?$', part.strip()):
                    model["likes"] = part.strip()

        models.append(model)

    return models


def format_output(models: list[dict], format_type: str = "markdown", include_readme: bool = False) -> str:
    """Format models for output."""
    if format_type == "json":
        if include_readme:
            for model in models:
                readme = fetch_model_card(model["path"])
                model["readme"] = extract_model_summary(readme)
        return json.dumps(models, indent=2, ensure_ascii=False)

    lines = ["# Hugging Face Trending Models\n"]

    for i, model in enumerate(models, 1):
        name = model.get("name", model.get("path", "Unknown"))
        url = model.get("url", "")
        lines.append(f"## {i}. [{name}]({url})")

        # Owner info
        if model.get("owner") and model.get("model_name"):
            lines.append(f"\n**Owner:** {model['owner']} | **Model:** {model['model_name']}")

        # Metadata line
        meta = []
        if model.get("task"):
            meta.append(f"Task: {model['task']}")
        if model.get("parameters"):
            meta.append(f"Params: {model['parameters']}")
        if model.get("downloads"):
            meta.append(f"Downloads: {model['downloads']}")
        if model.get("likes"):
            meta.append(f"Likes: {model['likes']}")
        if model.get("updated"):
            meta.append(model['updated'])

        if meta:
            lines.append(f"\n{' | '.join(meta)}")

        # Fetch and add model card summary
        if include_readme:
            readme = fetch_model_card(model["path"])
            if readme:
                summary = extract_model_summary(readme)
                if summary:
                    lines.append(f"\n### Model Card\n\n```\n{summary}\n```")

        lines.append("\n---\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scrape Hugging Face trending models")
    parser.add_argument("--task", default="", help="Filter by task (e.g., text-generation, image-classification)")
    parser.add_argument("--page", type=int, default=0, help="Page number (default: 0)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--no-readme", action="store_true",
                        help="Skip model card summary (faster, default includes readme)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of models to fetch (0 = all)")
    args = parser.parse_args()

    html = fetch_trending_page(args.task, args.page)
    models = parse_trending_models(html)

    if args.limit > 0:
        models = models[:args.limit]

    # Default: include readme, use --no-readme to skip
    include_readme = not args.no_readme
    output = format_output(models, args.format, include_readme)
    print(output)


if __name__ == "__main__":
    main()