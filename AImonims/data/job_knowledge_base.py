# 岗位化题库与知识库

# 岗位定义
JOB_TYPES = {
    "java_backend": "Java后端开发工程师",
    "web_frontend": "Web前端开发工程师",
    "python_algorithm": "Python算法工程师",
    "test_engineer": "测试工程师"
}

# 面试题型
QUESTION_TYPES = {
    "technical": "技术知识",
    "project": "项目经历",
    "behavioral": "行为问题",
    "scenario": "场景题",
    "system_design": "系统设计"
}

# 岗位题库
JOB_QUESTIONS = {
    "java_backend": {
        "technical": [
            "请解释Java中的多线程原理",
            "什么是Java中的垃圾回收机制？有哪些垃圾回收算法？",
            "请详细介绍Spring框架的核心组件",
            "什么是Java中的反射机制？有什么优缺点？",
            "请解释Java中的类加载机制",
            "什么是Java中的线程安全？如何实现线程安全？",
            "请详细介绍Java中的集合框架",
            "什么是Java中的泛型？有什么作用？",
            "请解释Java中的异常处理机制",
            "什么是Java中的序列化和反序列化？"
        ],
        "project": [
            "请分享一个你参与的Java后端项目，描述你在项目中的角色和贡献",
            "在你的项目中，遇到过哪些技术难题？你是如何解决的？",
            "请描述一个你优化过的Java后端系统，优化前后的性能对比如何？",
            "在团队开发中，你是如何保证代码质量的？",
            "请分享一个你使用Spring Boot开发的项目，介绍其架构设计"
        ],
        "behavioral": [
            "在工作中，你如何处理与同事的意见分歧？",
            "当项目 deadline 临近时，你会如何应对压力？",
            "请分享一个你成功解决的技术问题，你是如何思考和解决的？",
            "你如何看待技术债务？在项目中你是如何管理技术债务的？",
            "你如何保持对新技术的学习和了解？"
        ],
        "scenario": [
            "如果你的服务突然出现性能问题，你会如何排查和解决？",
            "当系统面临高并发请求时，你会采取哪些优化措施？",
            "如果数据库查询性能不佳，你会如何优化？",
            "当你的代码出现bug时，你会如何定位和修复？",
            "如果需要设计一个分布式系统，你会考虑哪些因素？"
        ],
        "system_design": [
            "请设计一个高可用的电商订单系统",
            "如何设计一个支持百万级用户的即时通讯系统？",
            "请设计一个分布式缓存系统的架构"
        ]
    },
    "web_frontend": {
        "technical": [
            "请解释React的生命周期",
            "什么是ES6+的新特性？请举例说明",
            "请详细介绍前端性能优化的方法",
            "什么是浏览器的渲染机制？",
            "请解释前端路由的实现原理",
            "什么是CSS盒模型？",
            "请详细介绍JavaScript的闭包和原型链",
            "什么是前端安全问题？如何防范？",
            "请解释前端模块化的发展历程",
            "什么是Webpack？它的核心功能是什么？"
        ],
        "project": [
            "请分享一个你参与的前端项目，描述你在项目中的角色和贡献",
            "在你的项目中，遇到过哪些前端性能问题？你是如何解决的？",
            "请描述一个你使用React或Vue开发的项目，介绍其组件设计",
            "在团队开发中，你是如何保证前端代码质量的？",
            "请分享一个你优化过的前端页面，优化前后的性能对比如何？"
        ],
        "behavioral": [
            "在工作中，你如何与后端开发人员协作？",
            "当设计需求频繁变更时，你会如何应对？",
            "请分享一个你成功解决的前端问题，你是如何思考和解决的？",
            "你如何看待前端技术的快速迭代？你是如何保持技术竞争力的？",
            "你如何平衡代码质量和开发速度？"
        ],
        "scenario": [
            "如果你的页面加载速度很慢，你会如何排查和优化？",
            "当用户反馈页面在某些浏览器上显示异常时，你会如何处理？",
            "如果需要实现一个复杂的表单验证，你会如何设计？",
            "当你的前端代码出现bug时，你会如何定位和修复？",
            "如果需要设计一个响应式页面，你会考虑哪些因素？"
        ],
        "system_design": [
            "请设计一个高性能的单页应用架构",
            "如何设计一个支持多语言的国际化系统？",
            "请设计一个可复用的组件库架构"
        ]
    },
    "python_algorithm": {
        "technical": [
            "请解释Python中的GIL（全局解释器锁）",
            "什么是Python中的生成器和迭代器？",
            "请详细介绍Python中的装饰器",
            "什么是Python中的多线程和多进程？",
            "请解释Python中的垃圾回收机制",
            "什么是Python中的元类？",
            "请详细介绍Python中的模块和包",
            "什么是Python中的上下文管理器？",
            "请解释Python中的深拷贝和浅拷贝",
            "什么是Python中的闭包？"
        ],
        "project": [
            "请分享一个你参与的算法项目，描述你在项目中的角色和贡献",
            "在你的项目中，遇到过哪些算法难题？你是如何解决的？",
            "请描述一个你优化过的算法，优化前后的性能对比如何？",
            "在团队开发中，你是如何保证算法代码质量的？",
            "请分享一个你使用Python实现的机器学习项目，介绍其算法选择"
        ],
        "behavioral": [
            "在工作中，你如何处理复杂的算法问题？",
            "当你的算法性能不达标时，你会如何优化？",
            "请分享一个你成功解决的算法问题，你是如何思考和解决的？",
            "你如何看待算法的时间复杂度和空间复杂度？",
            "你如何保持对新算法和新模型的学习？"
        ],
        "scenario": [
            "如果你的算法在生产环境中表现不佳，你会如何排查和优化？",
            "当面对大规模数据时，你会如何设计高效的算法？",
            "如果需要实现一个推荐系统，你会选择哪些算法？",
            "当你的算法出现bug时，你会如何定位和修复？",
            "如果需要设计一个搜索算法，你会考虑哪些因素？"
        ],
        "system_design": [
            "请设计一个大规模机器学习平台架构",
            "如何设计一个实时推荐系统？",
            "请设计一个分布式训练系统的架构"
        ]
    },
    "test_engineer": {
        "technical": [
            "请解释软件测试的基本概念和测试类型",
            "什么是单元测试、集成测试和系统测试？",
            "请详细介绍测试用例设计方法",
            "什么是自动化测试？有哪些常用的自动化测试工具？",
            "请解释性能测试和压力测试的区别",
            "什么是接口测试？如何进行接口测试？",
            "请详细介绍Web应用的测试方法",
            "什么是缺陷管理？如何跟踪和管理缺陷？",
            "请解释测试覆盖率的概念和计算方法",
            "什么是持续集成和持续测试？"
        ],
        "project": [
            "请分享一个你参与的测试项目，描述你在项目中的角色和贡献",
            "在你的项目中，遇到过哪些测试难题？你是如何解决的？",
            "请描述一个你设计的测试用例库，介绍其设计思路",
            "在团队开发中，你是如何与开发人员协作的？",
            "请分享一个你实施的自动化测试项目，介绍其实施效果"
        ],
        "behavioral": [
            "在工作中，你如何与开发人员沟通测试发现的问题？",
            "当项目 deadline 临近时，你会如何安排测试工作？",
            "请分享一个你成功发现的严重缺陷，你是如何发现和跟进的？",
            "你如何看待测试在软件开发中的作用？",
            "你如何保持对测试新技术的学习和了解？"
        ],
        "scenario": [
            "如果发现一个严重缺陷，但发布时间紧迫，你会如何处理？",
            "当测试环境不稳定时，你会如何确保测试工作的顺利进行？",
            "如果需要对一个复杂系统进行测试，你会如何设计测试策略？",
            "当自动化测试用例维护成本很高时，你会如何优化？",
            "如果需要提高测试效率，你会采取哪些措施？"
        ],
        "system_design": [
            "请设计一个完整的测试流程和规范",
            "如何设计一个自动化测试框架？",
            "请设计一个测试平台的架构"
        ]
    }
}

