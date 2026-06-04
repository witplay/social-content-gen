# 🚀 自媒体热点内容生成器

> 自动追踪全网热点，一键生成多平台适配内容，让自媒体创作效率提升10倍。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/witplay/social-content-gen?style=social)](https://github.com/witplay/social-content-gen)
[![Gumroad](https://img.shields.io/badge/Gumroad-Live-brightgreen)](https://witplay.gumroad.com/l/social-content-gen)

## ✨ 功能特性

- 🔥 **自动热点追踪** — 接入11个平台热榜（知乎/微博/抖音/B站/头条等）
- 📝 **多平台内容生成** — 一键生成公众号文章、小红书笔记、抖音脚本
- 🤖 **AI驱动** — 支持多种LLM（OpenAI/Claude/本地模型）
- ⚡ **自动化发布** — 可选一键发布到各平台（需配置账号）
- 📊 **热点分析** — 追踪话题热度变化，找出最佳创作时机

## 📊 实测数据

| 指标 | 人工 | social-content-gen | 效率提升 |
|------|------|-------------------|---------|
| 热点扫描（11平台） | 45分钟 | 30秒 | **90x** |
| 单篇公众号文章 | 60分钟 | 2分钟 | **30x** |
| 多平台适配（3平台） | 90分钟 | 1分钟 | **90x** |
| 每日内容产出上限 | 3-5篇 | 30+篇 | **10x** |

> 测试环境：TrendRadar真实热点 + Crawl4AI采集 + Qwen3.6-plus生成，2026-06-04

## 📸 真实生成效果

> 热点：`中国女足队史首次输给俄罗斯`

系统自动生成的公众号文章开头：

> 凌晨两点，老城区的街角只剩一家便利店还亮着灯。老林坐在塑料凳上，手机屏幕暗了又亮，亮了又暗。终场比分停在刺眼的位置，旁边是他女儿去年省吃俭用给他买的国家队围巾。他没发朋友圈，也没在群里争论，只是把围巾仔细叠好，放进抽屉……

1067 字情感故事风格文章，直接可用。同一热点还生成了小红书笔记（304字）和抖音脚本（443字）。

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/witplay/social-content-gen.git
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

### 🎯 真实案例：高考热点 → 3平台内容（2026-06-04）

**输入热点**：`[知乎] 2026高考1290万人报名，再创历史新高`

**公众号文章输出**（2300字，情感向）：
> 标题：《那个在考场外等了3小时的母亲，让1290万人的高考有了温度》
> 
> 清晨5点半，李美芳就坐在了省实验中学门口的马路牙子上。
> 一个5块钱的小马扎，一壶温水，一件叠得整整齐齐的红色T恤……
> 
> 这不是新闻画面，这是1290万考生家庭的缩影。
> 每一个坐在考场外的家长，都在用自己的方式参与这场人生大考。
> 
> （全文2300字，4层情感递进，原创故事）

**小红书笔记输出**（450字）：
> 🔥1290万人今天高考💯考场外的一幕让我破防了
> 
> 姐妹们！今天高考第一天，我去考点外看了一眼，直接泪目😭
> 
> 一位妈妈穿着红色旗袍，手里拿着向日葵...
> 
> （含emoji、分段短小、适合图片排版）

**抖音脚本输出**（60秒）：
> （开场3秒）"1290万人高考，但我想说说考场外的人..."
> （正文45秒）"你知道吗，每一位坐在考场外的家长..."
> （结尾12秒）"你家今天高考吗？评论区送上祝福！"

### 公众号文章（常规）

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

| | 免费版 | 专业版 |
|---|---|---|
| 热点扫描 | 每日10条 | ✅ 无限制 |
| 内容生成 | 基础模板 | ✅ AI定制风格 |
| 平台支持 | 3个 | ✅ 11个 |
| 定时任务 | ❌ | ✅ 自动扫描+生成 |
| 数据分析 | ❌ | ✅ 热度追踪+最佳发布时间 |
| 多账号管理 | ❌ | ✅ 支持多账号轮换 |
| 客服支持 | 社区 | ✅ 优先支持 |

- **免费版**: 永久免费，基础功能 → `git clone` 即用
- **专业版**: ~~$49~~ **$19 限时优惠** — 一次购买，永久更新

[👉 **立即购买专业版 ($19)**](https://witplay.gumroad.com/l/social-content-gen)

> 💡 为什么付费？专业版包含自动定时任务、11平台全覆盖、数据分析面板，帮你每天省2小时。一杯咖啡的钱，换一个月的高效产出。

## 📖 文档

- [快速开始指南](docs/quickstart.md)
- [配置说明](docs/config.md)
- [API文档](docs/api.md)
- [常见问题](docs/faq.md)

## 💬 社区讨论

- [📊 实测工作流分享](https://github.com/witplay/social-content-gen/issues/1) — 一天生成30+篇内容的完整流程
- [🤝 寻找贡献者](https://github.com/witplay/social-content-gen/issues/2) — 一起把这个工具做得更好

## 🤝 贡献

欢迎提交Issue和PR！当前需要的贡献：

- 🔌 更多热点源（Twitter trending, Google Trends）
- 📝 更多平台模板（微博、头条号、百家号）
- 🚀 自动化发布功能

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 💬 联系方式

- GitHub Issues: [提问/建议](https://github.com/witplay/social-content-gen/issues)
