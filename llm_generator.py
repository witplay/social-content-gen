#!/usr/bin/env python3
"""
LLM内容生成模块 - 安全版
密钥只从本地 config.yaml 读取，绝不硬编码或输出到日志
"""

import os
import yaml
from pathlib import Path

class LLMGenerator:
    """安全的LLM内容生成器"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config = self._load_config(config_path)
        self.client = None
        self._init_client()
    
    def _load_config(self, config_path):
        """加载本地配置"""
        if not config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {config_path}\n"
                f"请复制 config.example.yaml 为 config.yaml 并填写配置"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_client(self):
        """初始化LLM客户端（安全读取密钥）"""
        llm_config = self.config.get('llm', {})
        
        # 优先使用OpenAI
        if llm_config.get('openai', {}).get('enabled'):
            try:
                from openai import OpenAI
                api_key = llm_config['openai'].get('api_key', '')
                if not api_key or api_key == 'sk-...':
                    print("  ⚠ OpenAI API Key未配置，使用模板生成模式")
                    return
                
                base_url = llm_config['openai'].get('base_url') or None
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                self.model = llm_config['openai'].get('model', 'gpt-4o-mini')
                print(f"  ✓ OpenAI客户端初始化成功 (模型: {self.model})")
            except ImportError:
                print("  ⚠ 未安装openai库: pip install openai")
            except Exception as e:
                print(f"  ⚠ OpenAI初始化失败: {type(e).__name__}")
        
        # 备用：千问
        elif llm_config.get('qwen', {}).get('enabled'):
            try:
                from openai import OpenAI  # 千问兼容OpenAI接口
                api_key = llm_config['qwen'].get('api_key', '')
                if not api_key or api_key == 'sk-...':
                    print("  ⚠ 千问API Key未配置，使用模板生成模式")
                    return
                
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
                self.model = llm_config['qwen'].get('model', 'qwen-plus')
                print(f"  ✓ 千问客户端初始化成功 (模型: {self.model})")
            except Exception as e:
                print(f"  ⚠ 千问初始化失败: {type(e).__name__}")
        
        # 本地模型
        elif llm_config.get('local', {}).get('enabled'):
            try:
                from openai import OpenAI
                base_url = llm_config['local'].get('base_url', '')
                if not base_url:
                    print("  ⚠ 本地模型base_url未配置")
                    return
                
                self.client = OpenAI(
                    api_key=llm_config['local'].get('api_key') or "local",
                    base_url=base_url
                )
                self.model = llm_config['local'].get('model', 'qwen2.5-72b')
                print(f"  ✓ 本地模型客户端初始化成功 (模型: {self.model})")
            except Exception as e:
                print(f"  ⚠ 本地模型初始化失败: {type(e).__name__}")
        else:
            print("  ℹ 未启用任何LLM，使用模板生成模式")
    
    def generate_content(self, topic, details, platform="all", style="professional"):
        """生成内容（LLM或模板）"""
        if self.client:
            return self._generate_with_llm(topic, details, platform, style)
        else:
            return self._generate_with_template(topic, details, platform)
    
    def _generate_with_llm(self, topic, details, platform, style):
        """使用LLM生成高质量内容"""
        prompt = self._build_prompt(topic, details, platform, style)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            print(f"  ✓ LLM生成成功 ({len(content)}字符)")
            return content
        except Exception as e:
            print(f"  ⚠ LLM生成失败: {type(e).__name__}，降级到模板模式")
            return self._generate_with_template(topic, details, platform)
    
    def _generate_with_template(self, topic, details, platform="all"):
        """模板生成（备用方案）"""
        # 这里复用之前的模板逻辑
        content = {
            "topic": topic,
            "mode": "template",
            "platforms": {}
        }
        
        if platform in ["all", "wechat_mp"]:
            content["platforms"]["wechat_mp"] = f"""【公众号文章】
标题：{topic}——你需要知道的5个关键点
正文：最近，「{topic}」引发热议...
"""
        
        if platform in ["all", "xiaohongshu"]:
            content["platforms"]["xiaohongshu"] = f"""【小红书笔记】
标题：🔥{topic} | 一文看懂！
正文：姐妹们！最近刷到爆的「{topic}」...
"""
        
        if platform in ["all", "douyin"]:
            content["platforms"]["douyin"] = f"""【抖音脚本】
开场："{topic[:10]}，到底怎么回事？"
正文：简单说3点...
"""
        
        return content
    
    def _build_prompt(self, topic, details, platform, style):
        """构建LLM提示词"""
        platform_prompts = {
            "wechat_mp": "写一篇公众号文章，800-1200字，专业风格，包含标题、正文、个人观点",
            "xiaohongshu": "写一篇小红书笔记，300-500字，活泼风格，使用emoji，包含标题和标签",
            "douyin": "写一个抖音口播脚本，60秒内，口语化，包含开场、正文、结尾"
        }
        
        prompt = f"""
你是一个专业的自媒体内容创作者。请根据以下热点话题生成内容：

话题：{topic}
背景信息：{details}
平台要求：{platform_prompts.get(platform, platform_prompts['wechat_mp'])}
风格：{style}

要求：
1. 标题要吸引人，有点击欲
2. 内容要有价值，不是泛泛而谈
3. 结尾要有互动，引导评论
4. 不要使用AI味重的表达

只输出内容，不要解释。
"""
        return prompt


if __name__ == "__main__":
    # 测试
    print("测试LLM生成器...")
    try:
        gen = LLMGenerator()
        result = gen.generate_content("AI Agent生态爆发", "最新数据显示...", "wechat_mp")
        print(result)
    except Exception as e:
        print(f"测试失败: {e}")