# 岗位核心技术栈
JOB_TECH_STACKS = {
    "java_backend": [
        "Java SE",
        "Spring Boot",
        "Spring Cloud",
        "MySQL",
        "Redis",
        "Docker",
        "微服务架构",
        "消息队列"
    ],
    "web_frontend": [
        "HTML5",
        "CSS3",
        "JavaScript",
        "React/Vue",
        "TypeScript",
        "Webpack",
        "响应式设计",
        "前端性能优化"
    ],
    "python_algorithm": [
        "Python基础",
        "NumPy/Pandas",
        "Scikit-learn",
        "TensorFlow/PyTorch",
        "算法设计",
        "数据结构",
        "机器学习",
        "深度学习"
    ],
    "test_engineer": [
        "软件测试理论",
        "Selenium/Appium",
        "Jmeter/LoadRunner",
        "Postman/Jmeter",
        "Junit/TestNG",
        "缺陷管理工具",
        "持续集成",
        "测试用例设计"
    ]
}

# 优秀回答范例
EXCELLENT_ANSWERS = {
    "java_backend": {
        "请解释Java中的多线程原理": """
Java中的多线程是通过Thread类和Runnable接口实现的。线程是程序执行的最小单位，多线程可以提高程序的执行效率。

在Java中，我们可以通过以下方式创建线程：
1. 继承Thread类，重写run()方法
2. 实现Runnable接口，实现run()方法
3. 使用Callable和Future

线程的生命周期包括：新建（New）、就绪（Runnable）、运行（Running）、阻塞（Blocked）、死亡（Terminated）五个状态。

多线程编程需要注意线程安全问题，通常可以通过以下方式保证线程安全：
1. synchronized关键字
2. Lock接口
3. 原子类（AtomicInteger等）
4. 线程安全的集合类（ConcurrentHashMap等）

例如，使用synchronized修饰方法或代码块可以确保同一时间只有一个线程执行该部分代码。
        """,
        "什么是Java中的垃圾回收机制？有哪些垃圾回收算法？": """
Java的垃圾回收（GC）是自动管理内存的机制，它可以自动回收不再使用的对象，避免内存泄漏。

垃圾回收的主要步骤包括：
1. 标记：识别哪些对象是可达的，哪些是不可达的
2. 清除：回收不可达对象占用的内存
3. 压缩（可选）：移动存活对象，减少内存碎片

常见的垃圾回收算法包括：
1. 标记-清除算法（Mark-Sweep）：先标记再清除，会产生内存碎片
2. 复制算法（Copying）：将存活对象复制到新区域，适用于年轻代
3. 标记-整理算法（Mark-Compact）：标记后整理存活对象，适用于老年代
4. 分代收集算法（Generational Collection）：根据对象年龄分代收集

Java虚拟机中的常见垃圾回收器包括：
- Serial收集器：单线程收集，适用于客户端应用
- Parallel收集器：多线程收集，注重吞吐量
- CMS（Concurrent Mark Sweep）收集器：并发收集，注重低延迟
- G1（Garbage-First）收集器：面向服务端，平衡吞吐量和延迟
        """
    },
    "web_frontend": {
        "请解释React的生命周期": """
React组件的生命周期可以分为三个主要阶段：

1. 挂载阶段（Mounting）：
   - constructor()：组件初始化，设置state和绑定方法
   - static getDerivedStateFromProps()：从props获取state，在render前调用
   - render()：渲染组件UI，纯函数
   - componentDidMount()：组件挂载后调用，可以进行DOM操作和网络请求

2. 更新阶段（Updating）：
   - static getDerivedStateFromProps()：同上
   - shouldComponentUpdate()：决定是否更新组件，可用于性能优化
   - render()：重新渲染
   - getSnapshotBeforeUpdate()：在DOM更新前获取快照
   - componentDidUpdate()：组件更新后调用

3. 卸载阶段（Unmounting）：
   - componentWillUnmount()：组件卸载前调用，清理定时器、取消网络请求等

React 16.8引入了Hooks，可以在函数组件中使用状态和其他React特性，如useState、useEffect等。useEffect可以替代多个生命周期方法的功能。
        """,
        "什么是ES6+的新特性？请举例说明": """
ES6（ECMAScript 2015）带来了许多重要的新特性，后续版本也持续添加了新功能：

1. let和const：块级作用域变量声明
   const PI = 3.14159;
   let count = 0;

2. 箭头函数：简化函数语法，不绑定this
   const add = (a, b) => a + b;

3. 模板字符串：支持多行字符串和变量插值
   const name = "张三";
   const greeting = `你好，${name}！`;

4. 解构赋值：从对象或数组中提取值
   const { name, age } = user;
   const [first, second] = array;

5. 类（Class）：面向对象编程的语法糖
   class Person {
     constructor(name) { this.name = name; }
     sayHi() { console.log(`Hi, ${this.name}`); }
   }

6. 模块化：import和export
   import { useState } from 'react';
   export default MyComponent;

7. Promise：异步编程解决方案
   fetch('/api/data')
     .then(res => res.json())
     .then(data => console.log(data));

8. 展开运算符：扩展数组或对象
   const newArray = [...oldArray, newItem];
   const newObj = { ...oldObj, newProp: 'value' };

9. async/await：Promise的语法糖，更清晰的异步代码
   async function fetchData() {
     const res = await fetch('/api/data');
     const data = await res.json();
     return data;
   }

这些特性大大提高了JavaScript的开发效率和代码可读性。
        """
    },
    "python_algorithm": {
        "请解释Python中的GIL（全局解释器锁）": """
GIL（Global Interpreter Lock，全局解释器锁）是CPython解释器中的一个机制，它确保同一时刻只有一个线程在解释器中执行字节码。

GIL的存在有以下影响：

1. 对CPU密集型任务：多线程不会带来性能提升，因为GIL限制了同时只能有一个线程执行。这种情况下，应该使用多进程。

2. 对I/O密集型任务：多线程仍然有效，因为在等待I/O操作时，GIL会被释放，其他线程可以执行。

GIL的优点：
- 简化了C扩展的编写，不需要考虑线程安全
- 简化了解释器的实现
- 对单线程程序性能没有影响

如何绕过GIL的限制：
1. 使用多进程（multiprocessing模块）：每个进程有独立的GIL
2. 使用C扩展：在C代码中可以释放GIL
3. 使用其他Python实现：如Jython、IronPython等没有GIL

例如，对于CPU密集型任务：
from multiprocessing import Pool

def heavy_task(x):
    return x * x

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        results = pool.map(heavy_task, range(100))
        """
    },
    "test_engineer": {
        "请解释软件测试的基本概念和测试类型": """
软件测试是为了发现软件中的缺陷而执行软件的过程，其目的是评估软件的质量。

软件测试的基本概念：
- 缺陷（Bug）：软件中存在的问题或错误
- 测试用例：为特定目标设计的一组输入、执行条件和预期结果
- 测试覆盖率：衡量测试的完整性
- 回归测试：修改代码后重新测试，确保没有引入新缺陷

常见的测试类型：

1. 按测试阶段分：
   - 单元测试：测试单个组件或函数
   - 集成测试：测试多个组件的交互
   - 系统测试：测试整个系统的功能
   - 验收测试：用户或客户确认软件是否满足需求

2. 按测试方法分：
   - 黑盒测试：不考虑内部结构，只测试功能
   - 白盒测试：基于代码结构进行测试
   - 灰盒测试：结合黑盒和白盒测试

3. 按测试目标分：
   - 功能测试：验证软件功能是否符合需求
   - 性能测试：验证系统性能指标
   - 安全测试：验证系统的安全性
   - 兼容性测试：验证在不同环境下的兼容性
   - 易用性测试：验证用户体验

4. 按执行方式分：
   - 手工测试：人工执行测试
   - 自动化测试：使用工具自动化执行测试

测试的原则：
- 测试只能证明缺陷存在，不能证明缺陷不存在
- 尽早测试，持续测试
- 帕累托法则：80%的缺陷集中在20%的代码中
- 测试应该独立于开发
        """
    }
}

