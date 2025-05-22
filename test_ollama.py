import subprocess
import json
import time
import requests

def check_ollama_service():
    """检查Ollama服务是否正常运行"""
    try:
        # 尝试获取模型列表
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        print("\n已安装的模型列表:")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"检查Ollama服务时出错: {str(e)}")
        return False

def test_ollama_api():
    """测试Ollama API连接"""
    
    print("正在检查Ollama服务状态...")
    if not check_ollama_service():
        print("Ollama服务可能未正常运行，请检查服务状态")
        return
    
    # 测试用的简单提示
    test_prompt = "你好，请用一句话回答：1+1等于几？"
    
    # 构建curl命令
    curl_command = [
        "curl",
        "-v",  # 添加详细输出
        "http://localhost:11434/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": "deepseek-r1:latest",
            "messages": [
                {"role": "user", "content": test_prompt}
            ]
        })
    ]
    
    print("\n正在测试Ollama API连接...")
    print(f"发送请求: {test_prompt}")
    
    try:
        # 执行curl命令
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 打印响应状态码
        print(f"\n状态码: {result.returncode}")
        
        # 打印响应内容
        print("\n响应内容:")
        print(result.stdout)
        
        # 如果有错误，打印错误信息
        if result.stderr:
            print("\n错误信息:")
            print(result.stderr)
            
        # 尝试解析响应
        try:
            response_data = json.loads(result.stdout)
            print("\n解析后的响应:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\n响应不是有效的JSON格式")
            
    except subprocess.TimeoutExpired:
        print("请求超时")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    test_ollama_api() 