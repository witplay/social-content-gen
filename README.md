# 🚀 自媒体热点内容生成器

> 自动追踪全网热点，一键生成多平台适配内容，让自媒体创作效率提升10倍。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

- 🔥 **自动热点追踪** — 接入11个平台热榜（知乎/微博/抖音/B站/头条等）
- 📝 **多平台内容生成** — 一键生成公众号文章、小红书笔记、抖音脚本
- 🤖 **AI驱动** — 支持多种LLM（OpenAI/Claude/本地模型）
- ⚡ **自动化发布** — 可选一键发布到各平台（需配置账号）
- 📊 **热点分析** — 追踪话题热度变化，找出最佳创作时机

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/social-content-gen.git
cd social-content-gen

# 安装依赖
pip install -r requirements.txt
```

### 配置

复制配置文件并编辑：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`：

```yaml
# LLM配置（至少配置一个）
llm:
  openai:
    api_key: "sk-..."
    model: "gpt-4o"
  # 或使用本地模型
  local:
    base_url: "http://localhost:8000/v1"
    model: "qwen2.5-72b"

# 热点源配置
sources:
  trendradar_db: "/path/to/trendradar/output/news/"
  
# 输出配置
output:
  dir: "./output"
  format: "json"  # json/markdown/all
```

### 使用

```bash
# 生成今日热点内容
python main.py

# 指定话题
python main.py --topic "AI Agent"

# 指定平台
python main.py --platform wechat_mp,xiaohongshu

# 查看帮助
python main.py --help
```

## 📋 输出示例

### 公众号文章

```markdown
标题：黄金大跌，底层逻辑崩了吗？3个信号告诉你真相

最近，黄金价格突然大跌，全网都在讨论。作为关注财经的自媒体人，
我认为这个信号值得每个人警惕...
```

### 小红书笔记

```markdown
🔥黄金大跌怎么回事？3分钟看懂背后的逻辑！

姐妹们！最近黄金价格跌得厉害，到底怎么回事？
今天给你说明白👇

✨ 核心要点：
1️⃣ 为什么突然大跌？
2️⃣ 对你有什么影响？
3️⃣ 现在该买还是该卖？
```

### 抖音脚本

```
开场（3秒）：
"黄金大跌！你的首饰还值钱吗？"

正文（30秒）：
"简单说3点：为什么跌、影响谁、怎么办..."
```

## 🔧 高级功能（付费版）

| 功能 | 免费版 | 付费版 |
|------|--------|--------|
| 热点扫描 | ✅ 每日10条 | ✅ 无限制 |
| 内容生成 | ✅ 基础模板 | ✅ AI定制风格 |
| 平台支持 | 3个 | 11个 |
| 定时任务 | ❌ | ✅ 自动扫描+生成 |
| 数据分析 | ❌ | ✅ 热度追踪+最佳发布时间 |
| 多账号管理 | ❌ | ✅ 支持多账号轮换 |
| 客服支持 | 社区 | 优先支持 |

## 💰 定价

- **免费版**: 永久免费，基础功能
- **专业版**: ¥99/月 或 ¥299/年
- **企业版**: 联系定制

[👉 立即购买专业版](https://gumroad.com/YOUR_PRODUCT)

## 📖 文档

- [快速开始指南](docs/quickstart.md)
- [配置说明](docs/config.md)
- [API文档](docs/api.md)
- [常见问题](docs/faq.md)

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 💬 联系方式

- 微信: YOUR_WECHAT
- 邮箱: YOUR_EMAIL
- GitHub Issues: [提问/建议](https://github.com/YOUR_USERNAME/social-content-gen/issues)
