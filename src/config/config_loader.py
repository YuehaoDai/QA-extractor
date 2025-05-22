"""配置加载模块"""
import os
import yaml

def load_config() -> dict:
    """加载配置文件
    
    Returns:
        dict: 配置信息字典
        
    Raises:
        FileNotFoundError: 配置文件不存在时抛出
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) 