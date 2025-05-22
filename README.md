# QA-Extractor

一个基于大语言模型（LLM）的智能文档问答对生成工具。通过调用大模型API，能够深入理解文档内容，自动生成高质量的问答对。支持多种文档格式，能够从文档中提取关键信息并生成符合上下文的问答对。

## 功能特点

- 基于大语言模型（如GPT-3.5/4）的智能问答生成
- 支持多种文档格式：PDF、Word、Excel、Markdown
- 自动文本分割，处理长文档
- 智能问答对生成，确保问题和答案的准确性和相关性
- 支持批量处理多个文件
- 自动保存为CSV和Excel格式
- 详细的错误处理和日志记录
- 智能的token管理和优化
- 支持自定义提示词，优化问答生成效果

## 环境要求

- Python 3.7+
- 依赖包：
  - pandas
  - python-docx
  - PyPDF2
  - xlrd
  - openpyxl
  - tiktoken
  - tqdm
  - pyyaml
  - requests

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/YuehaoDai/QA-extractor.git
cd QA-extractor
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
- 复制 `config.yaml.example` 为 `config.yaml`
- 在 `config.yaml` 中配置您的API密钥和其他设置

## 使用方法

1. 将需要处理的文档放入 `input` 目录
2. 运行脚本：
```bash
python batch_qa_extraction.py
```
3. 处理结果将保存在 `output` 目录中

## 函数说明

### 核心功能函数

#### `load_config() -> dict`
- 功能：加载配置文件
- 说明：从 `config.yaml` 读取配置信息，包括API设置、路径配置等

#### `count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int`
- 功能：计算文本的token数量
- 说明：使用tiktoken库计算文本的token数，如果tiktoken不可用则使用估算方法

#### `split_text(text: str, max_tokens: int = 24000) -> List[str]`
- 功能：将长文本分割成不超过最大token数的片段
- 说明：
  - 考虑系统提示词和用户提示词的token数
  - 智能分配token使用：
    - 系统提示词：约200 tokens
    - 用户提示词前缀：约50 tokens
    - 文档内容：约20000 tokens
    - 模型回答：约8000 tokens
    - 余量：约1750 tokens

#### `generate_qa_pairs(document_content: str, llm_client: LLMClient) -> Tuple[List[Dict[str, str]], Optional[str]]`
- 功能：使用LLM API生成问答对
- 说明：
  - 发送文档内容到LLM API
  - 解析返回的JSON格式问答对
  - 支持多种格式的响应解析
  - 包含token使用监控

### 文件处理函数

#### `get_input_files() -> List[str]`
- 功能：获取输入目录下的所有支持的文件
- 说明：递归搜索input目录及其子目录，返回所有支持格式的文件路径

#### `get_output_path() -> str`
- 功能：获取输出文件路径
- 说明：根据配置生成带时间戳的输出文件路径

#### `extract_title(file_path: str) -> str`
- 功能：从文件中提取标题
- 说明：支持从不同格式的文件中智能提取标题

#### `read_document(file_path: str) -> str`
- 功能：读取文档内容
- 说明：支持读取多种格式的文档并转换为文本

#### `clean_for_excel(text) -> str`
- 功能：清理Excel中不允许的字符
- 说明：处理特殊字符和控制字符，确保Excel兼容性

### 错误处理函数

#### `save_failed_tasks(failed_files: List[Tuple[str, str, str]], output_dir: str)`
- 功能：保存失败任务清单
- 说明：
  - 生成详细的失败报告
  - 包含错误信息和模型响应
  - 统计失败原因

### 主处理函数

#### `process_files(input_files: List[str], output_file: str)`
- 功能：处理多个文件的主函数
- 说明：
  - 批量处理文件
  - 生成进度条显示
  - 保存处理结果
  - 错误处理和日志记录

## 配置说明

在 `config.yaml` 中可以配置以下内容：

```yaml
llm:
  api_url: "API地址"  # 支持OpenAI API或其他兼容的LLM API
  model_name: "模型名称"  # 如 gpt-3.5-turbo, gpt-4 等
  api_key: "API密钥"
  timeout: 超时时间
  max_retries: 最大重试次数
  temperature: 温度参数  # 控制生成结果的创造性

paths:
  input_dir: "输入目录"
  output_dir: "输出目录"

processing:
  supported_extensions: [".pdf", ".docx", ".xlsx", ".md"]

output:
  csv_filename_template: "qa_pairs_{timestamp}.csv"
  excel_filename_template: "qa_pairs_{timestamp}.xlsx"
```

## 大模型使用说明

本项目使用大语言模型（LLM）来生成高质量的问答对。主要特点：

1. 智能理解：模型能够深入理解文档内容，提取关键信息
2. 上下文感知：生成的问答对保持文档的上下文连贯性
3. 高质量输出：问题和答案都经过模型优化，确保准确性和可读性
4. 灵活配置：支持不同的模型和参数配置，适应不同场景需求

### 提示词优化

系统使用精心设计的提示词来引导模型生成高质量的问答对：

```python
system_prompt = """你是一个专业的文档分析助手。你的任务是：
1. 仔细阅读提供的文档内容
2. 提出10个与文档内容相关的重要问题
3. 对每个问题，从文档中提取相关信息作为答案
4. 确保问题和答案都是清晰、准确且相关的
5. 以JSON格式返回结果，格式为：[{"question": "问题1", "answer": "答案1"}, ...]
6. 只返回JSON格式的数据，不要包含任何其他内容"""
```

## 输出格式

### CSV/Excel文件包含以下列：
- filename: 源文件名
- chunk_index: 文本块序号
- question: 生成的问题
- answer: 对应的答案

### 失败任务报告包含：
- 失败文件列表
- 错误信息
- 模型返回内容
- 失败原因统计

## 注意事项

1. 确保API密钥配置正确
2. 检查输入文件格式是否支持
3. 注意token使用限制
4. 定期检查输出目录空间

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License 