# 学习资源推荐
LEARNING_RESOURCES = {
    "java_backend": {
        "技术文档": [
            "Oracle Java官方文档",
            "Spring官方文档",
            "MySQL官方文档",
            "Redis官方文档"
        ],
        "经典书籍": [
            "《深入理解Java虚拟机》",
            "《Effective Java》",
            "《Java并发编程实战》",
            "《Spring实战》",
            "《设计模式》"
        ],
        "在线课程": [
            "Coursera Java课程",
            "慕课网Spring Boot系列课程",
            "极客时间Java并发编程实战"
        ],
        "练习平台": [
            "LeetCode",
            "牛客网",
            "HackerRank"
        ]
    },
    "web_frontend": {
        "技术文档": [
            "MDN Web Docs",
            "React官方文档",
            "Vue官方文档",
            "Webpack官方文档"
        ],
        "经典书籍": [
            "《JavaScript高级程序设计》",
            "《你不知道的JavaScript》",
            "《CSS权威指南》",
            "《React设计模式与最佳实践》"
        ],
        "在线课程": [
            "Coursera前端开发课程",
            "慕课网React/Vue系列课程",
            "极客时间浏览器工作原理与实践"
        ],
        "练习平台": [
            "CodePen",
            "CodeSandbox",
            "Frontend Mentor"
        ]
    },
    "python_algorithm": {
        "技术文档": [
            "Python官方文档",
            "NumPy官方文档",
            "Scikit-learn官方文档",
            "TensorFlow官方文档"
        ],
        "经典书籍": [
            "《Python编程：从入门到实践》",
            "《算法导论》",
            "《机器学习》（周志华）",
            "《统计学习方法》",
            "《深度学习》"
        ],
        "在线课程": [
            "Coursera机器学习课程",
            "Fast.ai深度学习课程",
            "极客时间数据结构与算法之美"
        ],
        "练习平台": [
            "LeetCode",
            "Kaggle",
            "牛客网"
        ]
    },
    "test_engineer": {
        "技术文档": [
            "Selenium官方文档",
            "Postman官方文档",
            "Jmeter官方文档"
        ],
        "经典书籍": [
            "《软件测试艺术》",
            "《自动化测试实战》",
            "《Google软件测试之道》",
            "《敏捷软件测试》"
        ],
        "在线课程": [
            "慕课网软件测试系列课程",
            "Coursera软件测试课程",
            "极客时间测试实战52讲"
        ],
        "练习平台": [
            "DemoBlaze",
            "Restful Booker",
            "GitHub开源项目"
        ]
    }
}

