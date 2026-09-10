# 能力提升反馈模块

from data.job_knowledge_base import JOB_TECH_STACKS

class AbilityImprover:
    """
    能力提升建议生成器
    """
    
    def __init__(self):
        self.tech_stacks = JOB_TECH_STACKS
        self.learning_resources = self._load_learning_resources()
    
    def generate_improvement_plan(self, job_type, evaluation_report):
        """
        生成个性化提升计划
        
        Args:
            job_type: 岗位类型
            evaluation_report: 评估报告
        
        Returns:
            提升计划
        """
        # 分析能力短板
        weaknesses = self._identify_weaknesses(evaluation_report)
        
        # 生成提升建议
        suggestions = self._generate_suggestions(job_type, weaknesses)
        
        # 推荐学习资源
        resources = self._recommend_resources(job_type, weaknesses)
        
        # 生成学习计划
        learning_plan = self._generate_learning_plan(job_type, weaknesses)
        
        # 构建提升计划
        improvement_plan = {
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "resources": resources,
            "learning_plan": learning_plan,
            "timestamp": "2026-03-20"
        }
        
        return improvement_plan
    
    def _identify_weaknesses(self, evaluation_report):
        """
        识别能力短板
        
        Args:
            evaluation_report: 评估报告
        
        Returns:
            能力短板列表
        """
        weaknesses = []
        
        # 分析内容评估
        content_evaluation = evaluation_report.get("content_evaluation", {})
        for criterion, result in content_evaluation.items():
            if result.get("level") in ["average", "poor"]:
                weaknesses.append(criterion)
        
        # 分析表达评估
        expression_evaluation = evaluation_report.get("expression_evaluation", {})
        for item, result in expression_evaluation.items():
            if result.get("score") < 60:
                weaknesses.append(f"expression_{item}")
        
        return weaknesses
    
    def _generate_suggestions(self, job_type, weaknesses):
        """
        生成提升建议
        
        Args:
            job_type: 岗位类型
            weaknesses: 能力短板列表
        
        Returns:
            提升建议列表
        """
        suggestions = []
        
        # 根据岗位类型和能力短板生成建议
        for weakness in weaknesses:
            if weakness == "technical_accuracy":
                suggestions.append("加强技术知识学习，重点掌握岗位核心技术栈")
            elif weakness == "knowledge_depth":
                suggestions.append("深入学习技术原理，理解底层实现")
            elif weakness == "logical_thinking":
                suggestions.append("多进行逻辑思维训练，提高问题分析能力")
            elif weakness == "communication_skills":
                suggestions.append("多练习表达，提高沟通能力")
            elif weakness == "problem_solving":
                suggestions.append("多做算法题和编程练习，提高问题解决能力")
            elif weakness == "coding_ability":
                suggestions.append("多编写代码，提高编码能力和代码质量")
            elif weakness == "project_experience":
                suggestions.append("参与更多项目实践，积累项目经验")
            elif weakness == "learning_ability":
                suggestions.append("学习新技能和新技术，提高学习能力")
            elif weakness == "expression_speech_rate":
                suggestions.append("练习控制语速，确保表达清晰")
            elif weakness == "expression_clarity":
                suggestions.append("练习表达，注意语句的逻辑性和条理性")
            elif weakness == "expression_confidence":
                suggestions.append("多进行模拟面试练习，增强自信心")
        
        # 根据岗位类型添加特定建议
        if job_type == "java_backend":
            suggestions.append("重点学习Spring Boot、Spring Cloud等框架")
            suggestions.append("加强数据库优化和性能调优知识")
        elif job_type == "web_frontend":
            suggestions.append("重点学习React、Vue等前端框架")
            suggestions.append("加强前端性能优化和用户体验设计")
        elif job_type == "python_algorithm":
            suggestions.append("重点学习机器学习和深度学习算法")
            suggestions.append("加强数据结构和算法设计能力")
        
        return suggestions
    
    def _recommend_resources(self, job_type, weaknesses):
        """
        推荐学习资源
        
        Args:
            job_type: 岗位类型
            weaknesses: 能力短板列表
        
        Returns:
            学习资源列表
        """
        resources = []
        
        # 根据岗位类型和能力短板推荐资源
        for weakness in weaknesses:
            if weakness in ["technical_accuracy", "knowledge_depth"]:
                resources.extend(self.learning_resources.get(f"{job_type}_technical", []))
            elif weakness in ["problem_solving", "coding_ability"]:
                resources.extend(self.learning_resources.get("coding_practice", []))
            elif weakness in ["communication_skills", "expression_speech_rate", "expression_clarity", "expression_confidence"]:
                resources.extend(self.learning_resources.get("communication", []))
        
        # 去重
        resources = list(set(resources))
        
        return resources[:10]  # 限制返回10个资源
    
    def _generate_learning_plan(self, job_type, weaknesses):
        """
        生成学习计划
        
        Args:
            job_type: 岗位类型
            weaknesses: 能力短板列表
        
        Returns:
            学习计划
        """
        # 生成30天学习计划
        plan = []
        
        # 第一周：基础巩固
        plan.append({
            "week": 1,
            "title": "基础巩固",
            "tasks": [
                "复习岗位核心技术栈",
                "完成基础编程练习",
                "学习沟通表达技巧"
            ]
        })
        
        # 第二周：技能提升
        plan.append({
            "week": 2,
            "title": "技能提升",
            "tasks": [
                "深入学习技术原理",
                "完成中级编程练习",
                "练习模拟面试"
            ]
        })
        
        # 第三周：实战训练
        plan.append({
            "week": 3,
            "title": "实战训练",
            "tasks": [
                "参与项目实践",
                "完成高级编程练习",
                "进行多轮模拟面试"
            ]
        })
        
        # 第四周：综合提升
        plan.append({
            "week": 4,
            "title": "综合提升",
            "tasks": [
                "总结学习成果",
                "进行最终模拟面试",
                "制定长期学习计划"
            ]
        })
        
        return plan
    
    def _load_learning_resources(self):
        """
        加载学习资源
        
        Returns:
            学习资源字典
        """
        return {
            "java_backend_technical": [
                "《深入理解Java虚拟机》",
                "《Spring实战》",
                "《MySQL高性能》",
                "《分布式系统设计原理》",
                "Java官方文档"
            ],
            "web_frontend_technical": [
                "《JavaScript高级程序设计》",
                "《React实战》",
                "《CSS权威指南》",
                "《前端性能优化》",
                "MDN Web Docs"
            ],
            "python_algorithm_technical": [
                "《Python编程：从入门到实践》",
                "《机器学习实战》",
                "《算法导论》",
                "《深度学习》",
                "Python官方文档"
            ],
            "coding_practice": [
                "LeetCode",
                "GitHub",
                "Codewars",
                "HackerRank",
                "Topcoder"
            ],
            "communication": [
                "《沟通的方法》",
                "《演讲的力量》",
                "《非暴力沟通》",
                "《关键对话》",
                "Toastmasters国际演讲俱乐部"
            ]
        }

