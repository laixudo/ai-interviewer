import sqlite3
import json
import os

def add_new_tables():
    db_path = os.path.join(os.path.dirname(__file__), 'interview.db')

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("开始创建新的数据表...")

    # 1. 面试干货表 (interview_tips)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        summary TEXT,
        content TEXT,
        category TEXT NOT NULL,
        tags TEXT,
        difficulty TEXT DEFAULT 'beginner',
        related_skills TEXT,
        view_count INTEGER DEFAULT 0,
        collect_count INTEGER DEFAULT 0,
        author_id INTEGER,
        author_name TEXT DEFAULT '系统',
        status TEXT DEFAULT 'published',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ interview_tips 表创建成功")

    # 2. 用户干货交互表 (user_tip_interactions)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_tip_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tip_id INTEGER NOT NULL,
        is_collected INTEGER DEFAULT 0,
        is_read INTEGER DEFAULT 0,
        read_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (tip_id) REFERENCES interview_tips (id)
    )
    ''')
    print("✓ user_tip_interactions 表创建成功")

    # 3. 用户简历表 (user_resumes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_name TEXT,
        file_path TEXT,
        file_type TEXT,
        parsed_data TEXT,
        analysis_result TEXT,
        target_position TEXT,
        status TEXT DEFAULT 'uploaded',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✓ user_resumes 表创建成功")

    # 4. 简历优化建议表 (resume_suggestions)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        dimension TEXT,
        issue TEXT,
        suggestion TEXT,
        original_text TEXT,
        optimized_text TEXT,
        priority TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES user_resumes (id)
    )
    ''')
    print("✓ resume_suggestions 表创建成功")

    # 5. 社区帖子表 (community_posts)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS community_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        type TEXT DEFAULT 'experience',
        title TEXT NOT NULL,
        content TEXT,
        category TEXT,
        tags TEXT,
        view_count INTEGER DEFAULT 0,
        like_count INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'published',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✓ community_posts 表创建成功")

    # 6. 帖子评论表 (post_comments)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS post_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        username TEXT,
        content TEXT NOT NULL,
        parent_id INTEGER,
        like_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES community_posts (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✓ post_comments 表创建成功")

    # 7. 投递记录表 (job_applications)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        resume_id INTEGER,
        company TEXT NOT NULL,
        position TEXT NOT NULL,
        job_type TEXT DEFAULT 'fulltime',
        salary_range TEXT,
        stage TEXT DEFAULT 'applied',
        interview_date DATE,
        notes TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (resume_id) REFERENCES user_resumes (id)
    )
    ''')
    print("✓ job_applications 表创建成功")

    # 8. 优秀简历参考表 (reference_resumes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reference_resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        industry TEXT,
        position TEXT,
        resume_data TEXT,
        highlights TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ reference_resumes 表创建成功")

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interview_tips_category ON interview_tips (category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interview_tips_author ON interview_tips (author_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_tip_interactions_user ON user_tip_interactions (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_tip_interactions_tip ON user_tip_interactions (tip_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_resumes_user ON user_resumes (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_community_posts_user ON community_posts (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_community_posts_category ON community_posts (category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_comments_post ON post_comments (post_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_applications_user ON job_applications (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_applications_stage ON job_applications (stage)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reference_resumes_position ON reference_resumes (position)')
    print("✓ 索引创建成功")

    # 插入一些示例面试干货数据
    sample_tips = [
        {
            'title': '如何做好自我介绍',
            'summary': '面试中最常见的第一个问题，好的自我介绍能为面试定下基调',
            'content': '''# 如何做好自我介绍

## 基本原则
1. **控制时间**：2-3分钟为宜
2. **突出重点**：与岗位相关的经历优先
3. **逻辑清晰**：按时间线或能力线组织

## 结构建议
- 开场：基本信息（姓名、学校、专业）
- 核心：与岗位相关的工作/项目经验
- 结尾：表达对该岗位的兴趣和优势

## 常见错误
- ❌ 像念简历一样背诵
- ❌ 时间过长或过短
- ❌ 缺乏与岗位的关联性''',
            'category': '技巧类',
            'tags': json.dumps(['自我介绍', '面试技巧', '初级']),
            'difficulty': 'beginner',
            'related_skills': json.dumps(['沟通能力', '表达能力', '自我认知']),
            'author_name': '系统'
        },
        {
            'title': 'STAR法则让你的回答更专业',
            'summary': '使用STAR法则描述经历，让面试官清晰地了解你的能力和成果',
            'content': '''# STAR法则详解

