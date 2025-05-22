# QA-Extractor

QA-Extractor是一个强大的文档问答对生成工具，能够从各种格式的文档中自动生成高质量的问答对。

## 功能特点

- 支持多种文档格式：
  - 文本文件 (.txt)
  - Word文档 (.docx)
  - PDF文件 (.pdf)
  - Excel文件 (.xls, .xlsx)
- 自动文本分块处理
- 智能问答对生成
- 批量处理功能
- 进度显示
- 错误处理和重试机制
- 失败任务记录

## 项目结构

```
qa_extraction/
├── main.py                 # 主程序入口
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖包列表
└── src/                  # 源代码目录
    ├── __init__.py
    ├── config/           # 配置相关
    │   ├── __init__.py
    │   └── config_loader.py
    ├── processors/       # 处理器
    │   ├── __init__.py
    │   ├── file_processor.py
    │   └── qa_processor.py
    └── utils/           # 工具函数
        ├── __init__.py
        └── text_utils.py
```

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/qa_extraction.git
cd qa_extraction
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

在`config.yaml`中配置以下参数：

```yaml
paths:
  input_dir: "input"    # 输入文件目录
  output_dir: "output"  # 输出文件目录

api:
  url: "http://your-api-url"  # API地址
  timeout: 30                 # 请求超时时间（秒）
  max_retries: 3             # 最大重试次数
  api_key: "your-api-key"    # API密钥（可选）
```

## 使用方法

1. 将需要处理的文档放入`input`目录
2. 运行程序：
```bash
python main.py
```

3. 程序会自动处理所有支持的文件，并在`output`目录生成结果

## 输出格式

- 每个输入文件会生成一个对应的CSV文件，包含以下列：
  - question: 生成的问题
  - answer: 对应的答案

- 如果处理过程中出现错误，会生成一个失败任务清单（Markdown格式），包含：
  - 失败文件列表
  - 错误信息
  - 失败原因统计

## 依赖包

- pandas: 数据处理
- python-docx: Word文档处理
- PyPDF2: PDF文件处理
- xlrd: Excel文件处理
- tqdm: 进度显示
- requests: API请求
- tiktoken: Token计算
- pyyaml: 配置文件处理

## 注意事项

1. 确保输入目录存在并包含支持的文件
2. 确保有足够的磁盘空间存储输出文件
3. 对于大文件，处理时间可能较长
4. 建议定期检查失败任务清单，及时处理失败的文件

## 错误处理

程序包含完善的错误处理机制：
- API请求失败自动重试
- 文件读取错误记录
- JSON解析错误处理
- 详细的错误日志

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License 