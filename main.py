#!/usr/bin/env python3
"""
自媒体热点内容生成器 v0.1
功能：扫描热点 → 采集详情 → 生成多平台内容
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def get_trending_topics(config=None):
    """获取热点话题（支持多数据源）"""
    print("[1/3] 扫描热点话题...")
    
    # 从配置获取数据源路径
    if config:
        db_path = config.get('sources', {}).get('trendradar_db', '')
    else:
        db_path = "/www/wwwroot/MCP/TrendRadar/output/news/"
    
    try:
        import sqlite3, glob
        db_files = sorted(glob.glob(f'{db_path}*.db'))
        if not db_files:
            print(f"  ⚠ 无TrendRadar数据 ({db_path})，使用备用方案")
            return get_trending_topics_fallback()
        
        conn = sqlite3.connect(db_files[-1])
        # 获取各平台TOP3热点
        cursor = conn.execute("""
            SELECT ni.title, p.name, ni.rank 
            FROM news_items ni
            JOIN platforms p ON ni.platform_id = p.id
            WHERE ni.rank <= 3
            ORDER BY ni.rank
            LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            topics = []
            for i, (title, platform, rank) in enumerate(rows, 1):
                topics.append(f"{i:2d}. [{platform}] {title}")
            result = '\n'.join(topics)
            print(f"  ✓ 获取到热点 (来自 {db_files[-1].split('/')[-1]}):\n{result}")
            return result
        else:
            print("  ⚠ 无热点数据，使用备用方案")
            return get_trending_topics_fallback()
    except Exception as e:
        print(f"  ⚠ 热点获取失败: {e}")
        return get_trending_topics_fallback()

def get_trending_topics_fallback():
    """备用方案：读取新闻文件"""
    print("  使用备用方案读取热点...")
    try:
        from mcp_pg_mcp_get_latest_news import get_latest_news
        # 这里简化处理，实际应该调用MCP
        return "AI Agent生态爆发、隐私搜索崛起、AI基础设施投资"
    except:
        return "AI Agent生态爆发、隐私搜索崛起、AI基础设施投资（备用数据）"

def fetch_topic_details(topic):
    """使用Crawl4AI采集热点详情"""
    print(f"[2/3] 采集热点详情: {topic[:30]}...")
    # 实际应该调用Crawl4AI，这里先用模拟
    return f"关于「{topic}」的深度内容：\n- 背景：该话题近期在多个平台引发热议\n- 核心观点：行业专家分析认为这是一个重要趋势\n- 数据支持：相关讨论量增长300%\n- 用户反馈：评论区呈现两极分化"

def generate_content(topic, details, platform="all"):
    """生成多平台适配内容"""
    print(f"[3/3] 生成多平台内容...")
    
    content = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "platforms": {}
    }
    
    # 公众号文章
    content["platforms"]["wechat_mp"] = f"""【公众号文章】

标题：{topic}——你需要知道的5个关键点

正文：
最近，「{topic}」在各大平台引发热议。作为自媒体人，我认为这个趋势值得每个人关注。

{details}

💡 个人观点：这是一个不可逆的趋势，早了解早受益。

👇 你怎么看？欢迎评论区讨论。

#AI #科技趋势 #自媒体
"""
    
    # 小红书笔记
    content["platforms"]["xiaohongshu"] = f"""【小红书笔记】

标题：🔥{topic} | 一文看懂最近最火的话题！

正文：
姐妹们！最近刷到爆的「{topic}」到底是什么？
今天用3分钟给你说明白👇

✨ 核心要点：
1️⃣ 这个话题为什么火？
2️⃣ 对你有什么影响？
3️⃣ 你应该怎么做？

{details[:200]}...

💬 看完有什么想法？评论区告诉我～

#热点解读 #科技资讯 #AI趋势 #涨知识
"""
    
    # 抖音脚本
    content["platforms"]["douyin"] = f"""【抖音口播脚本】

开场（3秒）：
"最近全网都在讨论{topic[:10]}，到底怎么回事？"

正文（30秒）：
"简单说3点：
第一，这个话题为什么突然火了？
第二，它对你有什么影响？
第三，普通人应该怎么应对？

{details[:150]}..."

结尾（5秒）：
"关注我，每天3分钟看懂热点。评论区告诉我你的看法！"
"""
    
    return content

def main():
    """主流程"""
    print("=" * 50)
    print("🚀 自媒体热点内容生成器 v0.1")
    print("=" * 50)
    
    # 1. 获取热点
    topics = get_trending_topics()
    
    # 2. 选择第一个热点进行深度处理
    first_topic = topics.split('\n')[0] if '\n' in topics else topics
    first_topic = first_topic.split('. ', 1)[-1] if '. ' in first_topic else first_topic
    # 清理平台标签
    if ']' in first_topic:
        first_topic = first_topic.split('] ', 1)[-1]
    
    # 3. 采集详情
    details = fetch_topic_details(first_topic)
    
    # 4. 生成内容
    content = generate_content(first_topic, details)
    
    # 5. 保存输出
    output_file = OUTPUT_DIR / f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    # 6. 打印结果
    print(f"\n✅ 内容生成完成！")
    print(f"📁 保存至: {output_file}")
    print(f"\n--- 公众号文章预览 ---")
    print(content["platforms"]["wechat_mp"][:500])
    print(f"\n--- 小红书笔记预览 ---")
    print(content["platforms"]["xiaohongshu"][:500])
    print(f"\n--- 抖音脚本预览 ---")
    print(content["platforms"]["douyin"][:300])
    
    return content

if __name__ == "__main__":
    main()
