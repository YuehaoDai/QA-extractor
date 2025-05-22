"""问答处理模块"""
import json
import requests
from typing import List, Dict, Any
from ..utils.text_utils import count_tokens, split_text

def generate_qa_pairs(text: str, api_url: str, questions_per_chunk: int = None) -> List[Dict[str, Any]]:
    """生成问答对
    
    Args:
        text: 要处理的文本
        api_url: API地址
        questions_per_chunk: 每个文本块生成的问题数量
        
    Returns:
        List[Dict[str, Any]]: 问答对列表
    """
    # 系统提示词
    system_prompt = """你是一个专业的文档分析助手。你的任务是：
    1. 仔细阅读提供的文档内容
    2. 提出10个与文档内容相关的重要问题
    3. 对每个问题，从文档中提取相关信息作为答案
    4. 确保问题和答案都是清晰、准确且相关的
    5. 以JSON格式返回结果，格式为：[{"question": "问题1", "answer": "答案1"}, ...]
    6. 只返回JSON格式的数据，不要包含任何其他内容"""
    
    # 分割文本
    chunks = split_text(text)
    
    # 如果指定了每个块的问题数量，动态调整系统提示词
    if questions_per_chunk is not None:
        system_prompt = system_prompt.replace("提出10个", f"提出{questions_per_chunk}个")
    
    all_qa_pairs = []
    
    # 处理每个文本块
    for chunk in chunks:
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请分析以下文档内容并生成问答对：\n\n{chunk}"}
        ]
        
        # 计算token数
        total_tokens = sum(count_tokens(msg["content"]) for msg in messages)
        print(f"\n当前消息总token数: {total_tokens}")
        
        # 调用API
        try:
            response = requests.post(api_url, json={"messages": messages})
            response.raise_for_status()
            result = response.json()
            
            # 解析返回的JSON
            qa_pairs = json.loads(result['response'])
            all_qa_pairs.extend(qa_pairs)
            
        except Exception as e:
            print(f"处理文本块时出错: {str(e)}")
            continue
    
    return all_qa_pairs 