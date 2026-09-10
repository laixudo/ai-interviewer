class AbilityImprover:
    def __init__(self):
        pass
    
    def generate_improvement_plan(self, job_type, evaluation_report):
        """生成能力提升计划"""
        # 分析能力短板
        weaknesses = self._identify_weaknesses(evaluation_report)
        
        # 生成提升建议
        suggestions = self._generate_suggestions(weaknesses, job_type)
        
        # 推荐学习资源
        resources = self._recommend_resources(job_type, weaknesses)
        
        # 生成30天学习计划
        learning_plan = self._generate_learning_plan(weaknesses, job_type)
        
        # 构建提升计划
        improvement_plan = {
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "resources": resources,
            "learning_plan": learning_plan
        }
        
        return improvement_plan
    
    def _identify_weaknesses(self, evaluation_report):
        """分析能力短板"""
        weaknesses = []
        
        # 分析内容评估
        content_evaluation = evaluation_report.get("content_evaluation", {})
        if content_evaluation.get("technical", {}).get("score", 0) < 80:
            weaknesses.append("技术知识掌握不足")
        if content_evaluation.get("logic", {}).get("score", 0) < 80:
            weaknesses.append("逻辑思维能力需要提升")
        if content_evaluation.get("communication", {}).get("score", 0) < 80:
            weaknesses.append("沟通表达能力需要加强")
        
        # 分析表达评估
        expression_evaluation = evaluation_report.get("expression_evaluation", {})
        if expression_evaluation.get("clarity", {}).get("score", 0) < 80:
            weaknesses.append("表达清晰度需要提高")
        if expression_evaluation.get("confidence", {}).get("score", 0) < 80:
            weaknesses.append("自信度需要增强")
        
        # 确保至少有一个短板
        if not weaknesses:
            weaknesses.append("整体能力需要进一步提升")
        
        return weaknesses
    
    def _generate_suggestions(self, weaknesses, job_type):
        """生成提升建议"""
        suggestions = []
        
        if "技术知识掌握不足" in weaknesses:
            suggestions.append("系统学习核心技术栈，重点关注面试高频考点")
        if "逻辑思维能力需要提升" in weaknesses:
            suggestions.append("多做算法题和逻辑题，提高分析问题的能力")
        if "沟通表达能力需要加强" in weaknesses:
            suggestions.append("练习演讲和表达，提高语言组织能力")
        if "表达清晰度需要提高" in weaknesses:
            suggestions.append("注意回答的条理性，使用结构化的表达方式")
        if "自信度需要增强" in weaknesses:
            suggestions.append("多进行模拟面试，提高面试的自信心")
        
        # 通用建议
        suggestions.append("定期复习和总结，巩固所学知识")
        suggestions.append("关注行业动态，了解最新技术趋势")
        
        return suggestions
    
    def _recommend_resources(self, job_type, weaknesses):
        """推荐学习资源"""
        resources = []
        
        # 根据岗位类型推荐资源
        if job_type == "java_backend":
            resources.extend([
                "《Java核心技术》系列书籍",
                "Spring Boot官方文档",
                "LeetCode算法题",
                "Java并发编程实战"
            ])
        elif job_type == "web_frontend":
            resources.extend([
                "《JavaScript高级程序设计》",
                "React官方文档",
                "前端性能优化指南",
                "CSS权威指南"
            ])
        elif job_type == "python_algorithm":
            resources.extend([
                "《Python编程：从入门到实践》",
                "《算法导论》",
                "机器学习实战",
                "Python数据科学手册"
            ])
        
        # 根据短板推荐资源
        if "沟通表达能力需要加强" in weaknesses:
            resources.append("《演讲的力量》")
        if "逻辑思维能力需要提升" in weaknesses:
            resources.append("《思考，快与慢》")
        
        return resources
    
    def _generate_learning_plan(self, weaknesses, job_type):
        """生成30天学习计划"""
        learning_plan = []
        
        # 第1周：基础强化
        week1 = {
            "week": 1,
            "title": "基础强化",
            "tasks": [
                "系统学习核心技术概念",
                "完成基础练习题",
                "阅读技术文档",
                "每天进行15分钟的表达练习"
            ]
        }
        learning_plan.append(week1)
        
        # 第2周：技能提升
        week2 = {
            "week": 2,
            "title": "技能提升",
            "tasks": [
                "学习面试高频考点",
                "完成中等难度的练习题",
                "模拟面试1次",
                "分析面试常见问题"
            ]
        }
        learning_plan.append(week2)
        
        # 第3周：实战演练
        week3 = {
            "week": 3,
            "title": "实战演练",
            "tasks": [
                "参与实际项目或练习项目",
                "模拟面试2次",
                "分析和总结面试表现",
                "优化回答技巧"
            ]
        }
        learning_plan.append(week3)
        
        # 第4周：综合提升
        week4 = {
            "week": 4,
            "title": "综合提升",
            "tasks": [
                "系统复习所有知识点",
                "模拟面试3次",
                "总结提升计划的执行情况",
                "制定长期学习计划"
            ]
        }
        learning_plan.append(week4)
        
        return learning_plan