import os
import csv
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict
from pathlib import Path

# Ollama API配置
OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"
MODEL_NAME = "deepseek-r1:latest"

def select_file() -> str:
    """打开文件选择对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    file_path = filedialog.askopenfilename(
        title="选择要处理的文档",
        filetypes=[
            ("文本文件", "*.md"),
            ("所有文件", "*.*")
        ]
    )
    
    if not file_path:
        print("未选择文件")
        exit(1)
        
    return file_path

def select_save_location() -> str:
    """打开保存文件对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    file_path = filedialog.asksaveasfilename(
        title="选择保存位置",
        defaultextension=".csv",
        filetypes=[("CSV文件", "*.csv")],
        initialfile="qa_pairs.csv"
    )
    
    if not file_path:
        print("未选择保存位置")
        exit(1)
        
    return file_path

def read_document(file_path: str) -> str:
    """读取文档内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_qa_pairs(document_content: str) -> List[Dict[str, str]]:
    """使用Ollama API生成问答对"""
    
    # 系统提示词
    system_prompt = """你是一个专业的文档分析助手。你的任务是：
    1. 仔细阅读提供的文档内容
    2. 提出10个与文档内容相关的重要问题
    3. 对每个问题，从文档中提取相关信息作为答案
    4. 确保问题和答案都是清晰、准确且相关的
    5. 以JSON格式返回结果，格式为：[{"question": "问题1", "answer": "答案1"}, ...]"""
    
    # 用户提示词
    user_prompt = f"请分析以下文档内容并生成问答对：\n\n{document_content}"
    
    try:
        # 准备请求数据
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        print("正在发送请求到Ollama API...")
        print(f"请求内容: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # 构建curl命令
        curl_command = [
            "curl",
            "-s",  # 静默模式
            "-X", "POST",
            OLLAMA_API_URL,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]
        
        # 执行curl命令
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"curl命令执行状态码: {result.returncode}")
        
        if result.returncode != 0:
            print(f"curl命令执行失败: {result.stderr}")
            return []
            
        # 解析响应
        try:
            response_data = json.loads(result.stdout)
            content = response_data['choices'][0]['message']['content']
            
            print(f"模型返回内容: {content}")
            
            # 从内容中提取JSON部分
            json_start = content.find('```json')
            json_end = content.rfind('```')
            
            if json_start != -1 and json_end != -1:
                json_str = content[json_start + 7:json_end].strip()
                qa_pairs = json.loads(json_str)
            else:
                # 如果没有找到JSON标记，尝试直接解析整个内容
                qa_pairs = json.loads(content)
            
            if not isinstance(qa_pairs, list):
                print("返回的内容不是列表格式")
                return []
                
            print(f"成功解析问答对数量: {len(qa_pairs)}")
            return qa_pairs
            
        except json.JSONDecodeError as e:
            print(f"解析JSON失败: {str(e)}")
            print(f"原始内容: {result.stdout}")
            return []
    
    except subprocess.TimeoutExpired:
        print("请求超时")
        return []
    except Exception as e:
        print(f"生成问答对时发生错误: {str(e)}")
        return []

def save_to_csv(qa_pairs: List[Dict[str, str]], output_path: str):
    """将问答对保存为CSV文件"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question', 'answer'])
        writer.writeheader()
        writer.writerows(qa_pairs)

def process_document(input_file: str, output_file: str):
    """处理文档的主函数"""
    try:
        # 读取文档
        document_content = read_document(input_file)[:500]
        
        # 生成问答对
        qa_pairs = generate_qa_pairs(document_content)
        
        if not qa_pairs:
            print("未能生成问答对")
            return
        
        # 保存为CSV
        save_to_csv(qa_pairs, output_file)
        print(f"处理完成！结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"处理文档时发生错误: {str(e)}")

if __name__ == "__main__":
    print("请选择要处理的文档...")
    input_file = select_file()
    
    print("请选择保存位置...")
    output_file = select_save_location()
    
    # 处理文档
    process_document(input_file, output_file) 