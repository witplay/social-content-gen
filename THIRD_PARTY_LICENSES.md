# 第三方组件版权与许可证声明

## 本项目使用的第三方组件

### 1. TrendRadar (数据源)
- **项目**: https://github.com/sansan0/TrendRadar
- **许可证**: GPL-3.0
- **使用方式**: 仅读取其输出的SQLite数据库文件
- **合规说明**: 
  - 本项目**不嵌入**TrendRadar的任何代码
  - 仅读取TrendRadar独立运行后生成的**数据文件**（news/*.db）
  - 数据内容本身不受GPL许可证约束
  - 用户需自行安装并运行TrendRadar（遵循其GPL-3.0许可证）

### 2. Python标准库
- sqlite3, os, sys, json, pathlib, unittest, tempfile
- **许可证**: Python Software Foundation License (兼容MIT)

### 3. 第三方Python库
| 库名 | 许可证 | 用途 |
|------|--------|------|
| requests | Apache-2.0 | HTTP请求 |
| pyyaml | MIT | 配置文件解析 |
| rich | MIT | 终端输出美化 |
| click | BSD-3-Clause | CLI框架 |
| jinja2 | BSD-3-Clause | 模板引擎 |
| markdown | BSD-3-Clause | Markdown处理 |

## 本项目的许可证

本项目（social-content-gen）采用 **MIT License**，详见 `LICENSE` 文件。

## 用户合规责任

1. **TrendRadar**: 用户需自行安装TrendRadar并遵守其GPL-3.0许可证
2. **LLM API**: 用户需确保使用的LLM API有合法授权
3. **内容发布**: 用户需确保生成的内容不侵犯第三方版权
4. **平台规则**: 用户需遵守各内容平台的使用条款

## 免责声明

本项目仅提供技术工具，不对用户使用本工具生成的内容及其发布行为承担任何法律责任。用户使用本工具时，应自行确保其行为符合相关法律法规和平台规则。
