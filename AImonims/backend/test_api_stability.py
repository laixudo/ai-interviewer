import requests
import json
import time
import statistics

# 测试数据
payloads = [
    {"content": "我熟练使用Spring Boot开发后端接口", "interview_id": 1},
    {"content": "我在项目中使用多线程和并发编程", "interview_id": 1},
    {"content": "我熟悉MySQL数据库设计和SQL优化", "interview_id": 1},
    {"content": "我参与了AI模拟面试系统的开发", "interview_id": 1},
    {"content": "我擅长Java核心语法和面向对象编程", "interview_id": 1}
]

# 测试结果
results = []

# 运行测试
for i in range(10):  # 运行10次测试
    print(f"\n=== 测试轮次 {i+1} ===")
    for j, payload in enumerate(payloads):
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:8000/api/interview/message",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
            end_time = time.time()
            response_time = end_time - start_time
            status_code = response.status_code
            response_content = response.json()
            
            results.append({
                "test_round": i+1,
                "test_case": j+1,
                "input": payload["content"],
                "output": response_content["response"],
                "status_code": status_code,
                "response_time": response_time
            })
            
            print(f"测试用例 {j+1}: 响应时间: {response_time:.2f}秒, 状态码: {status_code}")
            print(f"  输入: {payload['content']}")
            print(f"  输出: {response_content['response']}")
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            results.append({
                "test_round": i+1,
                "test_case": j+1,
                "input": payload["content"],
                "output": f"错误: {str(e)}",
                "status_code": 0,
                "response_time": response_time
            })
            
            print(f"测试用例 {j+1}: 响应时间: {response_time:.2f}秒, 错误: {str(e)}")
        
        # 等待1秒，避免请求过于频繁
        time.sleep(1)

# 分析结果
print("\n=== 测试结果分析 ===")

# 计算响应时间统计
response_times = [r["response_time"] for r in results if r["status_code"] == 200]
if response_times:
    avg_time = statistics.mean(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    std_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
    
    print(f"成功响应次数: {len(response_times)}/{len(results)}")
    print(f"平均响应时间: {avg_time:.2f}秒")
    print(f"最小响应时间: {min_time:.2f}秒")
    print(f"最大响应时间: {max_time:.2f}秒")
    print(f"响应时间标准差: {std_time:.2f}秒")
else:
    print("没有成功的响应")

# 计算错误率
error_count = sum(1 for r in results if r["status_code"] != 200)
error_rate = error_count / len(results) * 100
print(f"错误率: {error_rate:.2f}%")

# 分析输出是否重复
texts = [r["output"] for r in results if r["status_code"] == 200]
unique_texts = set(texts)
print(f"唯一输出数量: {len(unique_texts)}/{len(texts)}")
print("\n唯一输出:")
for text in unique_texts:
    print(f"- {text}")
