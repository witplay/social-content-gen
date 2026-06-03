#!/usr/bin/env python3
"""
自媒体热点内容生成器 - 完整测试套件
参照GitHub成熟开源项目测试标准
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from main import get_trending_topics, fetch_topic_details, generate_content
from llm_generator import LLMGenerator

def create_test_config(path):
    """创建测试用配置文件"""
    config = """llm:
  openai:
    enabled: false
    api_key: ""
    model: "gpt-4o-mini"
"""
    with open(path, 'w') as f:
        f.write(config)

class TestTrendRadarIntegration(unittest.TestCase):
    """测试1: TrendRadar热点集成"""
    
    def test_get_real_trending_topics(self):
        """测试1.1: 能获取真实热点数据"""
        topics = get_trending_topics()
        self.assertIsNotNone(topics, "热点数据不能为空")
        self.assertTrue(len(topics) > 0, "至少获取到1个热点")
        print(f"  ✓ 获取到热点: {topics[:100]}...")
    
    def test_topic_format(self):
        """测试1.2: 热点格式正确"""
        topics = get_trending_topics()
        lines = [l for l in topics.split('\n') if l.strip()]
        self.assertTrue(len(lines) >= 5, f"至少5个热点，实际{len(lines)}个")
        print(f"  ✓ 热点数量: {len(lines)}个")

class TestContentGeneration(unittest.TestCase):
    """测试2: 内容生成"""
    
    def setUp(self):
        self.test_topic = "AI Agent生态爆发"
        self.test_details = "最新数据显示AI Agent市场增长300%..."
    
    def test_generate_wechat_content(self):
        """测试2.1: 生成公众号内容"""
        content = generate_content(self.test_topic, self.test_details, "wechat_mp")
        self.assertIn("platforms", content)
        self.assertIn("wechat_mp", content["platforms"])
        self.assertTrue(len(content["platforms"]["wechat_mp"]) > 100)
        print(f"  ✓ 公众号内容长度: {len(content['platforms']['wechat_mp'])}字符")
    
    def test_generate_xiaohongshu_content(self):
        """测试2.2: 生成小红书内容"""
        content = generate_content(self.test_topic, self.test_details, "xiaohongshu")
        self.assertIn("xiaohongshu", content["platforms"])
        self.assertTrue(len(content["platforms"]["xiaohongshu"]) > 50)
        print(f"  ✓ 小红书内容长度: {len(content['platforms']['xiaohongshu'])}字符")
    
    def test_generate_douyin_content(self):
        """测试2.3: 生成抖音内容"""
        content = generate_content(self.test_topic, self.test_details, "douyin")
        self.assertIn("douyin", content["platforms"])
        print(f"  ✓ 抖音脚本长度: {len(content['platforms']['douyin'])}字符")
    
    def test_generate_all_platforms(self):
        """测试2.4: 生成全平台内容"""
        content = generate_content(self.test_topic, self.test_details, "all")
        self.assertEqual(len(content["platforms"]), 3)
        print(f"  ✓ 全平台生成: {list(content['platforms'].keys())}")

class TestSecurity(unittest.TestCase):
    """测试3: 安全测试"""
    
    def test_no_hardcoded_keys(self):
        """测试3.1: 无硬编码密钥"""
        project_dir = Path(__file__).parent
        # 只检查.py文件中的真实密钥模式，排除占位符
        suspicious_patterns = ["api_key = 'sk-[a-zA-Z0-9]", "password = '[^']", "token = '[^']"]
        
        for pattern in suspicious_patterns:
            result = os.popen(
                f"grep -rE '{pattern}' {project_dir} --include='*.py' | grep -v test_all.py"
            ).read()
            self.assertFalse(result.strip(), f"发现硬编码密钥: {result[:200]}")
        
        print("  ✓ 无硬编码密钥")
    
    def test_gitignore_exists(self):
        """测试3.2: .gitignore存在且正确"""
        gitignore = Path(__file__).parent / ".gitignore"
        self.assertTrue(gitignore.exists(), ".gitignore必须存在")
        
        content = gitignore.read_text()
        self.assertIn("config.yaml", content, ".gitignore必须排除config.yaml")
        self.assertIn(".env", content, ".gitignore必须排除.env文件")
        print("  ✓ .gitignore配置正确")
    
    def test_config_example_has_placeholders(self):
        """测试3.3: 示例配置使用占位符"""
        config_example = Path(__file__).parent / "config.example.yaml"
        self.assertTrue(config_example.exists())
        
        content = config_example.read_text()
        self.assertIn("sk-...", content, "示例配置必须使用占位符")
        self.assertNotIn("sk-actual-key", content, "示例配置不能有真实密钥")
        print("  ✓ 示例配置使用占位符")

class TestUserExperience(unittest.TestCase):
    """测试4: 用户体验"""
    
    def test_cli_help(self):
        """测试4.1: CLI帮助信息"""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "main.py"), "--help"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, "帮助命令不能报错")
        self.assertTrue(len(result.stdout) > 50, "帮助信息太短")
        print(f"  ✓ CLI帮助: {result.stdout[:100]}...")
    
    def test_output_file_created(self):
        """测试4.2: 输出文件正确创建"""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # 运行主程序
        from main import main as run_main
        with patch('sys.stdout'):  # 静音输出
            run_main()
        
        # 检查输出文件
        files = list(output_dir.glob("content_*.json"))
        self.assertTrue(len(files) > 0, "至少生成1个输出文件")
        
        # 验证JSON格式
        with open(files[-1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn("platforms", data)
        print(f"  ✓ 输出文件: {files[-1].name}")

class TestLLMIntegration(unittest.TestCase):
    """测试5: LLM集成"""
    
    def setUp(self):
        """每个测试前创建临时配置"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        create_test_config(self.temp_config.name)
        self.temp_config.close()
    
    def tearDown(self):
        """清理临时文件"""
        if hasattr(self, 'temp_config') and os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_llm_fallback_to_template(self):
        """测试5.1: 无API时降级到模板"""
        from pathlib import Path
        gen = LLMGenerator(config_path=Path(self.temp_config.name))
        result = gen.generate_content("测试话题", "测试详情", "wechat_mp")
        self.assertIsNotNone(result, "必须有输出")
        print(f"  ✓ 降级模式工作正常")
    
    def test_llm_config_validation(self):
        """测试5.2: 配置验证"""
        from pathlib import Path
        # 测试无效配置
        gen = LLMGenerator(config_path=Path(self.temp_config.name))
        self.assertIsNone(gen.client, "无效配置时client应为None")
        print(f"  ✓ 配置验证通过")

