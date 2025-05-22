#!/usr/bin/env python3
"""QA-Extractor 主程序"""
import os
import sys
from tqdm import tqdm
from src.config.config_loader import load_config
from src.processors.file_processor import read_file, save_qa_pairs
from src.processors.qa_processor import generate_qa_pairs

def process_files(input_dir: str, output_dir: str, api_url: str) -> None:
    """处理目录中的所有文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        api_url: API地址
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有文件
    files = []
    for root, _, filenames in os.walk(input_dir):
        for filename in filenames:
            if filename.endswith(('.txt', '.docx', '.pdf', '.xls', '.xlsx')):
                files.append(os.path.join(root, filename))
    
    if not files:
        print(f"在 {input_dir} 中没有找到支持的文件")
        return
    
    # 处理每个文件
    for file_path in tqdm(files, desc="处理文件"):
        try:
            # 读取文件
            text = read_file(file_path)
            
            # 计算每个块的问题数量
            total_chunks = len(split_text(text))
            questions_per_chunk = 10 // total_chunks
            remainder = 10 % total_chunks
            
            # 生成问答对
            qa_pairs = []
            for i, chunk in enumerate(tqdm(split_text(text), desc=f"处理 {os.path.basename(file_path)} 的文本块", leave=False)):
                # 为最后一个块分配剩余的问题
                current_questions = questions_per_chunk + (1 if i == total_chunks - 1 and remainder > 0 else 0)
                chunk_qa_pairs = generate_qa_pairs(chunk, api_url, current_questions)
                qa_pairs.extend(chunk_qa_pairs)
            
            # 保存结果
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_qa.csv")
            save_qa_pairs(qa_pairs, output_file)
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            continue

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 获取配置
        input_dir = config['paths']['input_dir']
        output_dir = config['paths']['output_dir']
        api_url = config['api']['url']
        
        # 处理文件
        process_files(input_dir, output_dir, api_url)
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 