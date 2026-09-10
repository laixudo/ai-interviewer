# -*- coding: utf-8 -*-
"""
面试综合评估报告生成API
整合对话评估、简历评价、面部分析，生成完整的面试评估报告
"""

# 在main.py中添加此API端点
api_code = '''

class ComprehensiveReportRequest(BaseModel):
    interview_id: int

@app.post("/api/interview/comprehensive-report")
async def generate_comprehensive_report(request: ComprehensiveReportRequest):
    """生成综合评估报告（整合对话+简历+面部分析）"""
    try:
        import json as json_lib

        interview_id = request.interview_id

        # 1. 获取面试基本信息
        interview = db.get_interview(interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")

        # 2. 获取对话评估报告
        evaluation_report = db.get_evaluation_report(interview_id)

        # 3. 获取能力提升计划
        improvement_plan = db.get_improvement_plan(interview_id)

        # 4. 获取简历评价
        resume_evaluation = db.get_resume_evaluation(interview_id)

        # 5. 获取面部分析汇总
        face_summary = db.get_face_analysis_summary(interview_id)

        # 6. 计算综合评分
        total_score = 0
        score_count = 0

        if evaluation_report and evaluation_report.get('overall_score'):
            total_score += evaluation_report['overall_score']
            score_count += 1

        if resume_evaluation and resume_evaluation.get('overall_score'):
            total_score += resume_evaluation['overall_score']
            score_count += 1

        if face_summary and face_summary.get('avg_confidence'):
            total_score += face_summary['avg_confidence']
            score_count += 1

        final_score = round(total_score / score_count, 1) if score_count > 0 else 0

        # 7. 生成综合建议
        suggestions = []

        if face_summary:
            if face_summary.get('dominant_emotion') == '紧张':
                suggestions.append("建议：在面试中保持放松心态，可以尝试深呼吸和积极自我暗示")
            elif face_summary.get('dominant_emotion') == '焦虑':
                suggestions.append("建议：面试前做好充分准备，熟悉岗位要求和公司背景")

            if face_summary.get('dominant_focus') == '走神':
                suggestions.append("建议：面试时保持专注，认真倾听面试官的问题")

        if resume_evaluation:
            improvements = resume_evaluation.get('improvements', [])
            if improvements:
                for imp in improvements[:2]:
                    suggestions.append(f"简历优化：{imp}")

        if evaluation_report:
            suggestions_from_report = evaluation_report.get('improvement_suggestions', [])
            for suggestion in suggestions_from_report[:3]:
                suggestions.append(f"面试技巧：{suggestion}")

        # 8. 组装综合报告
        comprehensive_report = {
            "interview_id": interview_id,
            "final_score": final_score,
            "interview_info": {
                "position": interview.get('position'),
                "round": interview.get('round_info'),
                "duration": interview.get('duration'),
                "status": interview.get('status')
            },
            "conversation_evaluation": evaluation_report,
            "resume_evaluation": resume_evaluation,
            "face_analysis": face_summary,
            "improvement_plan": improvement_plan,
            "comprehensive_suggestions": suggestions,
            "overall_assessment": generate_overall_assessment(final_score, face_summary, resume_evaluation)
        }

        return comprehensive_report

    except Exception as e:
        print(f"生成综合报告失败: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"生成综合报告失败: {str(e)}"}


def generate_overall_assessment(score, face_summary, resume_evaluation):
    """生成综合评语"""
    if score >= 85:
        level = "优秀"
        description = "您在此次面试中表现优异，综合素质出众，建议重点关注此候选人。"
    elif score >= 70:
        level = "良好"
        description = "您在此次面试中表现良好，具备岗位所需的核心能力，建议进入下一轮面试。"
    elif score >= 60:
        level = "一般"
        description = "您在此次面试中表现一般，部分能力需要进一步提升，建议综合考虑。"
    else:
        level = "需改进"
        description = "您在此次面试中需要较大改进，建议先提升相关能力后再尝试面试。"

    return {
        "level": level,
        "description": description
    }


@app.get("/api/interview/full-evaluation/{interview_id}")
async def get_full_evaluation(interview_id: int):
    """获取完整评估报告"""
    try:
        import json as json_lib

        interview = db.get_interview(interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")

        evaluation_report = db.get_evaluation_report(interview_id)
        improvement_plan = db.get_improvement_plan(interview_id)
        resume_evaluation = db.get_resume_evaluation(interview_id)
        face_analyses = db.get_face_analyses(interview_id)
        face_summary = db.get_face_analysis_summary(interview_id)

        return {
            "status": "success",
            "interview": {
                "id": interview.get('id'),
                "position": interview.get('position'),
                "round_info": interview.get('round_info'),
                "duration": interview.get('duration'),
                "status": interview.get('status'),
                "created_at": interview.get('created_at')
            },
            "conversation_evaluation": evaluation_report,
            "improvement_plan": improvement_plan,
            "resume_evaluation": resume_evaluation,
            "face_analyses": face_analyses,
            "face_summary": face_summary
        }
    except Exception as e:
        print(f"获取完整评估失败: {e}")
        return {"error": f"获取完整评估失败: {str(e)}"}
'''

# 检查是否已添加
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if '/api/interview/comprehensive-report' in content:
    print("综合评估报告API已存在")
else:
    with open('main.py', 'a', encoding='utf-8') as f:
        f.write(api_code)
    print("综合评估报告API添加成功")
