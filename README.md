# QA-Extractor

QA-Extractor 是一个基于大语言模型的文档问答对提取工具，能够自动从各类文档中提取高质量的问答对。

## 功能特性

- 支持多种文档格式（PDF、Word、Markdown等）
- 自动分块处理长文本
- 智能生成问答对
- 支持批量处理多个文件
- 自动重试和错误处理
- 生成详细的失败任务报告
- 支持自定义配置
- 详细的日志输出和调试信息

## 系统要求

- Python 3.8+
- 依赖包：
  - pandas
  - tqdm
  - requests
  - openpyxl
  - python-docx
  - PyPDF2
  - markdown

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/YuehaoDai/QA-extractor.git
cd qa_extraction
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
   - 复制 `config/config.yaml.example` 为 `config/config.yaml`
   - 修改配置文件中的相关参数，特别是 LLM API 的配置

## 使用方法

1. 准备输入文件：
   - 将需要处理的文档放入 `input` 目录
   - 支持的文件格式：PDF、Word、Markdown等

2. 运行程序：
```bash
python main.py
```

3. 查看结果：
   - 生成的问答对将保存在 `output` 目录
   - 失败的任务将生成详细的报告（Markdown和Excel格式）
   - 控制台会输出详细的处理日志

## 配置说明

配置文件 `config/config.yaml` 包含以下主要部分：

- `paths`: 输入输出路径配置
  - `input_dir`: 输入文件目录
  - `output_dir`: 输出文件目录
- `llm`: LLM API配置
  - `api_url`: API地址
  - `model_name`: 模型名称
  - `api_key`: API密钥（可选）
  - `timeout`: 请求超时时间
  - `max_retries`: 最大重试次数
- `processing`: 文本处理参数
  - `supported_extensions`: 支持的文件扩展名
  - `questions_per_file`: 每个文件生成的问题数量
- `prompts`: 提示词模板
  - `system_prompt_template`: 系统提示词模板
  - `user_prompt_template`: 用户提示词模板

## 项目结构

```
qa_extraction/
├── config/
│   ├── config.yaml          # 配置文件
│   └── config.yaml.example  # 配置示例文件
├── src/
│   ├── config/             # 配置加载模块
│   │   └── config_loader.py
│   ├── processors/         # 文件处理模块
│   │   └── file_processor.py
│   └── utils/             # 工具函数
│       └── text_utils.py
├── input/                 # 输入文件目录
├── output/               # 输出文件目录
├── main.py              # 主程序
├── requirements.txt     # 依赖包列表
└── README.md           # 项目说明文档
```

## 错误处理

程序会自动处理以下情况：
- API请求失败（包括超时、连接错误等）
- 文件读取错误
- JSON解析错误
- 问答对格式验证错误
- 其他异常情况

所有失败的任务都会生成详细的报告，包括：
- 失败原因
- 错误信息
- 模型响应（如果有）
- 错误类型统计

## 日志输出

程序会输出详细的处理日志，包括：
- API配置信息
- 文件处理进度
- 请求和响应信息
- 错误和重试信息
- 处理结果统计

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- GitHub: [YuehaoDai](https://github.com/YuehaoDai)
- Email: [添加邮箱地址] 