# 测试提升建议生成器
if __name__ == "__main__":
    improver = AbilityImprover()
    
    # 测试数据
    job_type = "java_backend"
    evaluation_report = {
        "content_evaluation": {
            "technical_accuracy": {"level": "average", "score": 65},
            "knowledge_depth": {"level": "good", "score": 75},
            "logical_thinking": {"level": "excellent", "score": 90},
            "communication_skills": {"level": "average", "score": 60},
            "problem_solving": {"level": "good", "score": 70},
            "coding_ability": {"level": "poor", "score": 55},
            "project_experience": {"level": "good", "score": 80},
            "learning_ability": {"level": "excellent", "score": 85}
        },
        "expression_evaluation": {
            "speech_rate": {"score": 70},
            "clarity": {"score": 65},
            "confidence": {"score": 60}
        }
    }
    
    # 生成提升计划
    improvement_plan = improver.generate_improvement_plan(job_type, evaluation_report)
    print("提升计划:")
    print(f"能力短板: {improvement_plan['weaknesses']}")
    print("\n提升建议:")
    for suggestion in improvement_plan['suggestions']:
        print(f"- {suggestion}")
    print("\n推荐学习资源:")
    for resource in improvement_plan['resources']:
        print(f"- {resource}")
    print("\n学习计划:")
    for week_plan in improvement_plan['learning_plan']:
        print(f"第{week_plan['week']}周: {week_plan['title']}")
        for task in week_plan['tasks']:
            print(f"  - {task}")