# 岗位常见面试考点
JOB_KEY_POINTS = {
    "java_backend": [
        "Java基础：集合框架、多线程、JVM",
        "Spring框架：IoC、AOP、事务管理",
        "数据库：SQL优化、索引原理、事务隔离",
        "缓存：Redis数据结构、缓存策略",
        "微服务：服务注册发现、配置中心、熔断器",
        "消息队列：Kafka/RabbitMQ的使用场景"
    ],
    "web_frontend": [
        "JavaScript基础：原型链、闭包、作用域",
        "框架原理：React/Vue的核心机制",
        "性能优化：首屏加载、渲染优化、包体积优化",
        "浏览器：渲染机制、Event Loop、缓存策略",
        "工程化：构建工具、代码规范、CI/CD",
        "安全：XSS、CSRF、CSP"
    ],
    "python_algorithm": [
        "数据结构：数组、链表、树、图、堆",
        "算法：排序、查找、动态规划、回溯",
        "机器学习：线性回归、逻辑回归、决策树、神经网络",
        "深度学习：CNN、RNN、Transformer",
        "Python高级特性：装饰器、生成器、上下文管理器",
        "数据分析：NumPy、Pandas的使用"
    ],
    "test_engineer": [
        "测试理论：测试用例设计方法、测试策略",
        "自动化测试：Selenium、Appium、接口自动化",
        "性能测试：JMeter、LoadRunner、性能指标分析",
        "接口测试：Postman、RestAssured、API设计",
        "缺陷管理：缺陷生命周期、缺陷分析",
        "持续集成：Jenkins、GitLab CI、自动化测试集成"
    ]
}

