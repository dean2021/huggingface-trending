# Hugging Face Trending Skill

获取 Hugging Face 热门 AI 模型的 Claude Code 技能。抓取 Hugging Face Models 页面，返回包含详细介绍的结构化模型列表。

## 功能

- 获取 Hugging Face 热门模型列表
- **默认包含模型 Model Card 详细介绍**
- 支持按任务类型筛选（text-generation, image-classification 等）
- 支持分页浏览
- 支持 Markdown 和 JSON 输出格式

## 安装

将 `huggingface-trending.skill` 文件放入 Claude Code 的技能目录：

```bash
# 创建技能目录（如果不存在）
mkdir -p ~/.claude/skills

# 解压技能文件
unzip huggingface-trending.skill -d ~/.claude/skills/
```

或者手动复制：

```bash
cp -r huggingface-trending ~/.claude/skills/
```

## 使用

### 命令行方式

```bash
python3 ~/.claude/skills/huggingface-trending/scripts/scrape_hf_trending.py [选项]
```

### Claude Code 中使用

直接对 Claude 说以下任意关键词即可触发：

- "HuggingFace trending"
- "HF trending"
- "trending models"
- "看看 HuggingFace 热门模型"

## 命令选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--task <task>` | 按任务筛选（如 text-generation, image-classification） | 全部 |
| `--page <n>` | 页码 | 0 |
| `--no-readme` | 跳过模型介绍（更快） | 包含介绍 |
| `--limit <n>` | 限制返回模型数量 | 全部 |
| `--format <format>` | 输出格式：markdown, json | markdown |

## 示例

```bash
# 获取热门模型（默认包含详细介绍）
python3 scrape_hf_trending.py

# 获取前 10 个模型
python3 scrape_hf_trending.py --limit 10

# 快速模式（不含介绍）
python3 scrape_hf_trending.py --no-readme

# 按任务类型筛选
python3 scrape_hf_trending.py --task text-generation

# JSON 格式输出
python3 scrape_hf_trending.py --format json
```

## 输出示例

### Markdown 格式

```markdown
## 1. [Qwen/Qwen3.5-35B-A3B](https://huggingface.co/Qwen/Qwen3.5-35B-A3B)

**Owner:** Qwen | **Model:** Qwen3.5-35B-A3B

Downloads: 276k | Likes: 1.22k | Updated 12 days ago

### Model Card

# Qwen3.5-35B-A3B
Qwen3.5 represents a significant leap forward, integrating breakthroughs in
multimodal learning, architectural efficiency, reinforcement learning scale...

- 35B total parameters, ~3B active per forward pass (MoE)
- Unified Vision-Language Foundation
- 201 languages support
```

### JSON 格式

```json
{
  "path": "Qwen/Qwen3.5-35B-A3B",
  "url": "https://huggingface.co/Qwen/Qwen3.5-35B-A3B",
  "name": "Qwen3.5-35B-A3B",
  "owner": "Qwen",
  "downloads": "276k",
  "likes": "1.22k",
  "readme": "# Qwen3.5-35B-A3B\n..."
}
```

## 输出字段

每个模型包含：
- `name` - 模型名称
- `url` - Hugging Face 完整链接
- `owner` - 模型所有者/组织
- `model_name` - 模型名称
- `task` - 任务类型（如 Text Generation, OCR）
- `parameters` - 参数量（如 35B）
- `downloads` - 下载量
- `likes` - 点赞数
- `updated` - 更新时间
- `readme` - Model Card 详细介绍

## 依赖

- Python 3.6+
- 无需额外依赖（仅使用标准库）

## 相关技能

- [github-trending](https://github.com/yourname/github-trending) - 获取 GitHub 热门项目

## License

MIT