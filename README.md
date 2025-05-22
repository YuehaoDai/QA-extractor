# QA-Extractor

QA-Extractor 是一个强大的文档问答对生成工具，它能够从各种格式的文档中自动提取关键信息并生成高质量的问答对。该工具使用大语言模型（LLM）来理解文档内容并生成相关的问答对。

## 功能特点

- 支持多种文档格式：
  - 文本文件 (.txt)
  - Word文档 (.docx)
  - PDF文件 (.pdf)
  - Excel文件 (.xls, .xlsx)
- 自动文本分块处理
- 智能问答对生成
- 批量处理多个文件
- 进度条显示处理进度
- 自动清理Excel不兼容字符
- 详细的错误处理和日志记录

## 项目结构

```
QA-Extractor/
├── main.py                 # 主程序入口
├── config.yaml            # 配置文件
├── requirements.txt       # 项目依赖
├── README.md             # 项目文档
├── LICENSE               # MIT许可证
├── .gitignore           # Git忽略配置
├── input/               # 输入文件目录（需要创建）
├── output/              # 输出文件目录（自动创建）
└── src/                 # 源代码目录
    ├── __init__.py
    ├── config/          # 配置相关
    │   ├── __init__.py
    │   └── config_loader.py  # 配置加载模块
    ├── processors/      # 处理器模块
    │   ├── __init__.py
    │   ├── file_processor.py  # 文件处理模块
    │   └── qa_processor.py    # 问答处理模块
    └── utils/           # 工具函数
        ├── __init__.py
        └── text_utils.py      # 文本处理工具
```

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/qa-extractor.git
cd qa-extractor
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 创建配置文件 `config.yaml`：
```yaml
api:
  url: "http://your-api-endpoint"  # 替换为实际的API地址

paths:
  input_dir: "input"    # 输入文件目录
  output_dir: "output"  # 输出文件目录
```

2. 创建输入目录：
```bash
mkdir input
```

## 使用方法

1. 将需要处理的文档放入 `input` 目录

2. 运行程序：
```bash
python main.py
```

3. 处理完成后，问答对将保存在 `output` 目录中，每个输入文件对应一个CSV文件

## 输出格式

程序会为每个输入文件生成一个对应的CSV文件，包含以下列：
- question: 生成的问题
- answer: 对应的答案

## 注意事项

- 确保API地址配置正确
- 输入文件必须是支持的格式之一
- 每个文档最多生成10个问答对
- 大文件会自动分块处理
- 输出文件使用UTF-8编码，支持Excel打开

## 依赖项

- pandas>=1.5.0
- python-docx>=0.8.11
- PyPDF2>=3.0.0
- xlrd>=2.0.1
- openpyxl>=3.1.0
- tiktoken>=0.5.0
- tqdm>=4.65.0
- pyyaml>=6.0
- requests>=2.31.0

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件 