# 面试评估标准
EVALUATION_CRITERIA = {
    "technical_accuracy": "技术正确性",
    "knowledge_depth": "知识深度",
    "logical_expression": "语言表达逻辑性",
    "communication_skills": "沟通能力",
    "problem_solving": "问题解决能力",
    "coding_ability": "编码能力",
    "project_experience": "项目经验",
    "learning_ability": "学习能力"
}

# 评估等级
EVALUATION_LEVELS = {
    "excellent": "优秀",
    "good": "良好",
    "average": "一般",
    "poor": "较差"
}

# 生成面试问题的函数
def generate_questions(job_type, experience, question_count=3):
    """
    根据岗位类型和工作经验生成面试问题
    
    Args:
        job_type: 岗位类型，如 "java_backend", "web_frontend", "python_algorithm"
        experience: 工作经验，如 "实习", "应届", "1-3年工作经验", "3年以上工作经验"
        question_count: 生成的问题数量
    
    Returns:
        面试问题列表
    """
    import random
    
    questions = []
    job_questions = JOB_QUESTIONS.get(job_type, {})
    
    # 根据工作经验确定问题难度
    difficulty = "初级" if experience in ["实习", "应届"] else "中级" if experience == "1-3年工作经验" else "高级"
    
    # 从不同题型中随机选择问题
    question_types = list(job_questions.keys())
    for i in range(question_count):
        # 轮询不同题型
        q_type = question_types[i % len(question_types)]
        type_questions = job_questions.get(q_type, [])
        if type_questions:
            # 随机选择一个问题
            question = random.choice(type_questions)
            # 根据难度调整问题
            if difficulty == "高级":
                question = f"{question}（请详细说明并举例）"
            questions.append(question)
    
    return questions

