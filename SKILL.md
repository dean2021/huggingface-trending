---
name: huggingface-trending
description: 'Fetch and display Hugging Face trending AI models. Use when user asks about trending models on HuggingFace, popular AI models, what models are hot on HuggingFace, or wants to discover new trending machine learning models. Triggers: "HuggingFace trending", "HF trending", "trending models", "popular AI models", "HF models", "HuggingFace 模型".'
---

# Hugging Face Trending Models

Fetch trending AI models from Hugging Face with model names, URLs, and statistics.

## Usage

Run the scraping script:

```bash
python3 scripts/scrape_hf_trending.py [options]
```

**Options:**
- `--task <task>` - Filter by task (e.g., `text-generation`, `image-classification`)
- `--page <n>` - Page number (default: 0)
- `--readme` - Include model card summary for each model (slower)
- `--limit <n>` - Limit number of models to fetch (0 = all)
- `--format <markdown|json>` - Output format (default: markdown)

## Examples

**Get trending models:**
```bash
python3 scripts/scrape_hf_trending.py
```

**Get top 10 models with model card details:**
```bash
python3 scripts/scrape_hf_trending.py --readme --limit 10
```

**Get JSON output for processing:**
```bash
python3 scripts/scrape_hf_trending.py --format json
```

## Output Fields

Each model includes:
- `name` - Model name (e.g., `Qwen/Qwen3.5-9B`)
- `url` - Full Hugging Face URL
- `owner` - Model owner/organization
- `task` - Task type (e.g., Text Generation, OCR)
- `parameters` - Parameter count (e.g., 35B)
- `downloads` - Download count
- `likes` - Like count
- `updated` - Last update time