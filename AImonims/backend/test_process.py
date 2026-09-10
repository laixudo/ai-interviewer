import sys
sys.path.insert(0, '.')

from main import process_interview
import time

print('Testing process_interview...')
start = time.time()

# Simple test
result = process_interview('测试问题', '我擅长Java Spring Boot')

print(f'Time: {time.time() - start:.2f}s')
print('Result:', result)
