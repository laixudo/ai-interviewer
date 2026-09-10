
# 简单的修复脚本
import re

# 读取原始文件
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到问题区域：找到 '@app.websocket("/ws/{client_id}")' 的位置
search_pattern = r'@app\.websocket\("/ws/\{client_id\}"\)'
match = re.search(search_pattern, content)

if match:
    # 截断到这个位置之前
    content = content[:match.start()]

# 添加简历分析代码和主程序入口
additional_code = '''
# ==================== 简历分析相关功能 ====================

class ResumeExtractRequest(BaseModel):
    resume_text: str
    job_type: Optional[str] = "java_backend"


class ResumeEvaluationRequest(BaseModel):
    interview_id: int
    job_type: Optional[str] = "java_backend"


def extract_resume_info(resume_text, job_type):
    """使用AI提取简历的关键信息"""
    try:
        system_prompt = """你是一位专业的HR和简历分析专家。请从用户简历中提取以下关键信息，
并以JSON格式返回：
{
    "personal_info": {
        "name": "姓名",
        "phone": "联系电话",
        "email": "邮箱",
        "location": "所在城市"
    },
    "education": {
        "school": "毕业院校",
        "major": "专业",
        "degree": "学历",
        "graduate_time": "毕业时间"
    },
    "work_experience": [
        {
            "company": "公司名称",
            "position": "职位",
            "start_time": "入职时间",
            "end_time": "离职时间",
            "description": "工作描述"
        }
    ],
    "skills": {
        "technical": ["技术技能1", "技术技能2"],
        "soft": ["软技能1", "软技能2"]
    },
    "projects": [
        {
            "name": "项目名称",
            "role": "担任角色",
            "description": "项目描述",
            "tech_stack": ["技术栈1", "技术栈2"]
        }
    ],
    "highlights": ["个人亮点1", "个人亮点2"],
    "weaknesses": ["简历不足1", "简历不足2"]
}
要求：
1. 只提取简历中明确提到的信息，不确定的字段留空字符串或空数组
2. 如果某类信息（如工作经验）有多条，请全部提取
3. 保持JSON格式的正确性，不要使用markdown格式"""

        user_prompt = f"以下是候选人的简历，请提取关键信息：\\n{resume_text}"

        response = global_doubao_client.generate_response(
            system_prompt,
            user_prompt,
            temperature=0.3,
            max_tokens=2000
        )

        if response:
            import re
            json_match = re.search(r'\\{[\\s\\S]*\\}', response)
            if json_match:
                import json as json_lib
                return json_lib.loads(json_match.group())

    except Exception as e:
        print(f"简历信息提取失败: {e}")

    return {
        "personal_info": {"name": "", "phone": "", "email": "", "location": ""},
        "education": {"school": "", "major": "", "degree": "", "graduate_time": ""},
        "work_experience": [],
        "skills": {"technical": [], "soft": []},
        "projects": [],
        "highlights": [],
        "weaknesses": []
    }


def evaluate_resume_quality(resume_text, job_type, interview_id):
    """评价简历的制作质量"""
    try:
        system_prompt = """你是一位专业的HR和简历辅导专家。请从以下几个维度评价这份简历的制作质量：

1. 完整性（10分）：简历结构是否完整，关键信息是否齐全
2. 专业性（10分）：表述是否专业、是否有HR和面试官喜欢的关键词
3. 逻辑性（10分）：内容组织是否有条理，时间线是否清晰
4. 亮点突出（10分）：是否突出了个人优势和核心竞争力
5. 细节处理（10分）：排版、格式、错别字等细节是否处理到位

请以JSON格式返回：
{
    "overall_score": 总分（1-100）,
    "dimensions": {
        "completeness": {"score": 完整性得分, "comment": "评价内容"},
        "professionalism": {"score": 专业性得分, "comment": "评价内容"},
        "logic": {"score": 逻辑性得分, "comment": "评价内容"},
        "highlights": {"score": 亮点突出得分, "comment": "评价内容"},
        "details": {"score": 细节处理得分, "comment": "评价内容"}
    },
    "strengths": ["简历优点1", "简历优点2"],
    "improvements": ["改进建议1", "改进建议2"],
    "template_suggestion": "推荐的简历模板/结构建议"
}
要求：评价要具体、有建设性，能够帮助候选人改进简历"""

        user_prompt = f"以下是候选人的简历，请进行评价：\\n{resume_text}"

        response = global_doubao_client.generate_response(
            system_prompt,
            user_prompt,
            temperature=0.5,
            max_tokens=1500
        )

        if response:
            import re
            json_match = re.search(r'\\{[\\s\\S]*\\}', response)
            if json_match:
                import json as json_lib
                evaluation = json_lib.loads(json_match.group())
                
                db.save_resume_evaluation(
                    interview_id=interview_id,
                    overall_score=evaluation.get('overall_score', 0),
                    dimensions=json.dumps(evaluation.get('dimensions', {})),
                    strengths=json.dumps(evaluation.get('strengths', [])),
                    improvements=json.dumps(evaluation.get('improvements', [])),
                    template_suggestion=evaluation.get('template_suggestion', '')
                )
                
                return evaluation

    except Exception as e:
        print(f"简历评价失败: {e}")

    return {
        "overall_score": 60,
        "dimensions": {
            "completeness": {"score": 6, "comment": "简历基本完整，但信息可以更丰富"},
            "professionalism": {"score": 6, "comment": "表述基本清晰，可以更专业"},
            "logic": {"score": 6, "comment": "结构基本清晰，可以更有条理"},
            "highlights": {"score": 6, "comment": "有一些亮点，但可以更突出"},
            "details": {"score": 6, "comment": "细节处理基本到位"}
        },
        "strengths": ["简历内容完整", "结构清晰"],
        "improvements": ["可以增加更多项目细节", "突出个人核心竞争力"],
        "template_suggestion": "建议使用STAR法则描述项目经验"
    }


def generate_resume_based_questions(resume_info, job_type, question_count=3):
    """根据简历信息生成针对性的面试问题"""
    try:
        system_prompt = f"""你是一位专业的{job_type}面试官。请根据候选人的简历信息，生成{question_count}个有针对性的面试问题。

要求：
1. 问题要紧扣简历中的具体内容，如项目经验、技能、工作经历等
2. 问题要有深度，能够考察候选人的真实能力
3. 问题要自然，像真人面试官一样提问
4. 直接返回问题列表，用JSON格式：
{{
    "questions": [
        "问题1",
        "问题2",
        "问题3"
    ]
}}"""

        import json as json_lib
        resume_json = json_lib.dumps(resume_info, ensure_ascii=False)
        user_prompt = f"候选人简历信息：\\n{resume_json}\\n\\n请生成{question_count}个针对性问题。"

        response = global_doubao_client.generate_response(
            system_prompt,
            user_prompt,
            temperature=0.7,
            max_tokens=800
        )

        if response:
            import re
            json_match = re.search(r'\\{[\\s\\S]*\\}', response)
            if json_match:
                result = json_lib.loads(json_match.group())
                return result.get('questions', [])

    except Exception as e:
        print(f"生成简历相关问题失败: {e}")

    return [
        "请详细介绍一下你的一个核心项目经验？",
        "你在项目中遇到过哪些技术挑战？是如何解决的？",
        "请谈谈你对这个岗位的理解和你的职业规划？"
    ]


@app.post("/api/resume/extract")
async def extract_resume(request: ResumeExtractRequest):
    """提取简历关键信息"""
    try:
        resume_info = extract_resume_info(request.resume_text, request.job_type)
        return {"status": "success", "resume_info": resume_info}
    except Exception as e:
        print(f"简历提取API失败: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/resume/evaluate")
async def evaluate_resume(request: ResumeEvaluationRequest):
    """评价简历制作质量"""
    try:
        interview = db.get_interview(request.interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")

        resume_text = interview.get('resume_text', '')
        if not resume_text:
            raise HTTPException(status_code=400, detail="简历内容不存在")

        evaluation = evaluate_resume_quality(resume_text, request.job_type, request.interview_id)
        return {"status": "success", "evaluation": evaluation}
    except HTTPException:
        raise
    except Exception as e:
        print(f"简历评价API失败: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/resume/evaluation/{interview_id}")
async def get_resume_evaluation(interview_id: int):
    """获取简历评价结果"""
    try:
        evaluation = db.get_resume_evaluation(interview_id)
        if evaluation:
            if isinstance(evaluation.get('dimensions'), str):
                import json as json_lib
                evaluation['dimensions'] = json_lib.loads(evaluation['dimensions'])
            if isinstance(evaluation.get('strengths'), str):
                import json as json_lib
                evaluation['strengths'] = json_lib.loads(evaluation['strengths'])
            if isinstance(evaluation.get('improvements'), str):
                import json as json_lib
                evaluation['improvements'] = json_lib.loads(evaluation['improvements'])
            return {"status": "success", "evaluation": evaluation}
        else:
            return {"status": "not_found", "message": "简历评价不存在"}
    except Exception as e:
        print(f"获取简历评价API失败: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/resume/generate-questions")
async def generate_questions_from_resume(request: ResumeExtractRequest):
    """根据简历生成针对性问题"""
    try:
        resume_info = extract_resume_info(request.resume_text, request.job_type)
        questions = generate_resume_based_questions(resume_info, request.job_type, 3)
        return {"status": "success", "questions": questions, "resume_info": resume_info}
    except Exception as e:
        print(f"生成简历问题API失败: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/interview/detail")
async def get_interview_detail(interview_id: int):
    interview = db.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    messages = db.get_messages(interview_id)
    report = db.get_evaluation_report(interview_id)
    plan = db.get_improvement_plan(interview_id)
    resume_evaluation = db.get_resume_evaluation(interview_id)
    
    return {
        "interview": interview,
        "messages": messages,
        "report": report,
        "plan": plan,
        "resume_evaluation": resume_evaluation
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

# 写入新文件
with open('main_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)
    f.write(additional_code)

print("Successfully created main_fixed.py!")
