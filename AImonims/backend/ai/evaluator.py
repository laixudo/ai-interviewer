class InterviewEvaluator:
    def __init__(self):
        pass
    
    def generate_report(self, job_type, questions, answers):
        """生成面试评估报告"""
        # 计算内容评估分数
        content_scores = self._evaluate_content(job_type, questions, answers)
        
        # 计算表达评估分数
        expression_scores = self._evaluate_expression(answers)
        
        # 计算综合得分
        overall_score = self._calculate_overall_score(content_scores, expression_scores)
        
        # 确定综合等级
        overall_level = self._get_level(overall_score)
        
        # 生成亮点和改进建议
        highlights = self._generate_highlights(content_scores, expression_scores)
        suggestions = self._generate_suggestions(content_scores, expression_scores)
        
        # 构建评估报告
        report = {
            "overall_score": overall_score,
            "overall_level": overall_level,
            "timestamp": self._get_current_time(),
            "content_evaluation": content_scores,
            "expression_evaluation": expression_scores,
            "highlights": highlights,
            "suggestions": suggestions
        }
        
        return report
    
    def _evaluate_content(self, job_type, questions, answers):
        """评估内容质量"""
        # 简单的评估逻辑，实际应用中可以使用NLP模型
        
        # 基础分数
        technical_score = 60
        logic_score = 60
        communication_score = 60
        
        # 惩罚简短无内容的回答
        for answer in answers:
            if len(answer) < 10 or answer.strip() in ["不知道", "不清楚", "不会", "没学过"]:
                technical_score -= 20
                logic_score -= 15
                communication_score -= 10
            else:
                # 奖励有内容的回答
                technical_score += min(10, len(answer) // 20)
                logic_score += min(10, len(answer.split('.')))
                communication_score += min(10, sum(1 for char in answer if char in [',', '，', ';', '；', '.', '。']))
        
        # 确保分数在0-100之间
        technical_score = min(100, max(0, technical_score))
        logic_score = min(100, max(0, logic_score))
        communication_score = min(100, max(0, communication_score))
        
        return {
            "technical": {"comment": "技术知识掌握程度", "score": technical_score},
            "logic": {"comment": "逻辑思维清晰度", "score": logic_score},
            "communication": {"comment": "沟通表达能力", "score": communication_score}
        }
    
    def _evaluate_expression(self, answers):
        """评估表达能力"""
        # 简单的评估逻辑
        clarity_score = 70
        confidence_score = 70
        speed_score = 90  # 假设语速适中
        
        # 惩罚简短无内容的回答
        for answer in answers:
            if len(answer) < 10 or answer.strip() in ["不知道", "不清楚", "不会", "没学过"]:
                clarity_score -= 15
                confidence_score -= 20
            else:
                # 奖励有内容的回答
                clarity_score += min(15, len(answer) // 15)
                confidence_score += min(15, len(answer) // 20)
        
        # 确保分数在0-100之间
        clarity_score = min(100, max(0, clarity_score))
        confidence_score = min(100, max(0, confidence_score))
        speed_score = min(100, max(0, speed_score))
        
        return {
            "clarity": {"comment": "表达清晰度", "score": clarity_score},
            "confidence": {"comment": "自信度", "score": confidence_score},
            "speed": {"comment": "语速适中", "score": speed_score}
        }
    
    def _calculate_overall_score(self, content_scores, expression_scores):
        """计算综合得分"""
        # 内容评估占60%，表达评估占40%
        content_total = sum(item['score'] for item in content_scores.values()) / len(content_scores)
        expression_total = sum(item['score'] for item in expression_scores.values()) / len(expression_scores)
        
        overall = content_total * 0.6 + expression_total * 0.4
        return round(overall)
    
    def _get_level(self, score):
        """根据分数确定等级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "需改进"
    
    def _generate_highlights(self, content_scores, expression_scores):
        """生成亮点"""
        highlights = []
        
        if content_scores['technical']['score'] >= 85:
            highlights.append("技术知识掌握扎实")
        if content_scores['logic']['score'] >= 85:
            highlights.append("逻辑思维清晰")
        if content_scores['communication']['score'] >= 85:
            highlights.append("沟通表达流畅")
        if expression_scores['clarity']['score'] >= 85:
            highlights.append("表达清晰准确")
        if expression_scores['confidence']['score'] >= 85:
            highlights.append("回答自信从容")
        
        # 确保至少有一个亮点
        if not highlights:
            highlights.append("面试态度认真")
        
        return highlights
    
    def _generate_suggestions(self, content_scores, expression_scores):
        """生成改进建议"""
        suggestions = []
        
        if content_scores['technical']['score'] < 80:
            suggestions.append("加强技术知识的学习和掌握")
        if content_scores['logic']['score'] < 80:
            suggestions.append("提高逻辑思维能力，注意回答的条理性")
        if content_scores['communication']['score'] < 80:
            suggestions.append("加强沟通表达能力，提高回答的流畅度")
        if expression_scores['clarity']['score'] < 80:
            suggestions.append("注意表达的清晰度，避免模糊不清的回答")
        if expression_scores['confidence']['score'] < 80:
            suggestions.append("增强自信，保持良好的面试状态")
        
        # 确保至少有一个建议
        if not suggestions:
            suggestions.append("继续保持良好的面试表现")
        
        return suggestions
    
    def _get_current_time(self):
        """获取当前时间"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")