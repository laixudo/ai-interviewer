
# -*- coding: utf-8 -*-
import json

# 读取正确的简历分析代码
with open('temp_resume_code.txt', 'r', encoding='utf-8') as f:
    resume_code = f.read()

# 读取main.py文件，只保留前1860行
with open('main.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()[:1860]

# 写入修复后的文件
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
    f.write('\n')
    f.write(resume_code)

print("main.py文件修复完成！")
