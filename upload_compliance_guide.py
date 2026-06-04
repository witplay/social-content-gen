#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传微短剧合规指南文章到微信公众号草稿箱
独立脚本，复用 wechat-mp-story 的 token 和 draft 模块
"""

import os
import sys
import json
import time
import re
import requests
from pathlib import Path

# 添加 wechat-mp-story 工具模块路径
sys.path.insert(0, '/root/.hermes/profiles/xiaoxiao/skills/devops/wechat-mp-story/tools')
from wechat_token import WechatTokenManager
from wechat_media import WechatMediaManager
from wechat_draft import WechatDraftManager

# 加载配置
sys.path.insert(0, '/root/.hermes/profiles/xiaoxiao/skills/devops/wechat-mp-story')
from config import load_config

config = load_config()

# 确保 AppSecret 从环境变量读取（优先）
app_secret = os.environ.get('WECHAT_MP_APPSECRET', '')
if app_secret:
    config.wechat_mp.app_secret = app_secret

# Markdown 转简易 HTML
def md_to_html(md_text: str) -> str:
    lines = md_text.strip().split('\n')
    html_parts = []
    in_list = False
    
    for line in lines:
        line = line.rstrip()
        if not line.strip():
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            continue
        
        # 水平线
        if line.strip() == '---':
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append('<hr>')
            continue
        
        # 标题
        if line.startswith('**标题：'):
            title_match = re.match(r'\*\*标题：(.+?)\*\*', line)
            if title_match:
                html_parts.append(f'<h1 style="font-size:24px;color:#333;margin:20px 0 10px 0;">{title_match.group(1)}</h1>')
            continue
        
        if line.startswith('### '):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            title = line[4:]
            html_parts.append(f'<h2 style="font-size:18px;color:#1a73e8;margin:24px 0 12px 0;border-left:4px solid #1a73e8;padding-left:12px;">{title}</h2>')
            continue
        
        if line.startswith('## '):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            title = line[3:]
            html_parts.append(f'<h2 style="font-size:20px;color:#333;margin:20px 0 10px 0;">{title}</h2>')
            continue
        
        # 加粗文字
        if line.startswith('**') and line.endswith('**'):
            text = line[2:-2]
            html_parts.append(f'<p style="font-weight:bold;color:#333;margin:12px 0;">{text}</p>')
            continue
        
        # 普通段落
        # 处理行内加粗
        processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        html_parts.append(f'<p style="margin:8px 0;line-height:1.8;font-size:16px;color:#333;">{processed}</p>')
    
    if in_list:
        html_parts.append('</ul>')
    
    return '\n'.join(html_parts)

def main():
    print("=" * 50)
    print("微短剧合规指南 → 微信公众号草稿上传")
    print("=" * 50)
    
    # 读取优化后的文章
    article_path = '/root/.hermes/profiles/long/monetization/social-content-gen/output/p02_wechat_v2.md'
    with open(article_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 提取标题
    title_match = re.search(r'\*\*标题：(.+?)\*\*', md_content)
    title = title_match.group(1) if title_match else '微短剧合规指南'
    print(f"\n📝 标题: {title}")
    
    # 转换 HTML
    html_content = md_to_html(md_content)
    print(f"📄 HTML 长度: {len(html_content)} 字符")
    
    # 初始化微信模块
    token_manager = WechatTokenManager(config)
    media_manager = WechatMediaManager(config, token_manager)
    draft_manager = WechatDraftManager(config, token_manager)
    
    # 上传封面图（使用一个简单图片，这里先尝试用 MCP 生成或直接上传）
    print("\n🖼️ 正在上传封面图...")
    
    # 尝试用现有图片或生成一个简单封面
    cover_path = '/tmp/hermes-generated/covers/weiju_compliance_cover.jpg'
    
    # 如果没有封面图，先尝试生成一个
    if not os.path.exists(cover_path):
        os.makedirs(os.path.dirname(cover_path), exist_ok=True)
        print("  封面图不存在，尝试使用默认图片...")
        # 先尝试从已有输出中找图片
        for root, dirs, files in os.walk('/www/wwwroot/hermes/story/output/'):
            for f in files:
                if f.endswith(('.jpg', '.png')):
                    cover_path = os.path.join(root, f)
                    print(f"  找到图片: {cover_path}")
                    break
            if os.path.exists(cover_path) and os.path.exists(os.path.dirname(cover_path)):
                break
    
    thumb_media_id = None
    
    # 上传封面图到微信获取 media_id
    if os.path.exists(cover_path):
        try:
            print(f"  上传封面图: {cover_path}")
            cover_result = media_manager.upload_image(cover_path, 'thumb')
            thumb_media_id = cover_result.get('media_id')
            print(f"  ✓ 封面图上传成功, media_id: {thumb_media_id}")
        except Exception as e:
            print(f"  ✗ 封面图上传失败: {e}")
            print("  尝试使用永久素材上传...")
            try:
                # 尝试上传为永久素材
                cover_result = media_manager.upload_permanent_image(cover_path)
                thumb_media_id = cover_result.get('media_id')
                print(f"  ✓ 永久素材上传成功, media_id: {thumb_media_id}")
            except Exception as e2:
                print(f"  ✗ 永久素材上传也失败: {e2}")
                thumb_media_id = None
    
    if not thumb_media_id:
        # 如果所有上传都失败，需要用户手动提供 thumb_media_id
        print("\n⚠️ 封面图上传失败，无法自动获取 thumb_media_id")
        print("请手动操作：")
        print("1. 在公众号后台上传一张封面图")
        print("2. 获取该图片的 media_id")
        print("3. 设置环境变量: export THUMB_MEDIA_ID='你的media_id'")
        print("4. 重新运行此脚本")
        
        # 尝试从环境变量获取
        thumb_media_id = os.environ.get('THUMB_MEDIA_ID', '')
        if thumb_media_id:
            print(f"  ✓ 从环境变量获取到 thumb_media_id: {thumb_media_id}")
        else:
            print("\n❌ 无法继续，请提供 thumb_media_id")
            return
    
    # 创建草稿
    print(f"\n📤 正在创建草稿...")
    try:
        result = draft_manager.create_draft(
            title=title,
            html_content=html_content,
            thumb_media_id=thumb_media_id,
            author="新梅阅读",
            digest="广电总局专项治理微短剧，行业迎来合规洗牌。解读政策要点，分析行业趋势。"
        )
        
        if result.get('media_id'):
            print(f"\n✅ 草稿创建成功！")
            print(f"   草稿ID (media_id): {result['media_id']}")
            print(f"   标题: {result['title']}")
            print(f"\n请登录公众号后台查看和编辑：https://mp.weixin.qq.com")
        else:
            print(f"\n❌ 草稿创建失败: {result}")
            
    except Exception as e:
        print(f"\n❌ 草稿创建异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
