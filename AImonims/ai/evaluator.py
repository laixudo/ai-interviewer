# 面试表现多维度分析模块

from data.job_knowledge_base import EVALUATION_CRITERIA, EVALUATION_LEVELS

class InterviewEvaluator:
    """
    面试表现评估器
    """
    
    def __init__(self):
        self.criteria = EVALUATION_CRITERIA
        self.levels = EVALUATION_LEVELS
    
    def evaluate_content(self, job_type, questions, answers):
        """
        评估回答内容
        
        Args:
            job_type: 岗位类型
            questions: 面试问题列表
            answers: 回答列表
        
        Returns:
            内容评估结果
        """
        evaluation = {}
        
        for criterion in self.criteria:
            # 简单的评估逻辑，实际应用中可以使用大模型进行深度分析
            score = self._calculate_score(job_type, questions, answers, criterion)
            level = self._get_level(score)
            evaluation[criterion] = {
                "score": score,
                "level": level,
                "comment": self._generate_comment(criterion, level)
            }
        
        return evaluation
    
    def evaluate_expression(self, audio_data=None, text_answers=None):
        """
        评估表达能力
        
        Args:
            audio_data: 语音数据（可选）
            text_answers: 文字回答（可选）
        
        Returns:
            表达评估结果
        """
        expression_evaluation = {
            "speech_rate": self._evaluate_speech_rate(text_answers),
            "clarity": self._evaluate_clarity(text_answers),
            "confidence": self._evaluate_confidence(text_answers)
        }
        
        return expression_evaluation
    
    def generate_report(self, job_type, questions, answers, audio_data=None):
        """
        生成综合评估报告
        
        Args:
            job_type: 岗位类型
            questions: 面试问题列表
            answers: 回答列表
            audio_data: 语音数据（可选）
        
        Returns:
            综合评估报告
        """
        # 评估内容
        content_evaluation = self.evaluate_content(job_type, questions, answers)
        
        # 评估表达
        expression_evaluation = self.evaluate_expression(audio_data, answers)
        
        # 计算综合得分
        overall_score = self._calculate_overall_score(content_evaluation, expression_evaluation)
        overall_level = self._get_level(overall_score)
        
        # 生成改进建议
        suggestions = self._generate_suggestions(content_evaluation, expression_evaluation)
        
        # 生成亮点分析
        highlights = self._generate_highlights(content_evaluation, expression_evaluation)
        
        # 生成综合报告
        report = {
            "overall_score": overall_score,
            "overall_level": overall_level,
            "content_evaluation": content_evaluation,
            "expression_evaluation": expression_evaluation,
            "highlights": highlights,
            "suggestions": suggestions,
            "timestamp": "2026-03-20"
        }
        
        return report
    
    def _calculate_score(self, job_type, questions, answers, criterion):
        """
        计算单项得分
        
        Args:
            job_type: 岗位类型
            questions: 面试问题列表
            answers: 回答列表
            criterion: 评估标准
        
        Returns:
            得分（0-100）
        """
        # 简单的得分计算逻辑
        # 实际应用中可以使用大模型进行深度分析
        base_score = 60
        
        # 根据回答长度和质量调整得分
        for answer in answers:
            if len(answer) > 100:
                base_score += 10
            elif len(answer) < 50:
                base_score -= 10
        
        # 根据岗位类型调整得分
        if job_type == "java_backend":
            base_score += 5
        elif job_type == "web_frontend":
            base_score += 3
        
        # 确保得分在0-100之间
        return min(100, max(0, base_score))
    
    def _get_level(self, score):
        """
        根据得分获取评估等级
        
        Args:
            score: 得分
        
        Returns:
            评估等级
        """
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 60:
            return "average"
        else:
            return "poor"
    
    def _generate_comment(self, criterion, level):
        """
        生成评估评语
        
        Args:
            criterion: 评估标准
            level: 评估等级
        
        Returns:
            评语
        """
        comments = {
            "technical_accuracy": {
                "excellent": "技术回答准确，知识点掌握扎实",
                "good": "技术回答基本正确，有一定的知识储备",
                "average": "技术回答存在一些错误，需要加强知识学习",
                "poor": "技术回答错误较多，知识掌握不扎实"
            },
            "knowledge_depth": {
                "excellent": "知识理解深入，能够举一反三",
                "good": "知识理解较深入，能够基本应用",
                "average": "知识理解一般，需要加深学习",
                "poor": "知识理解肤浅，需要系统学习"
            },
            "logical_thinking": {
                "excellent": "逻辑清晰，条理分明",
                "good": "逻辑基本清晰，表达有条理",
                "average": "逻辑一般，表达不够清晰",
                "poor": "逻辑混乱，表达不清晰"
            },
            "communication_skills": {
                "excellent": "沟通表达流畅，能够清晰传达想法",
                "good": "沟通表达基本流畅，能够表达想法",
                "average": "沟通表达一般，需要提高表达能力",
                "poor": "沟通表达不畅，难以传达想法"
            },
            "problem_solving": {
                "excellent": "问题解决能力强，能够灵活应对挑战",
                "good": "问题解决能力较好，能够应对基本挑战",
                "average": "问题解决能力一般，需要提高",
                "poor": "问题解决能力较弱，需要加强训练"
            },
            "coding_ability": {
                "excellent": "编码能力强，代码质量高",
                "good": "编码能力较好，代码质量较高",
                "average": "编码能力一般，代码质量需要提高",
                "poor": "编码能力较弱，需要加强练习"
            },
            "project_experience": {
                "excellent": "项目经验丰富，能够详细描述项目细节",
                "good": "项目经验较多，能够基本描述项目情况",
                "average": "项目经验一般，需要积累更多经验",
                "poor": "项目经验较少，需要增加实践经验"
            },
            "learning_ability": {
                "excellent": "学习能力强，能够快速掌握新技术",
                "good": "学习能力较好，能够掌握基本技术",
                "average": "学习能力一般，需要提高学习效率",
                "poor": "学习能力较弱，需要加强学习方法"
            }
        }
        
        return comments.get(criterion, {}).get(level, "")
    
    def _evaluate_speech_rate(self, text_answers):
        """
        评估语速
        
        Args:
            text_answers: 文字回答
        
        Returns:
            语速评估结果
        """
        if not text_answers:
            return {"score": 0, "comment": "无回答内容"}
        
        # 简单的语速评估逻辑
        # 实际应用中可以通过语音识别分析语速
        average_length = sum(len(answer) for answer in text_answers) / len(text_answers)
        
        if average_length > 150:
            return {"score": 85, "comment": "语速适中，表达充分"}
        elif average_length > 80:
            return {"score": 70, "comment": "语速基本适中"}
        else:
            return {"score": 50, "comment": "语速偏快，表达不够充分"}
    
    def _evaluate_clarity(self, text_answers):
        """
        评估清晰度
        
        Args:
            text_answers: 文字回答
        
        Returns:
            清晰度评估结果
        """
        if not text_answers:
            return {"score": 0, "comment": "无回答内容"}
        
        # 简单的清晰度评估逻辑
        # 实际应用中可以通过语音识别分析清晰度
        clarity_score = 70
        
        for answer in text_answers:
            if "。" in answer and "，" in answer:
                clarity_score += 10
            elif "。" not in answer and "，" not in answer:
                clarity_score -= 10
        
        return {"score": min(100, max(0, clarity_score)), "comment": "表达清晰度一般"}
    
    def _evaluate_confidence(self, text_answers):
        """
        评估自信度
        
        Args:
            text_answers: 文字回答
        
        Returns:
            自信度评估结果
        """
        if not text_answers:
            return {"score": 0, "comment": "无回答内容"}
        
        # 简单的自信度评估逻辑
        # 实际应用中可以通过语音识别和情感分析评估自信度
        confidence_score = 70
        
        for answer in text_answers:
            if len(answer) > 100:
                confidence_score += 10
            elif len(answer) < 50:
                confidence_score -= 10
        
        return {"score": min(100, max(0, confidence_score)), "comment": "自信度一般"}
    
    def _calculate_overall_score(self, content_evaluation, expression_evaluation):
        """
        计算综合得分
        
        Args:
            content_evaluation: 内容评估结果
            expression_evaluation: 表达评估结果
        
        Returns:
            综合得分
        """
        # 计算内容得分平均值
        content_scores = [item["score"] for item in content_evaluation.values()]
        content_average = sum(content_scores) / len(content_scores) if content_scores else 0
        
        # 计算表达得分平均值
        expression_scores = [item["score"] for item in expression_evaluation.values()]
        expression_average = sum(expression_scores) / len(expression_scores) if expression_scores else 0
        
        # 综合得分 = 内容得分 * 0.7 + 表达得分 * 0.3
        overall_score = content_average * 0.7 + expression_average * 0.3
        
        return round(overall_score, 2)
    
    def _generate_suggestions(self, content_evaluation, expression_evaluation):
        """
        生成改进建议
        
        Args:
            content_evaluation: 内容评估结果
            expression_evaluation: 表达评估结果
        
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 根据内容评估生成建议
        for criterion, result in content_evaluation.items():
            if result["level"] in ["average", "poor"]:
                suggestions.append(f"{self.criteria[criterion]}方面需要加强，建议多学习相关知识，提高{self.criteria[criterion]}能力")
        
        # 根据表达评估生成建议
        if expression_evaluation["speech_rate"]["score"] < 60:
            suggestions.append("语速方面需要调整，建议练习控制语速，确保表达清晰")
        
        if expression_evaluation["clarity"]["score"] < 60:
            suggestions.append("表达清晰度需要提高，建议多练习表达，注意语句的逻辑性和条理性")
        
        if expression_evaluation["confidence"]["score"] < 60:
            suggestions.append("自信度需要提升，建议多进行模拟面试练习，增强自信心")
        
        return suggestions
    
    def _generate_highlights(self, content_evaluation, expression_evaluation):
        """
        生成亮点分析
        
        Args:
            content_evaluation: 内容评估结果
            expression_evaluation: 表达评估结果
        
        Returns:
            亮点列表
        """
        highlights = []
        
        # 根据内容评估生成亮点
        for criterion, result in content_evaluation.items():
            if result["level"] in ["excellent", "good"]:
                highlights.append(f"{self.criteria[criterion]}方面表现优秀，继续保持")
        
        # 根据表达评估生成亮点
        if expression_evaluation["speech_rate"]["score"] > 80:
            highlights.append("语速适中，表达流畅")
        
        if expression_evaluation["clarity"]["score"] > 80:
            highlights.append("表达清晰，逻辑分明")
        
        if expression_evaluation["confidence"]["score"] > 80:
            highlights.append("自信度高，表现从容")
        
        return highlights

# 测试评估器
if __name__ == "__main__":
    evaluator = InterviewEvaluator()
    
    # 测试数据
    job_type = "java_backend"
    questions = [
        "请解释Java中的多线程原理",
        "什么是Java中的垃圾回收机制？有哪些垃圾回收算法？",
        "请详细介绍Spring框架的核心组件"
    ]
    answers = [
        "Java中的多线程原理是通过Thread类和Runnable接口实现的。线程是程序执行的最小单位，多线程可以提高程序的执行效率。在Java中，我们可以通过继承Thread类或实现Runnable接口来创建线程。线程的生命周期包括新建、就绪、运行、阻塞和死亡五个状态。多线程编程需要注意线程安全问题，通常可以通过synchronized关键字、Lock接口或原子类来保证线程安全。",
        "Java中的垃圾回收机制是自动管理内存的一种机制，它可以自动回收不再使用的对象，避免内存泄漏。常见的垃圾回收算法包括标记-清除算法、复制算法、标记-整理算法和分代收集算法。不同的垃圾回收器使用不同的算法，例如Serial收集器使用复制算法，Parallel收集器使用标记-整理算法，CMS收集器使用标记-清除算法。",
        "Spring框架的核心组件包括IoC容器、AOP、MVC等。IoC容器是Spring的核心，它负责管理对象的创建和依赖注入。AOP（面向切面编程）可以在不修改原有代码的情况下，为程序添加额外的功能，例如事务管理、日志记录等。MVC（模型-视图-控制器）是一种设计模式，Spring MVC是Spring框架的Web层实现，它可以帮助我们构建Web应用程序。"
    ]
    
    # 生成评估报告
    report = evaluator.generate_report(job_type, questions, answers)
    print("评估报告:")
    print(f"综合得分: {report['overall_score']}")
    print(f"综合等级: {report['overall_level']}")
    print("\n内容评估:")
    for criterion, result in report['content_evaluation'].items():
        print(f"{evaluator.criteria[criterion]}: {result['score']}分, {evaluator.levels[result['level']]}, {result['comment']}")
    print("\n表达评估:")
    for item, result in report['expression_evaluation'].items():
        print(f"{item}: {result['score']}分, {result['comment']}")
    print("\n亮点:")
    for highlight in report['highlights']:
        print(f"- {highlight}")
    print("\n改进建议:")
    for suggestion in report['suggestions']:
        print(f"- {suggestion}")
