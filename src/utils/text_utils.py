"""文本处理工具模块"""
import re
import unicodedata
import tiktoken

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """计算文本的token数量
    
    Args:
        text: 要计算token数的文本
        model: 使用的模型名称
        
    Returns:
        int: token数量
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # 如果无法使用tiktoken，使用简单的估算方法
        return len(text) // 4

def clean_for_excel(text) -> str:
    """清理Excel中不允许的字符
    
    Args:
        text: 要清理的文本
        
    Returns:
        str: 清理后的文本
    """
    if not isinstance(text, str):
        return text
        
    # 保留制表符、换行符和回车符
    allowed_control_chars = ['\t', '\n', '\r']
    
    # 清理控制字符和特殊字符
    cleaned_text = ''
    for char in text:
        # 如果是允许的控制字符，保留
        if char in allowed_control_chars:
            cleaned_text += char
            continue
            
        # 获取字符的Unicode类别
        category = unicodedata.category(char)
        
        # 排除控制字符 (Cc类别)但保留允许的控制字符
        if category == 'Cc':
            cleaned_text += ' '  # 用空格替换控制字符
        else:
            # 对于其他字符，尝试保留
            try:
                cleaned_text += char
            except:
                cleaned_text += ' '
    
    return cleaned_text

def split_text(text: str, max_tokens: int = 24000) -> list:
    """将长文本分割成不超过最大token数的片段
    
    Args:
        text: 要分割的文本
        max_tokens: 每个片段的最大token数（包括系统提示词和用户提示词的token数）
                   默认值24000的分配：
                   - 系统提示词：约200 tokens
                   - 用户提示词前缀：约50 tokens
                   - 文档内容：约20000 tokens
                   - 模型回答：约8000 tokens
                   - 余量：约1750 tokens
                   总计：约24000 tokens，在32768 tokens限制内
        
    Returns:
        List[str]: 分割后的文本片段列表
    """
    # 系统提示词
    system_prompt = """你是一个专业的文档分析助手。你的任务是：
    1. 仔细阅读提供的文档内容
    2. 提出10个与文档内容相关的重要问题
    3. 对每个问题，从文档中提取相关信息作为答案
    4. 确保问题和答案都是清晰、准确且相关的
    5. 以JSON格式返回结果，格式为：[{"question": "问题1", "answer": "答案1"}, ...]
    6. 只返回JSON格式的数据，不要包含任何其他内容"""
    
    # 计算系统提示词和用户提示词前缀的token数
    system_tokens = count_tokens(system_prompt)
    user_prompt_prefix = "请分析以下文档内容并生成问答对：\n\n"
    user_prefix_tokens = count_tokens(user_prompt_prefix)
    
    # 计算实际可用于文档内容的token数
    available_tokens = max_tokens - system_tokens - user_prefix_tokens
    
    if count_tokens(text) <= available_tokens:
        return [text]
    
    # 按段落分割文本
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = count_tokens(para)
        
        # 如果单个段落超过最大token数，需要进一步分割
        if para_tokens > available_tokens:
            # 如果当前chunk不为空，先保存
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # 按句子分割长段落
            sentences = re.split(r'([.!?。！？])', para)
            temp_sentence = ''
            
            for i in range(0, len(sentences), 2):
                if i + 1 < len(sentences):
                    sentence = sentences[i] + sentences[i + 1]
                else:
                    sentence = sentences[i]
                
                sentence_tokens = count_tokens(sentence)
                
                if count_tokens(temp_sentence + sentence) <= available_tokens:
                    temp_sentence += sentence
                else:
                    if temp_sentence:
                        chunks.append(temp_sentence)
                    temp_sentence = sentence
            
            if temp_sentence:
                chunks.append(temp_sentence)
            continue
        
        # 检查添加当前段落是否会超过限制
        if current_tokens + para_tokens <= available_tokens:
            current_chunk.append(para)
            current_tokens += para_tokens
        else:
            # 保存当前chunk并开始新的chunk
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
    
    # 添加最后一个chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks 