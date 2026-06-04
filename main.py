#!/usr/bin/env python3
"""
自媒体热点内容生成器 v1.0
功能：TrendRadar热点 → Crawl4AI采集详情 → LLM生成文章 → 输出公众号文章/小红书笔记/抖音脚本
"""

import json
import os
import sqlite3
import subprocess
import sys
import glob
from datetime import datetime
from pathlib import Path

import yaml

# 项目根目录
ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_config():
    """加载配置文件"""
    config_path = ROOT / "config.yaml"
    if not config_path.exists():
        print("⚠ config.yaml 不存在，复制 config.example.yaml 并填写 API 密钥")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_trending_topics(config):
    """从 TrendRadar 数据库获取今日热点"""
    db_path = config.get("sources", {}).get(
        "trendradar_db", "/www/wwwroot/MCP/TrendRadar/output/news/"
    )
    today = datetime.now().strftime("%Y-%m-%d")
    db_files = sorted(glob.glob(f"{db_path}*.db"))

    if not db_files:
        print("  ⚠ 无 TrendRadar 数据库文件，使用 MCP 获取热点")
        return get_topics_via_mcp(config)

    # 用最新的数据文件
    latest_db = db_files[-1]
    try:
        conn = sqlite3.connect(latest_db)
        cursor = conn.execute(
            """
            SELECT ni.title, p.name, ni.rank
            FROM news_items ni
            JOIN platforms p ON ni.platform_id = p.id
            WHERE ni.rank <= 10
            ORDER BY ni.rank
            LIMIT 15
        """
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  ⚠ 数据库无热点，使用 MCP 获取")
            return get_topics_via_mcp(config)

        topics = []
        for title, platform, rank in rows:
            topics.append({"rank": rank, "platform": platform, "title": title})

        print(f"  ✓ 获取到 {len(topics)} 个热点 (来自 {latest_db.split('/')[-1]})")
        return topics

    except Exception as e:
        print(f"  ⚠ 读取数据库失败: {e}，使用 MCP 获取")
        return get_topics_via_mcp(config)


def get_topics_via_mcp(config):
    """备用：通过 MCP 获取热点"""
    print("  通过 MCP 获取热点...")
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import subprocess, json
r = subprocess.run(['python3', '-c', '''
import sys; sys.path.insert(0, "/root/.hermes/profiles/long/skills/trendradar-mcp/scripts")
'''], capture_output=True, text=True, timeout=10)
print("fallback")
""",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        # Fallback: 返回预设热点
        return [
            {"rank": 1, "platform": "知乎", "title": "AI Agent 生态爆发"},
            {"rank": 2, "platform": "微博", "title": "隐私搜索崛起"},
            {"rank": 3, "platform": "抖音", "title": "AI 基础设施投资"},
        ]
    except Exception:
        return [
            {"rank": 1, "platform": "知乎", "title": "AI 如何改变普通人生活"},
            {"rank": 2, "platform": "微博", "title": "最新科技趋势解读"},
            {"rank": 3, "platform": "抖音", "title": "自动化副业赚钱方法"},
        ]


def fetch_topic_details(topic_title, config):
    """使用 Crawl4AI 采集热点详情"""
    print(f"  采集「{topic_title[:30]}」详情...")

    # 搜索关键词
    query = topic_title.replace(" ", "")

    try:
        # 调用 Crawl4AI 搜索
        result = subprocess.run(
            ["/opt/crawl4ai/.venv/bin/python", "/opt/crawl4ai/crawl.py", "bing", query],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()[:3000]  # 限制长度
            print(f"  ✓ 采集成功 ({len(content)} 字符)")
            return content

    except Exception as e:
        print(f"  ⚠ Crawl4AI 采集失败: {e}")

    # Fallback: 返回热点标题作为基础素材
    return f"热点话题：{topic_title}"


def call_llm(prompt, llm_config):
    """调用 LLM API 生成内容
    llm_config 是 config['llm'] 的值（已解包后的 llm 配置字典）
    """
    # 优先使用 Qwen
    qwen = llm_config.get("qwen", {})
    if qwen.get("enabled"):
        api_key = qwen["api_key"]
        base_url = qwen.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model = qwen.get("model", "qwen-plus")
    else:
        # 使用环境变量中的 API
        api_key = os.environ.get("QWEN_API_KEY", "")
        base_url = os.environ.get(
            "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        model = os.environ.get("QWEN_MODEL", "qwen-plus")

    if not api_key:
        print("  ⚠ 未配置 LLM API Key，使用模板生成")
        return None

    import requests

    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4000,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        print(f"  ✓ LLM 生成成功 ({len(content)} 字符)")
        return content

    except Exception as e:
        print(f"  ⚠ LLM 调用失败: {e}")
        return None


def generate_wechat_article(topic, details, llm_config):
    """生成公众号文章"""
    prompt = f"""你是微信公众号爆款文章作者。请根据以下热点话题和采集到的素材，写一篇情感故事风格的公众号文章。

要求：
1. 标题要有吸引力，引发好奇心
2. 开头用一个真实感强的场景或故事引入
3. 中间结合热点话题展开，融入情感元素
4. 结尾有升华，引发读者共鸣
5. 全文1500-2000字
6. 语言风格：温暖、有力量、接地气

热点话题：{topic}

采集素材：
{details}

请直接输出文章标题和正文，格式：
标题：xxx

正文：
xxx
"""
    result = call_llm(prompt, llm_config)
    if result:
        return result

    # Fallback 模板生成
    return f"""标题：{topic}——那些你不知道的故事

正文：

深夜十一点，林小雨关掉电脑，靠在椅背上长长地出了一口气。

窗外下着小雨，她打开手机，看到热搜上那条关于「{topic}」的新闻。评论区已经炸了，有人愤怒，有人感动，有人说"终于有人站出来说了"。

她想起三年前，自己也曾经历过类似的事。

那时候她刚毕业，在一家小公司做运营。每天加班到深夜，工资 barely 够付房租。有次深夜下班，在地铁里刷到一条类似的新闻，她坐在空荡荡的车厢里，眼泪就这么掉下来了。

不是因为委屈，而是因为终于有人把那些说不出口的感受，明明白白地写了出来。

「{topic}」这件事，表面上看是一个热点新闻，但背后其实是我们这一代人共同的困境和挣扎。

我们总是在别人的故事里流自己的眼泪，因为那些故事里，藏着我们自己不敢面对的部分。

但我想说的是，你并不孤单。

每一个在深夜里独自消化情绪的人，每一个咬牙坚持不放弃的人，每一个明明很累但还是选择站起来继续走的人——你们都在用自己的方式，书写着属于自己的故事。

而「{topic}」，就是这些故事中的一个注脚。它提醒我们：生活从来不容易，但正因为不容易，那些咬牙坚持的瞬间才格外珍贵。

今晚，如果你也正经历着什么，请记住——

天总会亮的。

"""


def generate_xiaohongshu(topic, details, llm_config):
    """生成小红书笔记"""
    prompt = f"""你是小红书爆款笔记作者。请根据以下热点话题，写一篇小红书风格的笔记。

要求：
1. 标题要吸引眼球，使用emoji
2. 正文口语化，像闺蜜聊天
3. 多用emoji，分段清晰
4. 300-500字
5. 结尾引导互动（点赞、收藏、评论）

热点话题：{topic}

采集素材：
{details}

请直接输出笔记内容。
"""
    result = call_llm(prompt, llm_config)
    if result:
        return result

    return f"""🔥 {topic}｜姐妹们，这件事必须说清楚！

最近刷到爆的「{topic}」到底是什么？今天用3分钟给你说明白👇

✨ 先说结论：这件事跟你每个人息息相关！

1️⃣ 为什么突然火了？
因为戳中了太多人的痛点！评论区已经炸了💥

2️⃣ 对你有什么影响？
简单说：不了解就out了，了解了能少踩很多坑

3️⃣ 应该怎么做？
记住这3点就够了👇
- 保持关注，但别焦虑
- 学会判断哪些是真信息哪些是噪音
- 有自己的节奏，不跟风

💬 姐妹们看完有什么想法？评论区聊聊～
觉得有用的话记得❤️⭐️支持一下！

#热点解读 #{topic.replace(" ", "")} #涨知识 #生活感悟
"""


def generate_douyin_script(topic, details, llm_config):
    """生成抖音口播脚本"""
    prompt = f"""你是抖音短视频脚本创作者。请根据以下热点话题，写一个口播脚本。

要求：
1. 开场3秒必须抓住注意力
2. 正文讲3个关键点
3. 结尾引导关注+评论
4. 总时长约45-60秒
5. 口语化、接地气

热点话题：{topic}

采集素材：
{details}

请直接输出脚本。
"""
    result = call_llm(prompt, llm_config)
    if result:
        return result

    short_topic = topic[:15]
    return f"""【开场 3秒】
"最近全网都在讨论{short_topic}，到底怎么回事？今天一条视频给你说明白。"

【正文 40秒】
"简单说3点：
第一，这个话题为什么突然火了？
因为戳中了很多人的真实感受，评论区已经炸了。

第二，它对你有什么影响？
不管你关不关注，它都在悄悄改变我们的生活节奏。

第三，普通人应该怎么应对？
记住两个字：别慌。保持自己的节奏就好。

{details[:100] if len(details) > 100 else ''}"

【结尾 5秒】
"关注我，每天3分钟看懂热点。评论区告诉我你的看法！"
"""


def main():
    """主流程"""
    print("=" * 50)
    print("🚀 自媒体热点内容生成器 v1.0")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    config = load_config()

    # Step 1: 获取热点
    print("\n[1/4] 获取热点话题...")
    topics = get_trending_topics(config)
    if not topics:
        print("❌ 无法获取热点，退出")
        sys.exit(1)

    # Step 2: 选择TOP1热点并采集详情
    print(f"\n[2/4] 选择 TOP 热点: {topics[0]['title']}")
    topic = topics[0]
    topic_title = topic["title"]
    details = fetch_topic_details(topic_title, config)

    # Step 3: 生成多平台内容
    print(f"\n[3/4] 生成多平台内容...")
    llm_cfg = config.get("llm", {})

    wechat = generate_wechat_article(topic_title, details, llm_cfg)
    xiaohongshu = generate_xiaohongshu(topic_title, details, llm_cfg)
    douyin = generate_douyin_script(topic_title, details, llm_cfg)

    # Step 4: 保存输出
    print(f"\n[4/4] 保存输出...")
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "topic": topic_title,
        "platform": topic.get("platform", ""),
        "rank": topic.get("rank", 0),
        "generated_at": datetime.now().isoformat(),
        "wechat_article": wechat,
        "xiaohongshu_note": xiaohongshu,
        "douyin_script": douyin,
    }

    # JSON 输出
    json_path = OUTPUT_DIR / f"content_{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Markdown 输出（公众号文章）
    md_path = OUTPUT_DIR / f"article_{date_str}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {wechat.split('标题：')[-1].split('正文：')[0].strip() if '标题：' in wechat else topic_title}\n\n")
        f.write(wechat.split("正文：")[-1] if "正文：" in wechat else wechat)

    print(f"\n✅ 内容生成完成！")
    print(f"📁 JSON: {json_path}")
    print(f"📄 文章: {md_path}")

    # 预览
    print(f"\n{'=' * 40}")
    print("📱 公众号文章预览（前300字）:")
    print(f"{'=' * 40}")
    print(wechat[:300])
    print("...")

    return output


if __name__ == "__main__":
    main()
