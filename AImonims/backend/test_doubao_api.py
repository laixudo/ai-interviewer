import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 测试豆包API连接
def test_doubao_api():
    try:
        api_key = os.getenv("DOUBAO_API_KEY")
        model = os.getenv("DOUBAO_MODEL", "Doubao-Seed-2.0-pro")
        base_url = os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
        
        print(f"API Key: {api_key}")
        print(f"Model: {model}")
        print(f"Base URL: {base_url}")
        
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 测试生成响应
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位专业的面试官"},
                {"role": "user", "content": "请生成一个简单的面试问题"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        print("\nAPI调用成功！")
        print("响应:", response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"\nAPI调用失败: {e}")
        return False

if __name__ == "__main__":
    print("测试豆包API连接...")
    test_doubao_api()