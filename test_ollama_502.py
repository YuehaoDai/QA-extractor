import requests
import time
import yaml
import json
import sys
from pathlib import Path

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / 'config.yaml'
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_simple_request():
    """测试简单请求"""
    config = load_config()
    api_url = config['llm']['api_url']
    model_name = config['llm']['model_name']
    
    print(f"使用API地址: {api_url}")
    print(f"使用模型: {model_name}")
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "你好，请用一句话回答：1+1等于几？"}],
        "temperature": 0.7
    }
    
    print("\n发送简单请求...")
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30  # 短超时时间
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("请求成功!")
            try:
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                print(f"模型回答: {content}")
            except Exception as e:
                print(f"解析响应时出错: {str(e)}")
        else:
            print(f"请求失败: {response.text}")
    except requests.Timeout:
        print("请求超时")
    except Exception as e:
        print(f"发生错误: {str(e)}")

def test_large_request():
    """测试大型请求"""
    config = load_config()
    api_url = config['llm']['api_url']
    model_name = config['llm']['model_name']
    
    # 创建一个较大的文本内容
    large_content = "测试内容\n" * 100  # 重复100次
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": "你是一个专业的文档分析助手。请分析文档内容并提供5个问答对，格式为JSON。"
            },
            {
                "role": "user", 
                "content": f"请分析以下文档:\n\n{large_content}"
            }
        ],
        "temperature": 0.7
    }
    
    print("\n发送较大请求...")
    print(f"请求大小: {sys.getsizeof(json.dumps(payload))} 字节")
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60  # 较长超时时间
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("请求成功!")
        else:
            print(f"请求失败: {response.text}")
    except requests.Timeout:
        print("请求超时")
    except Exception as e:
        print(f"发生错误: {str(e)}")

def test_multiple_concurrent_requests():
    """测试多个并发请求"""
    config = load_config()
    api_url = config['llm']['api_url']
    model_name = config['llm']['model_name']
    
    headers = {"Content-Type": "application/json"}
    
    print("\n测试并发请求...")
    for i in range(5):
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": f"请回答问题 {i+1}: 什么是人工智能？"}],
            "temperature": 0.7
        }
        
        print(f"\n发送请求 {i+1}...")
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"请求 {i+1} 状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"请求 {i+1} 成功!")
            else:
                print(f"请求 {i+1} 失败: {response.text}")
        except Exception as e:
            print(f"请求 {i+1} 出错: {str(e)}")
        
        # 暂停1秒再发送下一个请求
        time.sleep(1)

def stress_test():
    """进行压力测试"""
    config = load_config()
    api_url = config['llm']['api_url']
    model_name = config['llm']['model_name']
    
    headers = {"Content-Type": "application/json"}
    
    print("\n开始压力测试...")
    success_count = 0
    fail_count = 0
    
    for i in range(20):  # 进行20次请求
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": f"简短回答问题 {i+1}: 1+{i}等于几？"}],
            "temperature": 0.7
        }
        
        print(f"发送压力测试请求 {i+1}/20...", end="")
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=15  # 短超时
            )
            
            if response.status_code == 200:
                print(" 成功!")
                success_count += 1
            else:
                print(f" 失败! 状态码: {response.status_code}")
                fail_count += 1
                
        except Exception as e:
            print(f" 出错: {str(e)}")
            fail_count += 1
        
        # 暂停0.5秒再发送下一个请求
        time.sleep(0.5)
    
    print(f"\n压力测试结果: 成功 {success_count}/20, 失败 {fail_count}/20")

def continuous_request_test():
    """连续发送请求测试，直到遇到502错误"""
    config = load_config()
    api_url = config['llm']['api_url']
    model_name = config['llm']['model_name']
    
    headers = {"Content-Type": "application/json"}
    
    print("\n开始连续请求测试...")
    print("该测试将持续发送请求，直到遇到502错误或用户中断...")
    
    request_count = 0
    try:
        while True:
            request_count += 1
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": f"请用一句话回答: 什么是人工智能?"}],
                "temperature": 0.7
            }
            
            print(f"发送请求 #{request_count}...", end="", flush=True)
            
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(" 成功!")
                elif response.status_code == 502:
                    print(f" 发现502错误！在第{request_count}次请求时")
                    print("找到502错误! 测试结束")
                    break
                else:
                    print(f" 其他错误: {response.status_code}")
                    
            except Exception as e:
                print(f" 请求出错: {str(e)}")
            
            # 暂停1秒再发送下一个请求
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n用户中断测试")
    
    print(f"共发送了 {request_count} 次请求")

if __name__ == "__main__":
    print("=== Ollama API 502错误测试工具 ===")
    print("该工具用于诊断Ollama API 502错误问题")
    
    while True:
        print("\n请选择要执行的测试:")
        print("1. 发送简单请求")
        print("2. 发送大型请求")
        print("3. 测试并发请求")
        print("4. 进行压力测试")
        print("5. 连续请求测试（直到遇到502错误）")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ")
        
        if choice == '1':
            test_simple_request()
        elif choice == '2':
            test_large_request()
        elif choice == '3':
            test_multiple_concurrent_requests()
        elif choice == '4':
            stress_test()
        elif choice == '5':
            continuous_request_test()
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效的选项，请重新输入") 