## 什么是STAR法则
- **S**ituation（情境）：描述当时的情境或背景
- **T**ask（任务）：你的任务或职责是什么
- **A**ction（行动）：你采取了什么行动
- **R**esult（结果）：取得了什么结果

## 应用示例
**问题**：请描述你完成的一个项目

**回答**：
- S：在我实习的公司，我负责优化用户注册流程
- T：当时的注册转化率只有30%，需要提升
- A：我分析了用户行为数据，优化了注册表单，并增加了引导功能
- R：最终注册转化率提升到65%，提升了117%

## 注意事项
- 结果尽量量化，用数据说话
- 突出个人贡献而非团队成果''',
            'category': '技巧类',
            'tags': json.dumps(['STAR法则', '答题技巧', '中级']),
            'difficulty': 'intermediate',
            'related_skills': json.dumps(['逻辑思维', '表达能力', '项目经验']),
            'author_name': '系统'
        },
        {
            'title': '互联网产品经理面试指南',
            'summary': '详细介绍互联网产品经理岗位的面试流程和常见问题',
            'content': '''# 互联网产品经理面试指南

## 面试流程
1. **一面**：业务面（项目经历、专业能力）
2. **二面**：业务负责人（深入项目、思维模式）
3. **三面**：HR/高管（价值观、稳定性）

## 常见问题类型
### 项目经历类
- 请介绍一下你最成功的项目
- 项目中遇到的最大挑战是什么？
- 你在项目中扮演什么角色？

### 专业能力类
- 如何进行需求优先级排序？
- 描述一次你推动项目落地的经历
- 如何判断一个需求是否值得做？

### 思维类
- 你认为产品经理最重要的能力是什么？
- 如果做XXX产品，你会怎么做？
''',
            'category': '行业类',
            'tags': json.dumps(['产品经理', '互联网', '面试指南']),
            'difficulty': 'intermediate',
            'related_skills': json.dumps(['产品思维', '项目管理', '沟通协调']),
            'author_name': '系统'
        },
        {
            'title': '公务员面试技巧大全',
            'summary': '系统整理公务员面试的题型、答题思路和注意事项',
            'content': '''# 公务员面试技巧大全

## 面试形式
- **结构化面试**：最常见的形式
- **无领导小组讨论**：部分岗位采用
- **结构化小组**：新兴形式

## 五大题型
1. **综合分析**：对社会现象或观点的分析
2. **计划组织**：组织活动类题目
3. **人际关系**：处理人际关系的场景
4. **应急应变**：处理突发情况
5. **言语理解**：演讲、沟通类题目

## 备考建议
- 多看新闻，了解时事热点
- 练习历年真题，熟悉出题方向
- 注重仪态，保持自信''',
            'category': '行业类',
            'tags': json.dumps(['公务员', '事业单位', '面试技巧']),
            'difficulty': 'beginner',
            'related_skills': json.dumps(['综合分析', '语言表达', '应变能力']),
            'author_name': '系统'
        },
        {
            'title': '技术类岗位面试常见问题',
            'summary': '涵盖Java、Python、前端等技术岗位的面试高频问题',
            'content': '''# 技术类岗位面试常见问题

## Java开发
### 基础问题
- HashMap和HashTable的区别
- 多线程的实现方式
- Spring Boot自动装配原理

### 进阶问题
- 分布式事务如何处理
- 如何保证接口幂等性
- Redis缓存穿透、击穿、雪崩及解决方案

## Python开发
### 基础问题
- Python中的装饰器是什么
- Python中的GIL是什么
- 生成器和迭代器的区别

### 进阶问题
- 如何设计一个分布式爬虫
- Python中的内存管理机制

## 前端开发
### 基础问题
- Vue响应式原理
- JavaScript事件循环
- CSS盒模型

### 进阶问题
- 如何优化前端性能
- Webpack构建优化''',
            'category': '真题类',
            'tags': json.dumps(['技术面试', 'Java', 'Python', '前端']),
            'difficulty': 'advanced',
            'related_skills': json.dumps(['技术知识', '问题解决', '源码理解']),
            'author_name': '系统'
        }
    ]

    cursor.execute('SELECT COUNT(*) FROM interview_tips')
    count = cursor.fetchone()[0]
    if count == 0:
        for tip in sample_tips:
            cursor.execute('''
            INSERT INTO interview_tips (title, summary, content, category, tags, difficulty, related_skills, author_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tip['title'], tip['summary'], tip['content'], tip['category'],
                  tip['tags'], tip['difficulty'], tip['related_skills'], tip['author_name']))
        print(f"✓ 插入 {len(sample_tips)} 条示例面试干货")

    conn.commit()
    conn.close()

    print("\n数据库更新完成！")

if __name__ == '__main__':
    add_new_tables()
