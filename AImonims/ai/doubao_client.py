import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()


class DoubaoClient:
    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY")
        self.model = os.getenv("DOUBAO_MODEL", "Doubao-Seed-2.0-pro")
        self.base_url = os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_response(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None
    
    def build_system_prompt(self, position, job_type, experience, interviewer_role, pressure_level, resume_text="", target_company=""):
        pressure_desc = {
            1: "等级1（温和友好-适合初次练习）",
            2: "等级2（专业严谨-模拟常规面试）", 
            3: "等级3（高压挑战-模拟真实压力面试）"
        }
        
        pressure_rules = {
            1: "需温和友好，避免尖锐问题，多给予鼓励",
            2: "专业严谨，问题要有深度，直接指出不足",
            3: "高压挑战，提问尖锐直接，不给回避机会，考察抗压能力"
        }
        
        role_specific_focus = {
            "HR面试官": "侧重自我介绍、职业规划、实习经历、抗压能力、团队协作、价值观匹配",
            "业务面试官": "侧重业务理解、项目经验、问题解决能力、逻辑思维",
            "技术面试官": "侧重技术深度、系统设计、编码能力、技术栈掌握",
            "CEO/总经理": "侧重战略思维、领导力、商业敏感度、职业愿景"
        }
        
        experience_focus = {
            "实习": "实习/应届生难度，注重基础知识、学习能力、潜力、校园经历",
            "应届": "实习/应届生难度，注重基础知识、学习能力、潜力、校园经历",
            "1-3年工作经验": "中级难度，注重项目经验、实际问题解决、技术应用",
            "3年以上工作经验": "高级难度，注重系统设计、架构能力、技术深度、团队领导力"
        }
        
        resume_section = ""
        if resume_text and len(resume_text.strip()) > 0:
            resume_section = f"- 简历信息：{resume_text}\n  【重要】必须围绕简历中的经历、项目、技能进行提问！"
        else:
            resume_section = "- 简历信息：未导入简历，基于通用背景提问"
        
        company_section = ""
        if target_company and len(target_company.strip()) > 0:
            company_section = f"- 目标公司：{target_company}"
        
        system_prompt = f"""你是一位非常智能的AI面试官，和豆包助手一样聪明、会上下文、会追问、贴合简历面试。

【用户信息】
- 面试岗位：{position}
- 岗位类型：{job_type}
- 工作经验：{experience}
- 面试官角色：{interviewer_role}
- 面试压力等级：{pressure_desc.get(pressure_level, '等级1')}
{resume_section}
{company_section}

【面试规则】
1. 必须根据用户信息面试，不脱离背景
2. 记住所有对话历史，自然追问
3. 用户回答后直接出下一题，禁止说"感谢你的回答"这类客套话
4. 每次只输出一个问题，不要额外解释，不要重复已问过的问题
5. 流畅自然，像真人面试官
6. 严格按照用户背景出题：{experience_focus.get(experience, '通用难度')}
7. 面试官角色侧重：{role_specific_focus.get(interviewer_role, '综合能力')}
8. 压力等级匹配：{pressure_rules.get(pressure_level, '温和友好')}
9. 若导入了简历，必须围绕简历中的经历、项目、技能提问
10. 问题要有梯度：从简单到复杂，先基础后深入
11. 适当追问细节：挖掘关键词，挑战假设，场景推演

【初始问题要求】
第一个问题应该引导候选人自我介绍，并了解其对岗位的理解，符合压力等级的语气。"""
        
        return system_prompt
    
    def generate_interview_question(self, position, round, job_type, experience, interviewer_role, pressure_level=1, resume_text="", target_company=""):
        system_prompt = self.build_system_prompt(
            position=position,
            job_type=job_type,
            experience=experience,
            interviewer_role=interviewer_role,
            pressure_level=pressure_level,
            resume_text=resume_text,
            target_company=target_company
        )
        
        user_prompt = "请生成第一个面试问题。"
        
        return self.generate_response(system_prompt, user_prompt, temperature=0.8)
    
    def generate_followup_question_with_context(self, system_prompt, conversation_history):
        history_messages = []
        
        history_messages.append({"role": "system", "content": system_prompt})
        
        for msg in conversation_history:
            role = "assistant" if msg.get('role') == 'ai' else "user"
            history_messages.append({"role": role, "content": msg.get('content', '')})
        
        history_messages.append({"role": "user", "content": "请根据对话历史，生成下一个递进的面试问题。要求：每次只输出一个问题，不要额外解释，不要重复已问过的问题。"})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=history_messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None
    
    def analyze_answer_quality(self, job_type, question, answer):
        system_prompt = """你是一位专业的面试评估专家，需要快速分析候选人回答的质量。
        请从以下维度评估：
        - 技术正确性：回答是否正确
        - 完整性：回答是否全面
        - 深度：回答是否有深度
        - 逻辑性：回答是否逻辑清晰
        
        请返回JSON格式，包含：
        {
            "quality": "excellent|good|average|poor",
            "confidence": 0-1,
            "reason": "简短原因"
        }"""
        
        user_prompt = f"""岗位类型：{job_type}
        面试问题：{question}
        候选人回答：{answer}
        
        请评估回答质量。"""
        
        response = self.generate_response(system_prompt, user_prompt, temperature=0.3, max_tokens=500)
        if response:
            try:
                return json.loads(response)
            except:
                return {"quality": "average", "confidence": 0.5, "reason": "无法评估"}
        return {"quality": "average", "confidence": 0.5, "reason": "无法评估"}
    
    def evaluate_answer(self, job_type, question, answer):
        system_prompt = """你是一位专业的面试评估专家，需要从多个维度评估候选人的回答。
        请给出客观、专业的评估。"""
        
        user_prompt = f"""岗位类型：{job_type}
        面试问题：{question}
        候选人回答：{answer}
        
        请评估候选人的回答，从以下维度打分（每个维度0-100分），并给出详细评语。
        以JSON格式返回：
        {{
            "technical_accuracy": {{ "score": 分数, "comment": "技术正确性评语" }},
            "knowledge_depth": {{ "score": 分数, "comment": "知识深度评语" }},
            "logical_thinking": {{ "score": 分数, "comment": "语言表达逻辑性评语：包括条理清晰度、论证充分性、思维连贯性" }},
            "communication_skill": {{ "score": 分数, "comment": "沟通能力评语：包括表达清晰度、倾听理解、回应针对性、专业术语使用恰当性" }},
            "job_match": {{ "score": 分数, "comment": "岗位匹配度评语" }}
        }}"""
        
        response = self.generate_response(system_prompt, user_prompt, temperature=0.3, max_tokens=1500)
        if response:
            try:
                return json.loads(response)
            except:
                return None
        return None
    
    def generate_evaluation_report(self, job_type, questions, answers):
        system_prompt = """你是一位专业的面试评估专家，需要生成一份全面、深度的面试评估报告。
        报告需要真实反映候选人的能力水平，给出具体的改进建议。"""
        
        qa_pairs = "\n".join([f"问题{i+1}: {q}\n回答{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])
        
        user_prompt = f"""岗位类型：{job_type}
        面试问题与回答：
        {qa_pairs}
        
        请生成一份详细的结构化评估报告，以JSON格式返回：
        {{
            "overall_score": 0-100,
            "overall_level": "优秀|良好|中等|需改进",
            "content_evaluation": {{
                "technical_accuracy": {{ "score": 0-100, "comment": "技术正确性详细评估" }},
                "knowledge_depth": {{ "score": 0-100, "comment": "知识深度详细评估" }},
                "problem_solving": {{ "score": 0-100, "comment": "问题解决能力详细评估" }},
                "project_experience": {{ "score": 0-100, "comment": "项目经验详细评估" }},
                "learning_ability": {{ "score": 0-100, "comment": "学习能力详细评估" }}
            }},
            "expression_evaluation": {{
                "logical_thinking": {{ "score": 0-100, "comment": "语言表达逻辑性：包括条理清晰、论证充分、思维连贯、层次分明" }},
                "communication_skill": {{ "score": 0-100, "comment": "沟通能力：包括表达清晰度、倾听理解、回应针对性、专业术语使用、互动性" }},
                "confidence": {{ "score": 0-100, "comment": "自信度评估" }},
                "clarity": {{ "score": 0-100, "comment": "表达清晰度评估" }}
            }},
            "highlights": ["亮点1", "亮点2", "亮点3"],
            "weaknesses": ["短板1", "短板2", "短板3"],
            "improvement_suggestions": [
                {{ "category": "技术提升", "suggestion": "具体建议" }},
                {{ "category": "表达提升", "suggestion": "具体建议" }},
                {{ "category": "沟通提升", "suggestion": "具体建议" }}
            ]
        }}"""
        
        response = self.generate_response(system_prompt, user_prompt, temperature=0.4, max_tokens=4000)
        if response:
            try:
                return json.loads(response)
            except:
                return None
        return None
    
    def generate_improvement_plan(self, job_type, evaluation_report):
        system_prompt = """你是一位专业的职业发展顾问，需要根据面试评估报告为候选人制定能力提升计划。
        计划要具体、可行，有针对性。"""
        
        user_prompt = f"""岗位类型：{job_type}
        评估报告：{json.dumps(evaluation_report, ensure_ascii=False)}
        
        请生成一份详细的能力提升计划，以JSON格式返回：
        {{
            "weakness_analysis": [
                {{ 
                    "category": "技术能力|表达能力|沟通能力", 
                    "weakness": "具体短板描述", 
                    "severity": "高|中|低" 
                }}
            ],
            "improvement_suggestions": [
                {{ 
                    "category": "技术提升|表达提升|沟通提升", 
                    "suggestion": "具体可操作的建议", 
                    "priority": 1-3 
                }}
            ],
            "learning_resources": [
                {{ 
                    "type": "在线课程|技术文档|书籍|博客文章|面试题库",
                    "title": "资源标题",
                    "url": "资源链接（如果有）",
                    "description": "资源描述",
                    "target_weakness": "针对的短板"
                }}
            ],
            "thirty_day_plan": [
                {{ 
                    "week": 1-4,
                    "focus": "本周重点",
                    "daily_tasks": ["任务1", "任务2", "任务3"],
                    "expected_outcome": "预期成果"
                }}
            ]
        }}"""
        
        response = self.generate_response(system_prompt, user_prompt, temperature=0.5, max_tokens=3500)
        if response:
            try:
                return json.loads(response)
            except:
                return None
        return None
    
    def recommend_learning_resources(self, job_type, weak_areas=None, interview_history=None):
        base_prompt = f"你是一位专业的{job_type}职业发展导师，需要为候选人推荐精准的学习资源。"
        
        weak_areas_str = ""
        if weak_areas:
            weak_areas_str = f"候选人的能力短板：{', '.join(weak_areas)}"
        
        history_str = ""
        if interview_history:
            history_str = f"历史面试记录：{json.dumps(interview_history, ensure_ascii=False)}"
        
        system_prompt = f"""{base_prompt}
        请基于岗位要求、候选人短板和历史表现推荐学习资源。
        资源类型包括：在线课程、技术文档、经典书籍、优质博客、面试题库、实践项目等。"""
        
        user_prompt = f"""岗位类型：{job_type}
        {weak_areas_str}
        {history_str}
        
        请推荐5-8个高质量学习资源，以JSON格式返回：
        {{
            "resources": [
                {{
                    "id": 1,
                    "type": "在线课程|技术文档|书籍|博客文章|面试题库|实践项目",
                    "title": "资源标题",
                    "author": "作者/来源（可选）",
                    "url": "资源链接（可选）",
                    "description": "资源简介和推荐理由",
                    "difficulty": "入门|中级|高级",
                    "estimated_time": "预计学习时长",
                    "target_skills": ["技能1", "技能2"],
                    "priority": 1-3
                }}
            ],
            "study_advice": "总体学习建议"
        }}"""
        
        response = self.generate_response(system_prompt, user_prompt, temperature=0.6, max_tokens=3000)
        if response:
            try:
                return json.loads(response)
            except:
                return None
        return None
    
    def analyze_interview_history(self, user_id, interviews):
        system_prompt = """你是一位专业的职业发展分析师，需要分析候选人的多次面试记录，
        找出能力成长趋势和持续短板，为个性化提升提供数据支撑。"""
        
        interviews_str = json.dumps(interviews, ensure_ascii=False)
        
        user_prompt = f"""用户ID：{user_id}
        面试历史记录：
        {interviews_str}
        
        请分析历史面试数据，生成能力成长报告，以JSON格式返回：
        {{
            "growth_trend": {{
                "overall": "上升|稳定|下降",
                "technical_accuracy": "趋势描述",
                "logical_thinking": "趋势描述",
                "communication_skill": "趋势描述"
            }},
            "persistent_weaknesses": [
                {{ "area": "短板领域", "frequency": "出现次数", "improvement": "是否有改善" }}
            ],
            "strengths": ["优势1", "优势2", "优势3"],
            "recommended_focus": ["建议重点提升领域1", "建议重点提升领域2"],
            "milestones": [
                {{ "date": "日期", "event": "关键里程碑描述", "score_change": 分数变化 }}
            ]
        }}"""
        
        response = self.generate_response(system_prompt, user_prompt, temperature=0.4, max_tokens=2500)
        if response:
            try:
                return json.loads(response)
            except:
                return None
        return None
