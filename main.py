#!/usr/bin/env python3
"""QA-Extractor 主程序"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from tqdm import tqdm
import pandas as pd
from src.config.config_loader import load_config
from src.processors.file_processor import read_file, save_qa_pairs
from src.processors.qa_processor import generate_qa_pairs
from src.utils.text_utils import split_text

class LLMClient:
    """LLM API客户端"""
    def __init__(self, config: dict):
        self.api_url = config['api_url']
        self.model_name = config['model_name']
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        
        # 设置请求头
        self.headers = {
            "Content-Type": "application/json"
        }
        if 'api_key' in config and config['api_key']:
            self.headers["Authorization"] = f"Bearer {config['api_key']}"
        
        # 打印配置信息（调试用）
        print(f"\nAPI配置信息:")
        print(f"- API地址: {self.api_url}")
        print(f"- 模型名称: {self.model_name}")
        print(f"- 超时时间: {self.timeout}秒")
        print(f"- 最大重试次数: {self.max_retries}")
        print(f"- 是否使用API密钥: {'是' if 'api_key' in config and config['api_key'] else '否'}\n")
    
    def generate_response(self, messages: list) -> tuple:
        """生成响应
        
        Args:
            messages: 消息列表
            
        Returns:
            tuple: (响应内容, 错误信息)
        """
        for attempt in range(self.max_retries):
            try:
                # 添加重试延迟
                if attempt > 0:
                    delay = min(2 ** attempt, 30)  # 指数退避，最大30秒
                    print(f"第 {attempt + 1} 次重试，等待 {delay} 秒...")
                    time.sleep(delay)
                
                # 打印请求信息（调试用）
                print(f"\n发送API请求:")
                print(f"- URL: {self.api_url}")
                print(f"- 模型: {self.model_name}")
                print(f"- 消息数量: {len(messages)}")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": self.model_name,
                        "messages": messages
                    },
                    timeout=self.timeout
                )
                
                # 处理不同的HTTP状态码
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if 'response' in result:
                            return result['response'], None
                        elif 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content'], None
                        else:
                            error_msg = f"API响应格式错误: {result}"
                            print(error_msg)
                            if attempt < self.max_retries - 1:
                                continue
                            return None, error_msg
                    except json.JSONDecodeError as e:
                        error_msg = f"解析API响应JSON失败: {str(e)}"
                        print(error_msg)
                        if attempt < self.max_retries - 1:
                            continue
                        return None, error_msg
                elif response.status_code == 502:
                    error_msg = f"服务器暂时不可用 (502)，正在进行第 {attempt + 1} 次重试"
                    print(error_msg)
                    if attempt < self.max_retries - 1:
                        continue
                    return None, error_msg
                elif response.status_code == 429:
                    error_msg = f"请求频率限制 (429)，正在进行第 {attempt + 1} 次重试"
                    print(error_msg)
                    if attempt < self.max_retries - 1:
                        continue
                    return None, error_msg
                elif response.status_code == 503:
                    error_msg = f"服务暂时不可用 (503)，正在进行第 {attempt + 1} 次重试"
                    print(error_msg)
                    if attempt < self.max_retries - 1:
                        continue
                    return None, error_msg
                else:
                    error_msg = f"API请求失败: HTTP {response.status_code} - {response.text}"
                    print(error_msg)
                    if attempt < self.max_retries - 1:
                        continue
                    return None, error_msg
                    
            except requests.Timeout:
                error_msg = f"请求超时，正在进行第 {attempt + 1} 次重试"
                print(error_msg)
                if attempt < self.max_retries - 1:
                    continue
                return None, error_msg
            except requests.ConnectionError:
                error_msg = f"连接错误，正在进行第 {attempt + 1} 次重试"
                print(error_msg)
                if attempt < self.max_retries - 1:
                    continue
                return None, error_msg
            except Exception as e:
                error_msg = f"请求出错: {str(e)}，正在进行第 {attempt + 1} 次重试"
                print(error_msg)
                if attempt < self.max_retries - 1:
                    continue
                return None, error_msg
        
        return None, f"达到最大重试次数 ({self.max_retries})"

def save_failed_tasks(failed_files: list, output_dir: str):
    """保存失败任务清单到Markdown文件和Excel表格
    
    Args:
        failed_files: 失败文件列表，每个元素为 (文件路径, 错误信息, 模型响应)
        output_dir: 输出目录
    """
    if not failed_files:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    failed_tasks_md = os.path.join(output_dir, f"failed_tasks_{timestamp}.md")
    failed_tasks_excel = os.path.join(output_dir, f"failed_tasks_{timestamp}.xlsx")
    
    # 保存为Markdown文件
    with open(failed_tasks_md, 'w', encoding='utf-8') as f:
        f.write("# 失败任务清单\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 失败文件列表\n\n")
        
        for file_path, error, model_response in failed_files:
            f.write(f"### {os.path.basename(file_path)}\n\n")
            f.write(f"- 文件路径: `{file_path}`\n")
            f.write(f"- 错误信息: {error}\n")
            if model_response:
                f.write("\n#### 模型返回内容\n\n")
                f.write("```\n")
                f.write(model_response)
                f.write("\n```\n\n")
        
        f.write("## 失败原因统计\n\n")
        # 统计错误类型
        error_types = {}
        for _, error, _ in failed_files:
            error_type = error.split(':')[0] if ':' in error else error
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            f.write(f"- {error_type}: {count}个文件\n")
    
    # 保存为Excel文件
    df = pd.DataFrame([
        {
            '文件名': os.path.basename(file_path),
            '文件路径': file_path,
            '错误信息': error,
            '模型响应': model_response if model_response else ''
        }
        for file_path, error, model_response in failed_files
    ])
    
    # 添加错误类型统计sheet
    error_stats = pd.DataFrame([
        {'错误类型': error_type, '数量': count}
        for error_type, count in error_types.items()
    ])
    
    # 保存到Excel，包含两个sheet
    with pd.ExcelWriter(failed_tasks_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='失败文件列表', index=False)
        error_stats.to_excel(writer, sheet_name='错误统计', index=False)
    
    print(f"\n失败任务清单已保存到:")
    print(f"- Markdown文件: {failed_tasks_md}")
    print(f"- Excel文件: {failed_tasks_excel}")

def process_files(input_dir: str, output_dir: str, config: dict) -> None:
    """处理目录中的所有文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        config: 配置信息
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有文件
    files = []
    for root, _, filenames in os.walk(input_dir):
        for filename in filenames:
            if filename.endswith(tuple(config['processing']['supported_extensions'])):
                files.append(os.path.join(root, filename))
    
    if not files:
        print(f"在 {input_dir} 中没有找到支持的文件")
        return
    
    print(f"\n找到 {len(files)} 个文件需要处理")
    print(f"支持的文件类型: {', '.join(config['processing']['supported_extensions'])}")
    
    # 创建LLM客户端
    try:
        llm_client = LLMClient(config['llm'])
    except Exception as e:
        print(f"创建LLM客户端失败: {str(e)}")
        return
    
    # 处理每个文件
    failed_files = []
    for file_path in tqdm(files, desc="处理文件"):
        try:
            print(f"\n开始处理文件: {file_path}")
            
            # 读取文件
            try:
                text = read_file(file_path)
                if not text:
                    print(f"文件内容为空: {file_path}")
                    failed_files.append((file_path, "文件内容为空", None))
                    continue
            except Exception as e:
                print(f"读取文件失败: {str(e)}")
                failed_files.append((file_path, f"读取文件失败: {str(e)}", None))
                continue
            
            # 计算每个块的问题数量
            chunks = split_text(text)
            total_chunks = len(chunks)
            if total_chunks == 0:
                print(f"文件分块后为空: {file_path}")
                failed_files.append((file_path, "文件分块后为空", None))
                continue
                
            questions_per_file = config['processing']['questions_per_file']
            questions_per_chunk = questions_per_file // total_chunks
            remainder = questions_per_file % total_chunks
            
            print(f"文件将被分为 {total_chunks} 个块处理")
            print(f"每个块生成 {questions_per_chunk} 个问题")
            if remainder > 0:
                print(f"最后一个块额外生成 {remainder} 个问题")
            
            # 生成问答对
            qa_pairs = []
            for i, chunk in enumerate(tqdm(chunks, desc=f"处理 {os.path.basename(file_path)} 的文本块", leave=False)):
                # 为最后一个块分配剩余的问题
                current_questions = questions_per_chunk + (1 if i == total_chunks - 1 and remainder > 0 else 0)
                
                # 构建消息
                system_prompt = config['prompts']['system_prompt_template'].format(questions_count=current_questions)
                user_prompt = config['prompts']['user_prompt_template'].format(text=chunk)
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                # 调用API
                response, error = llm_client.generate_response(messages)
                if error:
                    print(f"\n处理文件 {file_path} 的第 {i+1} 个文本块时出错: {error}")
                    failed_files.append((file_path, error, response))
                    continue
                
                try:
                    # 解析返回的JSON
                    chunk_qa_pairs = json.loads(response)
                    if not isinstance(chunk_qa_pairs, list):
                        raise ValueError("API返回的不是问答对列表")
                    qa_pairs.extend(chunk_qa_pairs)
                except json.JSONDecodeError as e:
                    print(f"\n解析JSON时出错: {str(e)}")
                    failed_files.append((file_path, f"JSON解析错误: {str(e)}", response))
                    continue
                except ValueError as e:
                    print(f"\n验证问答对格式时出错: {str(e)}")
                    failed_files.append((file_path, f"问答对格式错误: {str(e)}", response))
                    continue
            
            if qa_pairs:
                # 保存结果
                output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_qa.csv")
                try:
                    save_qa_pairs(qa_pairs, output_file)
                    print(f"成功保存 {len(qa_pairs)} 个问答对到: {output_file}")
                except Exception as e:
                    print(f"保存问答对失败: {str(e)}")
                    failed_files.append((file_path, f"保存问答对失败: {str(e)}", None))
            else:
                print(f"未能生成任何问答对: {file_path}")
                failed_files.append((file_path, "未能生成任何问答对", None))
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            failed_files.append((file_path, str(e), None))
            continue
    
    # 保存失败任务清单
    if failed_files:
        print(f"\n有 {len(failed_files)} 个文件处理失败")
        save_failed_tasks(failed_files, output_dir)
    else:
        print("\n所有文件处理成功！")

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 获取配置
        input_dir = config['paths']['input_dir']
        output_dir = config['paths']['output_dir']
        
        # 处理文件
        process_files(input_dir, output_dir, config)
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 