# 获取岗位技术栈
def get_job_tech_stack(job_type):
    """
    获取指定岗位的核心技术栈
    
    Args:
        job_type: 岗位类型
    
    Returns:
        技术栈列表
    """
    return JOB_TECH_STACKS.get(job_type, [])

# 获取评估标准
def get_evaluation_criteria():
    """
    获取面试评估标准
    
    Returns:
        评估标准字典
    """
    return EVALUATION_CRITERIA

# 获取学习资源
def get_learning_resources(job_type):
    """
    获取指定岗位的学习资源
    
    Args:
        job_type: 岗位类型
    
    Returns:
        学习资源字典
    """
    return LEARNING_RESOURCES.get(job_type, {})

# 获取优秀回答范例
def get_excellent_answer(job_type, question):
    """
    获取指定问题的优秀回答范例
    
    Args:
        job_type: 岗位类型
        question: 面试问题
    
    Returns:
        优秀回答范例
    """
    job_answers = EXCELLENT_ANSWERS.get(job_type, {})
    return job_answers.get(question, "")

# 获取岗位常见面试考点
def get_job_key_points(job_type):
    """
    获取指定岗位的常见面试考点
    
    Args:
        job_type: 岗位类型
    
    Returns:
        面试考点列表
    """
    return JOB_KEY_POINTS.get(job_type, [])
