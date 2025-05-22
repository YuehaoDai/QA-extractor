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
git clone [repository_url]
cd qa_extraction
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
   - 复制 `config/config.yaml.example` 为 `config/config.yaml`
   - 修改配置文件中的相关参数

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

## 配置说明

配置文件 `config/config.yaml` 包含以下主要部分：

- `paths`: 输入输出路径配置
- `llm`: LLM API配置
- `processing`: 文本处理参数
- `prompts`: 提示词模板

## 项目结构

```
qa_extraction/
├── config/
│   ├── config.yaml
│   └── config.yaml.example
├── src/
│   ├── config/
│   ├── processors/
│   └── utils/
├── input/
├── output/
├── main.py
├── requirements.txt
└── README.md
```

## 错误处理

程序会自动处理以下情况：
- API请求失败
- 文件读取错误
- JSON解析错误
- 其他异常情况

所有失败的任务都会生成详细的报告，包括：
- 失败原因
- 错误信息
- 模型响应（如果有）

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[添加许可证信息]

## 联系方式

[添加联系方式] 