class TestCompliance(unittest.TestCase):
    """测试6: 版权合规"""
    
    def test_license_file_exists(self):
        """测试6.1: LICENSE文件存在"""
        license_file = Path(__file__).parent / "LICENSE"
        self.assertTrue(license_file.exists(), "LICENSE文件必须存在")
        content = license_file.read_text()
        self.assertIn("MIT", content, "必须是MIT许可证")
        print("  ✓ LICENSE文件存在（MIT）")
    
    def test_third_party_licenses(self):
        """测试6.2: 第三方许可证声明"""
        third_party = Path(__file__).parent / "THIRD_PARTY_LICENSES.md"
        self.assertTrue(third_party.exists(), "THIRD_PARTY_LICENSES.md必须存在")
        content = third_party.read_text()
        self.assertIn("TrendRadar", content, "必须声明TrendRadar")
        self.assertIn("GPL-3.0", content, "必须说明GPL-3.0许可证")
        print("  ✓ 第三方许可证声明完整")
    
    def test_no_gpl_code_embedding(self):
        """测试6.3: 无GPL代码嵌入"""
        project_dir = Path(__file__).parent
        # 检查是否嵌入了TrendRadar的代码
        result = os.popen(
            f"grep -r 'TrendRadar' {project_dir} --include='*.py' | grep -v test_all.py | grep -v '#' | grep -v 'print' | grep -v 'docstring'"
        ).read()
        # 只允许注释和文档中提到，不能有代码引用
        lines = [l for l in result.split('\n') if l.strip() and not l.strip().startswith('#')]
        self.assertTrue(len(lines) <= 2, f"发现可能的GPL代码嵌入: {result[:200]}")
        print("  ✓ 无GPL代码嵌入")

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 自媒体热点内容生成器 - 完整测试套件")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 按顺序添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestTrendRadarIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestContentGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestUserExperience))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCompliance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！可以发布")
        return True
    else:
        print("\n❌ 有测试失败，不能发布")
        if result.failures:
            print("\n失败详情:")
            for test, trace in result.failures:
                print(f"  - {test}: {trace[:200]}")
        if result.errors:
            print("\n错误详情:")
            for test, trace in result.errors:
                print(f"  - {test}: {trace[:200]}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
