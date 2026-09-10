from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import logging
import sys
import os
from collections import OrderedDict
from typing import Optional
import json
from datetime import datetime
import time

from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# 显式指定 .env 路径。原先是裸 load_dotenv()，它按 cwd 向上找，
# 换个目录启动就读不到配置。
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
)
logger = logging.getLogger("interview")

sys.path.append(os.path.dirname(BACKEND_DIR))

from data.database import Database
from data.job_knowledge_base import generate_questions as generate_job_questions, JOB_TYPES

from ai.doubao_client import DoubaoClient
from ai.evaluator import InterviewEvaluator
from ai.improver import AbilityImprover
from ai.local_speech_analyzer import light_speech_analyzer
from ai.speech_recognizer import speech_recognizer, convert_audio_to_whisper_format

import admin_api
import prep_center_api
import favorites_api
from auth import (
    ConfigError,
    assert_interview_owner,
    create_token,
    current_user_id,
    get_current_user,
    get_optional_user,
    require_admin,
)
from errors import fail, install_exception_handlers, log_exception
from llm_utils import extract_json

app = FastAPI()

db = Database()

doubao_client = DoubaoClient()

install_exception_handlers(app)
admin_api.register_admin_routes(app, db.get_connection)
prep_center_api.register_prep_center_routes(app, db.get_connection)
favorites_api.register_favorites_routes(app, db.get_connection)


@app.on_event("startup")
def _check_config():
    """启动即校验签名密钥，避免运行到登录接口才炸。"""
    from auth import _secret
    _secret()
    logger.info("配置校验通过，数据库: %s", db.db_path)






def get_candidate_question_prompt(duration):
    """获取候选人提问环节的提示"""
    prompts = {
        5: "好的，感谢你的回答！面试接近尾声，请问你有没有什么问题想问我？比如关于岗位职责、实习工作内容、团队氛围等。（可提问1个问题）",
        10: "好的，感谢你的精彩回答！接下来是候选人提问环节，请问你有1-2个问题想问我吗？比如关于岗位职责、培养机制、工作节奏、团队构成等。",
        20: "非常好，感谢你的回答！现在是候选人提问环节，你有2-3个问题可以提问。可以问问关于团队构成、项目流程、培养模式、实习转正机会等你关心的问题。",
        30: "感谢你今天的精彩表现！现在进入候选人提问环节，你有3-4个问题可以提问。关于团队、技术栈、培养机制、转正流程、福利待遇等，任何你关心的问题都可以问。"
    }
    return prompts.get(duration, prompts[10])


def answer_candidate_question(question, position, interviewer_role, target_company, is_last_question=False):
    """回答候选人提出的问题"""
    if not question or not question.strip():
        if is_last_question:
            return "好的，如果没有其他问题，那我们今天的面试就到这里，感谢你的参与！"
        return "好的，如果没有其他问题，可以告诉我。"

    try:
        system_prompt = f"""你是一位专业的{interviewer_role}，正在面试{position}岗位的候选人。
候选人会提问一些关于岗位、团队、公司的问题。请给出专业、真实、有帮助的回答。
要求：
1. 回答要真诚、积极
2. 可以适当介绍公司和团队的优势
3. 不要回避可能的不足，但要从积极角度表达
4. 回答要简洁，1-3句话即可
5. 如果是最后一个问题，回答后可以简单表示期待候选人加入"""

        user_prompt = f"候选人提问：{question}\n\n请回答这个问题。"

        response = global_doubao_client.generate_response(system_prompt, user_prompt, temperature=0.6, max_tokens=300)
        if response:
            return response
    except Exception as e:
        print(f"AI回答候选人问题失败: {e}")

    return "好问题！关于这方面，我可以告诉你我们团队非常注重候选人的成长和培养，会有导师一对一带教。"


def evaluate_interview_and_recommend(interview_id, doubao_client=None, job_type=None):
    """面试结束时，分析能力短板并推荐学习资源。

    失败返回 None，由调用方记录 status="failed" —— 不再返回硬编码的假报告。
    job_type 此前被调用方传了却没接住，导致所有岗位都按 Java 出评估。
    """
    if doubao_client is None:
        doubao_client = global_doubao_client

    messages = db.get_messages(interview_id)

    if len(messages) < 4:
        logger.info("面试 %s 对话不足 4 轮，不足以生成评估", interview_id)
        return None

    if not job_type:
        job_type = (db.get_interview(interview_id) or {}).get('job_type') or 'unknown'
    # JOB_TYPES 的结构是 {job_type: 岗位中文名}，不是嵌套字典
    job_label = JOB_TYPES.get(job_type, job_type) if isinstance(JOB_TYPES, dict) else job_type

    try:
        system_prompt = """你是一位专业的面试教练，需要根据面试对话分析候选人的能力短板，并推荐学习资源。
请分析候选人在以下方面的表现：
1. 技术深度 - 对核心技术的理解程度
2. 项目经验 - 实际动手能力和经验
3. 表达逻辑 - 回答的条理性和逻辑性
4. 岗位匹配 - 与应聘岗位的契合度

然后给出：
- 能力短板分析（3-5条）
- 推荐学习资源（每个短板给出1-2个具体资源）

请用JSON格式返回：
{
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["短板1", "短板2", "短板3"],
    "recommendations": [
        {"topic": "相关主题", "resource": "推荐资源名称+链接"}
    ]
}"""

        conversation_text = ""
        for msg in messages:
            role = "面试官" if msg['sender'] == 'ai' else "候选人"
            conversation_text += f"{role}：{msg['content']}\n\n"

        user_prompt = f"应聘岗位：{job_label}\n面试对话记录：\n{conversation_text}\n\n请结合该岗位分析并给出评估和建议。"

        response = doubao_client.generate_response(system_prompt, user_prompt, temperature=0.5, max_tokens=1500)

        if response:
            parsed = extract_json(response)
            if parsed:
                return parsed
        logger.warning("面试 %s 的评估回复无法解析为 JSON", interview_id)

    except Exception as exc:
        log_exception("evaluate_interview_and_recommend(%s)" % interview_id, exc)

    return None


# 全局豆包客户端
global_doubao_client = DoubaoClient()

# 白名单原先写死为 3000-3003，漏了管理后台的 8080（开发期靠 vite 代理绕过，
# 独立部署即失败）。改为从 CORS_ORIGINS 读取，逗号分隔。
_default_origins = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:8080"
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()


def get_tech_question_system_prompt(duration, position, job_type):
    """根据面试时长获取技术问题系统提示"""
    prompts = {
        5: f"""你是一位专业的{position}面试官。面试时长5分钟，只问1个最核心的问题。
要求：聚焦岗位最核心的技能（如Java后端问Spring Boot基础）。不要追问，直接结束。""",

        10: f"""你是一位专业的{position}面试官。面试时长10分钟，问3个技术问题。
要求：
1. 第1问：基础技能（Spring Boot/MySQL基础）
2. 第2问：进阶技能（Redis/多线程/缓存）
3. 第3问：问题处理或项目经验
每次只问一个问题，用户回答后再问下一个。""",

        20: f"""你是一位专业的{position}面试官。面试时长20分钟，问5-6个深入的技术问题。
要求：
1. 第1问：技能体系概述
2. 第2-3问：技术深度（框架原理、数据库优化）
3. 第4-5问：项目经验、问题处理
4. 第6问：综合能力或职业规划
每次只问一个深入的问题，适当追问。""",

        30: f"""你是一位专业的{position}面试官。面试时长30分钟，问7-8个全面深入的问题。
要求：
1. 第1问：技能体系完整介绍
2. 第2-3问：技术深度（分布式、性能优化）
3. 第4-5问：项目细节、团队协作
4. 第6-7问：问题处理、抗压能力
5. 第8问：综合能力、岗位匹配
深入追问，挖掘真实能力。"""
    }
    return prompts.get(duration, prompts[10])


def generate_next_tech_question(position, question_num, duration, job_type):
    """生成下一个技术问题"""
    try:
        system_prompt = f"""你是一位专业的{position}面试官。用户刚回答了第{question_num}个技术问题。
请直接生成第{question_num + 1}个技术问题。
要求：
1. 直接输出一句话的问题
2. 不要前缀，不要解释
3. 像真人面试官一样自然提问"""

        prompt = f"请生成第{question_num + 1}个技术问题。"

        response = global_doubao_client.generate_response(system_prompt, prompt, temperature=0.7, max_tokens=200)
        if response:
            return response.strip()
    except Exception as e:
        print(f"AI生成技术问题失败: {e}")

    return get_default_tech_question(question_num + 1, position)


def get_default_tech_question(question_num, position):
    """获取默认的技术问题"""
    questions = {
        1: "请详细介绍一下你掌握的Java核心技术栈和框架？",
        2: "你在项目中使用Spring Boot遇到过哪些问题？如何解决的？",
        3: "如何理解多线程编程？有哪些常见的并发问题？",
        4: "描述一个你在项目中解决的复杂技术问题？",
        5: "你对未来的技术发展方向有什么规划？"
    }
    return questions.get(question_num, "请介绍一下你的项目经验？")


def get_interview_ending_message(duration):
    """获取面试结束语"""
    endings = {
        5: "好的，感谢你的提问！5分钟面试到此结束，感谢你的参与！稍后你会收到能力评估报告。",
        10: "好的，感谢你的提问！10分钟面试到此结束，感谢你的精彩表现！稍后你会收到详细的能力评估报告和学习建议。",
        20: "好的，感谢你的提问！20分钟面试到此结束，你今天的表现很出色！稍后你会收到详细的能力评估报告和针对性的学习建议。",
        30: "好的，感谢你的提问！30分钟面试到此结束，你今天的表现非常出色！作为面试官，我对你的综合能力印象深刻。稍后你会收到详细的能力评估报告和个性化的学习提升方案。"
    }
    return endings.get(duration, endings[10])






def generate_comment_and_followup_combined(user_answer, position, question_index, should_followup, max_tokens=200):
    """合并点评和追问为一次API调用（优化方案A+C）

    Args:
        user_answer: 用户回答
        position: 岗位
        question_index: 当前问题索引
        should_followup: 是否应该追问
        max_tokens: 最大生成长度（限制方案C）

    Returns:
        dict: {"comment": 点评, "followup": 追问/下一题, "is_new_question": 是否是新问题}
    """
    result = {"comment": "感谢你的回答。", "followup": "", "is_new_question": False}

    try:
        if should_followup:
            system_prompt = f"""你是一位专业的{position}面试官，正在进行技术面试。

请分两部分回复（用|分隔）：
1. 简短点评：1-2句话点评候选人刚才的回答
2. 追问：针对回答中的具体点，深入追问一个具体问题

要求：
- 点评要指出亮点或不足
- 追问要具体，像真人面试官
- 不要使用markdown格式
- 总回复控制在{max_tokens}字以内"""

            prompt = f"候选人第{question_index + 1}个问题的回答：{user_answer}\n\n请生成点评和追问，用|分隔。"

            response = global_doubao_client.generate_response(system_prompt, prompt, temperature=0.7, max_tokens=max_tokens)

            if response:
                parts = response.split('|')
                if len(parts) >= 2:
                    result["comment"] = parts[0].strip()
                    result["followup"] = parts[1].strip()
                else:
                    result["comment"] = "好的，继续追问："
                    result["followup"] = response.strip()
        else:
            system_prompt = f"""你是一位专业的{position}面试官。

请分两部分回复（用|分隔）：
1. 简短点评：1-2句话点评候选人刚才的回答
2. 过渡语：简短自然地过渡到下一个话题

要求：
- 点评要正面积极
- 过渡语要自然
- 不要使用markdown格式
- 总回复控制在{max_tokens}字以内"""

            prompt = f"候选人第{question_index + 1}个问题的回答：{user_answer}\n\n请生成点评和过渡语，用|分隔。"

            response = global_doubao_client.generate_response(system_prompt, prompt, temperature=0.7, max_tokens=max_tokens)

            if response:
                parts = response.split('|')
                if len(parts) >= 2:
                    result["comment"] = parts[0].strip()
                    result["followup"] = parts[1].strip()
                else:
                    result["comment"] = "感谢你的回答。"
                    result["followup"] = response.strip()

    except Exception as e:
        print(f"AI生成点评和追问失败: {e}")
        if should_followup:
            result["comment"] = "好的，继续追问："
            result["followup"] = "你能详细说明一下吗？"
        else:
            result["comment"] = "感谢你的回答。"

    return result






# 评估报告缓存（用于异步生成后存储结果）
# 报告的进程内缓存只作为「刚生成完」的快速通道，真实来源是数据库。
# 原先只有这个 dict：进程一重启报告就没了，端点会永久返回 status="generating"。
_REPORT_CACHE_MAX = 200
evaluation_report_cache = OrderedDict()


def _cache_report(interview_id, value):
    evaluation_report_cache[interview_id] = value
    evaluation_report_cache.move_to_end(interview_id)
    while len(evaluation_report_cache) > _REPORT_CACHE_MAX:
        evaluation_report_cache.popitem(last=False)


def generate_evaluation_report_task(interview_id, job_type=None):
    """后台生成对话式评估报告，成功与否都落库。

    失败时记录 status="failed"，不再用硬编码的假报告冒充结果 ——
    对面试评估产品来说，编造的「优势/短板/推荐书目」比明确报错更糟，
    用户无从分辨哪份评估是真的。
    """
    try:
        logger.info("[异步评估] 开始为面试 %s 生成评估报告", interview_id)
        report = evaluate_interview_and_recommend(interview_id, job_type=job_type)
        if report:
            db.save_conversation_report(interview_id, "completed", payload=report, job_type=job_type)
            _cache_report(interview_id, {"status": "completed", "payload": report})
            logger.info("[异步评估] 面试 %s 评估报告生成完成", interview_id)
        else:
            db.save_conversation_report(interview_id, "failed", error="模型未返回可解析的评估结果", job_type=job_type)
            _cache_report(interview_id, {"status": "failed", "error": "模型未返回可解析的评估结果"})
            logger.warning("[异步评估] 面试 %s 评估生成失败", interview_id)
    except Exception as exc:
        trace_id = log_exception("generate_evaluation_report_task(%s)" % interview_id, exc)
        try:
            db.save_conversation_report(interview_id, "failed", error="生成异常 trace_id=%s" % trace_id, job_type=job_type)
        except Exception:
            logger.exception("写入失败状态时再次异常")
        _cache_report(interview_id, {"status": "failed", "error": "生成异常", "trace_id": trace_id})


def generate_evaluation_report_async(interview_id, job_type=None, background_tasks=None):
    """调度后台评估任务。

    原实现是 threading.Thread(...).start()：无上限、无 join、异常不上报；
    同时还建了个从未使用的 ThreadPoolExecutor(max_workers=6)。
    """
    db.save_conversation_report(interview_id, "generating", job_type=job_type)
    _cache_report(interview_id, {"status": "generating"})
    if background_tasks is not None:
        background_tasks.add_task(generate_evaluation_report_task, interview_id, job_type)
        return
    try:
        asyncio.get_running_loop().run_in_executor(None, generate_evaluation_report_task, interview_id, job_type)
    except RuntimeError:
        generate_evaluation_report_task(interview_id, job_type)


def get_cached_evaluation_report(interview_id):
    """取评估报告：先看进程内缓存，再回落到数据库。"""
    cached = evaluation_report_cache.get(interview_id)
    if cached:
        return cached
    stored = db.get_conversation_report(interview_id)
    if not stored:
        return None
    return {"status": stored.get("status"), "payload": stored.get("payload"), "error": stored.get("error")}

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    phone: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class InterviewRequest(BaseModel):
    position: str
    round: str
    job_type: Optional[str] = None
    experience: Optional[str] = None
    interviewer_role: Optional[str] = None
    pressure_level: Optional[int] = 1
    duration: Optional[int] = 10
    resume_text: Optional[str] = None
    target_company: Optional[str] = None

class MessageRequest(BaseModel):
    content: str
    interview_id: int

class GenerateQuestionsRequest(BaseModel):
    job: str
    job_type: str = "java_backend"
    experience: str
    interviewer_role: str
    duration: int = 10  # 面试时长（分钟）

class EvaluateRequest(BaseModel):
    interview_id: int
    job_type: str = "java_backend"
    questions: list
    answers: list

class ImprovementPlanRequest(BaseModel):
    interview_id: int
    job_type: str = "java_backend"
    evaluation_report: dict

class RecommendResourcesRequest(BaseModel):
    job_type: str = "java_backend"
    weak_areas: Optional[list] = None
    user_id: Optional[int] = None

@app.post("/api/auth/register")
async def register(request: UserRegisterRequest):
    if len(request.password or "") < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    # role 固定为 user：注册接口不接受角色参数，管理员只能由管理端授予。
    user_id = db.add_user(
        username=request.username,
        password=request.password,
        email=request.email,
        phone=request.phone,
        role="user",
    )
    if user_id is None:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    user = db.get_user_by_id(user_id)
    return {"message": "注册成功", "user_id": user_id, "token": create_token(user), "role": "user"}

@app.post("/api/user/info")
async def get_user_info(user_id: Optional[int] = None, _user: dict = Depends(get_current_user)):
    """返回当前登录用户的信息。

    user_id 形参仅为兼容前端既有调用（它仍会带上这个参数），其值不采信；
    身份一律取自令牌，否则任何人改 id 就能读他人资料。
    """
    user = db.get_user_by_id(current_user_id(_user))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@app.post("/api/user/update")
async def update_user(user_id: Optional[int] = None, username: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, avatar: Optional[str] = None, _user: dict = Depends(get_current_user)):
    success = db.update_user(current_user_id(_user), username, email, phone, avatar)
    if success:
        return {"message": "更新成功"}
    else:
        return {"message": "无更新内容"}

@app.post("/api/interview/start")
async def start_interview(request: InterviewRequest, user_id: Optional[int] = None, _user: dict = Depends(get_current_user)):
    # user_id 形参仅为兼容前端既有调用，其值不采信；归属一律以令牌为准。
    try:
        interview_id = db.start_interview(
            user_id=current_user_id(_user),
            position=request.position,
            round_info=request.round,
            job_type=request.job_type,
            experience=request.experience,
            interviewer_role=request.interviewer_role,
            pressure_level=request.pressure_level,
            duration=request.duration,
            resume_text=request.resume_text,
            target_company=request.target_company
        )
        
        # 根据面试时长生成对应的开场语和配置
        duration = request.duration
        if duration == 5:
            question_config = {
                "self_intro_questions": 1,
                "tech_questions": 2,
                "candidate_questions": 1,
                "max_followups_total": 1
            }
            initial_question = f"你好！我是AI面试官，今天将对你进行{request.position}岗位的{request.round}面试，时长为5分钟。本次面试主要是快速核实你的基本信息和核心适配度。请先做一个简短的自我介绍，重点说明个人基本信息、核心技能和求职意向。"
        elif duration == 10:
            question_config = {
                "self_intro_questions": 1,
                "tech_questions": 4,
                "candidate_questions": 2,
                "max_followups_total": 2
            }
            initial_question = f"你好！我是AI面试官，今天将对你进行{request.position}岗位的{request.round}面试，时长为10分钟。本次面试主要考察你的技能匹配度和表达能力。请先做一个详细的自我介绍，包括个人基本信息、技能掌握情况和相关学习/项目经历（重点提炼1个核心亮点）。"
        elif duration == 20:
            question_config = {
                "self_intro_questions": 1,
                "tech_questions": 6,
                "candidate_questions": 3,
                "max_followups_total": 3
            }
            initial_question = f"你好！我是AI面试官，今天将对你进行{request.position}岗位的{request.round}面试，时长为20分钟。本次面试将全面考察你的技能掌握、项目经验、问题处理和职业素养。请先做一个完整的自我介绍，包括个人信息、技能体系、学习/项目经历（简要展开1个相关案例）和职业规划。"
        elif duration == 30:
            question_config = {
                "self_intro_questions": 1,
                "tech_questions": 8,
                "candidate_questions": 4,
                "max_followups_total": 4
            }
            initial_question = f"你好！我是AI面试官，今天将对你进行{request.position}岗位的{request.round}面试，时长为30分钟。本次面试将全方位、深层次考察你的能力、态度与潜力。请先做一个详细的自我介绍，包括个人基本信息、技能熟练度、学习/项目经历（展开1-2个核心案例，说明背景、自身职责、遇到的问题及解决成果）和职业规划。"
        else:
            question_config = {
                "self_intro_questions": 1,
                "tech_questions": 4,
                "candidate_questions": 2,
                "max_followups_total": 2
            }
            initial_question = f"你好！我是AI面试官，今天将对你进行{request.position}岗位的{request.round}面试，时长为{duration}分钟。请先做一个详细的自我介绍。"

        import json as json_lib
        db.update_interview_config(interview_id, question_config)
        db.update_interview_phase(interview_id, "introduction")
        db.update_current_question_index(interview_id, 0)
        db.update_current_followup_count(interview_id, 0)
        db.update_max_followups_per_question(interview_id, question_config.get("max_followups_total", 2))

        # 如果有简历，先提取简历信息并存储
        resume_info = None
        resume_based_questions = []
        if request.resume_text and request.resume_text.strip():
            try:
                resume_info = await asyncio.to_thread(extract_resume_info, request.resume_text, request.job_type)
                db.update_resume_info(interview_id, json_lib.dumps(resume_info, ensure_ascii=False))
                # 生成基于简历的问题，为技术问题环节做准备
                resume_based_questions = await asyncio.to_thread(generate_resume_based_questions, resume_info, request.job_type, min(3, question_config.get("tech_questions", 4)))
                db.update_resume_based_questions(interview_id, json_lib.dumps(resume_based_questions, ensure_ascii=False))
            except Exception as resume_error:
                print(f"简历处理失败: {resume_error}")

        db.add_message(interview_id, "ai", initial_question)
        
        return {
            "message": f"面试已开始，岗位：{request.position}，轮次：{request.round}，压力等级：{request.pressure_level}，时长：{duration}分钟",
            "initial_question": initial_question,
            "interview_id": interview_id,
            "resume_info": resume_info,
            "resume_based_questions": resume_based_questions
        }
    except Exception as e:
        print(f"开始面试失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {
            "error": "开始面试失败",
            "message": _msg
        }

@app.post("/api/interview/message")
async def send_message(request: MessageRequest, _user: dict = Depends(get_current_user)):
    assert_interview_owner(db, request.interview_id, _user)
    db.add_message(request.interview_id, "user", request.content)

    interview_info = db.get_interview(request.interview_id)
    if not interview_info:
        return {"error": "面试不存在"}

    import json as json_lib
    position = interview_info.get('position', '未知岗位')
    job_type = interview_info.get('job_type', 'java_backend')
    duration = interview_info.get('duration', 10)
    interviewer_role = interview_info.get('interviewer_role', '面试官')
    target_company = interview_info.get('target_company', '')
    current_phase = interview_info.get('phase', 'introduction')
    interview_config_str = interview_info.get('interview_config')

    if interview_config_str:
        question_config = json_lib.loads(interview_config_str)
    else:
        question_config = {
            5: {"self_intro_questions": 1, "tech_questions": 1, "candidate_questions": 1},
            10: {"self_intro_questions": 1, "tech_questions": 3, "candidate_questions": 2},
            20: {"self_intro_questions": 1, "tech_questions": 5, "candidate_questions": 3},
            30: {"self_intro_questions": 1, "tech_questions": 7, "candidate_questions": 4}
        }.get(duration, {"self_intro_questions": 1, "tech_questions": 3, "candidate_questions": 2})

    self_intro_limit = question_config.get("self_intro_questions", 1)
    tech_question_limit = question_config.get("tech_questions", 3)
    candidate_question_limit = question_config.get("candidate_questions", 2)

    messages = db.get_messages(request.interview_id)
    user_answers_count = sum(1 for msg in messages if msg['sender'] == 'user')
    ai_questions_count = sum(1 for msg in messages if msg['sender'] == 'ai' and msg['content'].strip())

    self_intro_count = interview_info.get('self_intro_question_count', 0) or 0
    tech_question_count = interview_info.get('tech_question_count', 0) or 0
    candidate_q_count = interview_info.get('candidate_question_count', 0) or 0

    comment = ""
    followup_response = ""
    is_interview_over = False
    evaluation_report = None
    is_candidate_question_phase = False
    current_phase_display = current_phase

    if current_phase == "ended":
        return {
            "response": "面试已经结束，感谢你的参与！",
            "comment": "",
            "followup": "",
            "is_interview_over": True,
            "evaluation_report": None,
            "current_phase": "ended",
            "self_intro_count": self_intro_count,
            "tech_question_count": tech_question_count,
            "candidate_q_count": candidate_q_count
        }

    elif current_phase == "introduction":
        self_intro_count += 1
        db.update_self_intro_question_count(request.interview_id, self_intro_count)

        if self_intro_count >= self_intro_limit:
            db.update_interview_phase(request.interview_id, "tech_questions")
            current_phase_display = "tech_questions"
            tech_question_count = 0
            db.update_tech_question_count(request.interview_id, 0)

            system_prompt = get_tech_question_system_prompt(duration, position, job_type)
            followup_response = await asyncio.to_thread(doubao_client.generate_response, system_prompt,
                f"候选人自我介绍：{request.content}\n\n请生成第1个技术问题。",
                temperature=0.7,
                max_tokens=500)
            if not followup_response:
                followup_response = get_default_tech_question(tech_question_count + 1, position)
        else:
            comment = "好的，感谢你的自我介绍。"
            followup_response = "请继续补充，特别是你的核心技能亮点和相关项目经验。"

    elif current_phase == "tech_questions":
        current_question_index = interview_info.get('current_question_index', 0) or 0
        current_followup_count = interview_info.get('current_followup_count', 0) or 0
        max_followups_per_question = interview_info.get('max_followups_per_question', 2) or 2

        should_followup = current_followup_count < max_followups_per_question

        combined_result = await asyncio.to_thread(generate_comment_and_followup_combined, request.content, position, current_question_index, should_followup, max_tokens=250)

        comment = combined_result["comment"]
        followup_response = combined_result["followup"]

        if should_followup:
            current_followup_count += 1
            db.update_current_followup_count(request.interview_id, current_followup_count)
        else:
            tech_question_count += 1
            current_question_index += 1
            current_followup_count = 0
            db.update_tech_question_count(request.interview_id, tech_question_count)
            db.update_current_question_index(request.interview_id, current_question_index)
            db.update_current_followup_count(request.interview_id, 0)

            latest_interview = db.get_interview(request.interview_id)
            current_db_tech_count = latest_interview.get('tech_question_count', 0) if latest_interview else tech_question_count

            if current_db_tech_count >= tech_question_limit:
                db.update_interview_phase(request.interview_id, "candidate_questions")
                db.update_candidate_question_count(request.interview_id, 0)
                current_phase_display = "candidate_questions"
                is_candidate_question_phase = True
                comment = "感谢你的精彩回答！技术问题环节到此结束。"
                followup_response = get_candidate_question_prompt(duration)
            else:
                # 优先使用简历相关的问题
                import json as json_lib
                resume_based_questions_str = latest_interview.get('resume_based_questions') if latest_interview else None
                resume_based_questions = []
                if resume_based_questions_str:
                    try:
                        resume_based_questions = json_lib.loads(resume_based_questions_str)
                    except:
                        resume_based_questions = []
                
                if current_question_index - 1 < len(resume_based_questions):
                    followup_response = resume_based_questions[current_question_index - 1]
                else:
                    next_question = await asyncio.to_thread(generate_next_tech_question, position, current_question_index, duration, job_type)
                    if next_question:
                        followup_response = next_question
                    else:
                        followup_response = get_default_tech_question(current_question_index, position)

    elif current_phase == "candidate_questions":
        is_candidate_question_phase = True
        current_phase_display = "candidate_questions"
        candidate_q_count += 1
        db.update_candidate_question_count(request.interview_id, candidate_q_count)

        if candidate_q_count >= candidate_question_limit:
            is_interview_over = True
            followup_response = get_interview_ending_message(duration)
            db.update_interview_phase(request.interview_id, "ended")
            
            # 生成评估报告
            generate_evaluation_report_async(request.interview_id, job_type)
            
            # 如果有简历，进行简历评价
            resume_text = interview_info.get('resume_text', '') if interview_info else ''
            if resume_text and resume_text.strip():
                try:
                    await asyncio.to_thread(evaluate_resume_quality, resume_text, job_type, request.interview_id)
                except Exception as resume_eval_error:
                    print(f"简历评价失败: {resume_eval_error}")
            
            evaluation_report = {
                "status": "generating",
                "message": "评估报告生成中，请稍候...",
                "interview_id": request.interview_id
            }
        else:
            followup_response = await asyncio.to_thread(answer_candidate_question, request.content,
                position,
                interviewer_role,
                target_company,
                is_last_question=(candidate_q_count == candidate_question_limit - 1))
            if candidate_q_count == candidate_question_limit - 1:
                generate_evaluation_report_async(request.interview_id, job_type)

    else:
        db.update_interview_phase(request.interview_id, "introduction")
        followup_response = "请开始自我介绍。"

    full_response = followup_response
    if comment and not is_candidate_question_phase:
        full_response = f"{comment}\n\n{followup_response}"
    
    # 先添加点评（如果有的话）
    if comment and not is_candidate_question_phase:
        db.add_message(request.interview_id, "ai", comment)
    
    # 再添加下一题或结束语
    db.add_message(request.interview_id, "ai", followup_response)

    return {
        "response": followup_response,
        "comment": comment if (comment and not is_candidate_question_phase) else "",
        "followup": followup_response,
        "is_interview_over": is_interview_over,
        "is_candidate_question_phase": is_candidate_question_phase,
        "evaluation_report": evaluation_report,
        "current_phase": current_phase_display,
        "self_intro_count": self_intro_count,
        "self_intro_limit": self_intro_limit,
        "tech_question_count": tech_question_count,
        "tech_question_limit": tech_question_limit,
        "candidate_q_count": candidate_q_count,
        "candidate_question_limit": candidate_question_limit
    }

@app.post("/api/interview/generate-questions")
async def generate_questions(request: GenerateQuestionsRequest):
    try:
        # 根据面试时长确定问题数量
        duration = getattr(request, 'duration', 10)
        if duration == 5:
            question_count = 2  # 5分钟：1-2个核心问题
        elif duration == 10:
            question_count = 4  # 10分钟：3-4个问题
        elif duration == 20:
            question_count = 6  # 20分钟：5-6个问题
        elif duration == 30:
            question_count = 8  # 30分钟：7-8个问题
        else:
            question_count = 4  # 默认4个问题
        
        questions = generate_job_questions(request.job_type, request.experience, question_count)
        if questions and len(questions) > 0:
            return {"questions": questions, "question_count": question_count}
        
        system_prompt = f"""你是一位专业的AI面试官，正在为{request.job}岗位准备面试题。
        面试官角色是{request.interviewer_role}，候选人经验是{request.experience}。
        请生成{question_count}个专业、有针对性的面试问题。"""
        
        user_prompt = f"请生成{question_count}个{request.job}岗位的面试问题，以JSON数组格式返回。"
        
        result = await asyncio.to_thread(doubao_client.generate_response, system_prompt, user_prompt, temperature=0.8)
        if result:
            try:
                questions_data = json.loads(result)
                if isinstance(questions_data, list):
                    return {"questions": questions_data}
            except:
                pass
        
        return {"questions": [
            f"请介绍一下你对{request.job}岗位的理解。",
            f"你为什么想申请{request.job}岗位？",
            "请分享一个你相关的项目经验。"
        ]}
    except Exception as e:
        print(f"生成问题失败: {e}")
        return {"questions": [
            f"请介绍一下你对{request.job}岗位的理解。",
            f"你为什么想申请{request.job}岗位？",
            "请分享一个你相关的项目经验。"
        ]}

@app.post("/api/interview/evaluate")
async def evaluate_interview(request: EvaluateRequest, _user: dict = Depends(get_current_user)):
    assert_interview_owner(db, request.interview_id, _user)
    try:
        report = await asyncio.to_thread(generate_evaluation_with_ai, job_type=request.job_type,
            questions=request.questions,
            answers=request.answers)

        if not report:
            evaluator = InterviewEvaluator()
            report = evaluator.generate_report(
                job_type=request.job_type,
                questions=request.questions,
                answers=request.answers
            )

        if 'timestamp' not in report:
            report['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db.save_evaluation_report(
            interview_id=request.interview_id,
            overall_score=report.get('overall_score', 0),
            overall_level=report.get('overall_level', 'average'),
            content_evaluation=json.dumps(report.get('content_evaluation', {})),
            expression_evaluation=json.dumps(report.get('expression_evaluation', {})),
            highlights=json.dumps(report.get('highlights', [])),
            suggestions=json.dumps(report.get('suggestions', []))
        )

        return report
    except Exception as e:
        print(f"评估失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {
            "error": "评估失败",
            "message": _msg
        }


@app.get("/api/interview/{interview_id}/evaluation-report")
async def get_evaluation_report(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取面试评估报告（支持异步轮询）"""
    interview = assert_interview_owner(db, interview_id, _user)
    stored = get_cached_evaluation_report(interview_id)

    if stored:
        status = stored.get("status")
        if status == "completed":
            return {"status": "completed", "report": stored.get("payload")}
        if status == "failed":
            # 明确告知失败，而不是永远显示「生成中」，也不塞假报告
            return {"status": "failed", "message": stored.get("error") or "评估报告生成失败"}
        return {"status": "generating", "message": "评估报告生成中..."}

    if interview.get('phase', '') != 'ended':
        return {"status": "in_progress", "message": "面试尚未结束"}

    # 面试已结束却没有任何报告记录：补跑一次，而不是永久卡在 generating。
    generate_evaluation_report_async(interview_id, interview.get('job_type'))
    return {"status": "generating", "message": "评估报告生成中..."}


def generate_evaluation_with_ai(job_type, questions, answers):
    """使用AI生成面试评估报告"""
    try:
        system_prompt = """你是一位专业的面试评估专家。请根据面试问答内容生成评估报告。

请用JSON格式返回评估结果：
{
    "overall_score": 85,
    "overall_level": "良好",
    "content_evaluation": {
        "technical_depth": {"score": 85, "comment": "技术深度评价"},
        "project_experience": {"score": 80, "comment": "项目经验评价"},
        "communication": {"score": 85, "comment": "表达能力评价"}
    },
    "expression_evaluation": {
        "voice_tone": {"score": 85, "comment": "语音语调评价"},
        "speech_rate": {"score": 80, "comment": "语速评价"},
        "voice_volume": {"score": 85, "comment": "音量评价"}
    },
    "highlights": ["亮点1", "亮点2"],
    "improvement_suggestions": [{"suggestion": "建议1"}, {"suggestion": "建议2"}]
}"""

        qa_text = ""
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            qa_text += f"问题{i}：{q}\n回答{i}：{a}\n\n"

        response = global_doubao_client.generate_response(system_prompt, qa_text, temperature=0.5, max_tokens=2000)

        if response:
            import re
            json_match = extract_json(response)
            if json_match:
                return json_match
    except Exception as e:
        print(f"AI生成评估报告失败: {e}")
    return None

@app.post("/api/interview/improvement-plan")
async def generate_improvement_plan(request: ImprovementPlanRequest, _user: dict = Depends(get_current_user)):
    assert_interview_owner(db, request.interview_id, _user)
    try:
        improver = AbilityImprover()
        improvement_plan = improver.generate_improvement_plan(
            job_type=request.job_type,
            evaluation_report=request.evaluation_report or {}
        )

        if not improvement_plan or not improvement_plan.get('weaknesses'):
            # 原先这里会塞一份写死的 Java 提升计划（《Java核心技术》《Effective Java》……），
            # 不分岗位，用户也无从分辨这是真建议还是兜底。现在如实报告失败。
            logger.warning("面试 %s 的提升计划生成失败", request.interview_id)
            return {
                "status": "failed",
                "success": False,
                "detail": "提升计划生成失败，请稍后重试",
            }

        # 转换数据格式以匹配前端期望
        weakness_analysis = []
        for weakness in improvement_plan.get('weaknesses', []):
            if isinstance(weakness, str):
                weakness_analysis.append({"weakness": weakness, "severity": "中"})
            else:
                weakness_analysis.append(weakness)

        improvement_suggestions = []
        for i, suggestion in enumerate(improvement_plan.get('suggestions', [])):
            if isinstance(suggestion, str):
                improvement_suggestions.append({
                    "suggestion": suggestion,
                    "category": "技术提升",
                    "priority": "高" if i < 3 else "中"
                })
            else:
                improvement_suggestions.append(suggestion)

        learning_resources = []
        for resource in improvement_plan.get('resources', []):
            if isinstance(resource, str):
                learning_resources.append({
                    "title": resource,
                    "type": "在线课程",
                    "url": ""
                })
            else:
                learning_resources.append(resource)

        thirty_day_plan = []
        for week_plan in improvement_plan.get('learning_plan', []):
            if isinstance(week_plan, dict):
                thirty_day_plan.append({
                    "week": week_plan.get('week', 1),
                    "focus": week_plan.get('title', week_plan.get('focus', '学习')),
                    "daily_tasks": week_plan.get('tasks', []),
                    "expected_outcome": "掌握相关技能"
                })
            else:
                thirty_day_plan.append({
                    "week": len(thirty_day_plan) + 1,
                    "focus": str(week_plan),
                    "daily_tasks": [],
                    "expected_outcome": ""
                })

        # 确保数据结构与前端匹配
        formatted_plan = {
            "weakness_analysis": weakness_analysis,
            "improvement_suggestions": improvement_suggestions,
            "learning_resources": learning_resources,
            "thirty_day_plan": thirty_day_plan
        }

        # 保存到数据库时使用原结构
        db.save_improvement_plan(
            interview_id=request.interview_id,
            weaknesses=json.dumps(improvement_plan.get('weaknesses', [])),
            suggestions=json.dumps(improvement_plan.get('suggestions', [])),
            resources=json.dumps(improvement_plan.get('resources', [])),
            learning_plan=json.dumps(improvement_plan.get('learning_plan', []))
        )

        return formatted_plan
    except Exception as e:
        print(f"生成提升计划失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {
            "error": "生成提升计划失败",
            "message": _msg
        }

@app.get("/api/interview/history")
async def get_interview_history(user_id: Optional[int] = None, _user: dict = Depends(get_current_user)):
    # 只返回当前登录用户自己的面试历史
    interviews = db.get_user_interviews(current_user_id(_user))
    return {"interviews": interviews}

@app.get("/api/interview/detail")
async def get_interview_detail(interview_id: int, _user: dict = Depends(get_current_user)):
    assert_interview_owner(db, interview_id, _user)
    interview = db.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    messages = db.get_messages(interview_id)
    report = db.get_evaluation_report(interview_id)
    plan = db.get_improvement_plan(interview_id)
    resume_evaluation = db.get_resume_evaluation(interview_id)
    
    if resume_evaluation:
        if isinstance(resume_evaluation.get('dimensions'), str):
            import json as json_lib
            resume_evaluation['dimensions'] = json_lib.loads(resume_evaluation['dimensions'])
        if isinstance(resume_evaluation.get('strengths'), str):
            import json as json_lib
            resume_evaluation['strengths'] = json_lib.loads(resume_evaluation['strengths'])
        if isinstance(resume_evaluation.get('improvements'), str):
            import json as json_lib
            resume_evaluation['improvements'] = json_lib.loads(resume_evaluation['improvements'])
    
    return {
        "interview": interview,
        "messages": messages,
        "report": report,
        "plan": plan,
        "resume_evaluation": resume_evaluation
    }

@app.delete("/api/interview/delete")
async def delete_interview(interview_id: int, user_id: int, _user: dict = Depends(get_current_user)):
    assert_interview_owner(db, interview_id, _user)
    interview = db.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 原先是 `if interview['user_id'] != user_id`，而 user_id 由调用方提供，
    # 等于自己证明自己；现由 assert_interview_owner 依据令牌校验。
    success = db.delete_interview(interview_id)
    return {"success": bool(success), "message": "删除成功" if success else "删除失败"}

# 数字人相关API端点
class AvatarMessage(BaseModel):
    text: str
    voice_type: Optional[str] = "Cherry"  # 默认声音类型

class AvatarASRRequest(BaseModel):
    text: str
    voice_type: Optional[str] = "Cherry"
    duration: Optional[int] = 5000  # 语音时长（毫秒）

# 阿里云TTS声音类型映射（使用DashScope系统音色）
VOICE_TYPES = {
    "Cherry": {"name": "艾夏(芊悦)", "description": "阳光积极、亲切自然小姐姐", "recommended": True},
    "Serena": {"name": "苏瑶", "description": "温柔小姐姐", "recommended": False},
    "Ethan": {"name": "晨煦", "description": "阳光、温暖、活力男声", "recommended": False},
    "Chelsie": {"name": "千雪", "description": "二次元虚拟女友", "recommended": False},
    "Momo": {"name": "茉兔", "description": "撒娇搞怪", "recommended": False},
    "Moon": {"name": "月白", "description": "率性帅气的月白", "recommended": False},
    "Maia": {"name": "四月", "description": "知性与温柔的碰撞", "recommended": False},
    "Kai": {"name": "凯", "description": "耳朵SPA男性", "recommended": False},
    "Nofish": {"name": "不吃鱼", "description": "不会翘舌音的设计师", "recommended": False},
    "Bella": {"name": "萌宝", "description": "小萝莉", "recommended": False},
    "Ryan": {"name": "甜茶", "description": "节奏拉满，戏感炸裂", "recommended": False},
    "Eldric_Sage": {"name": "沧明子", "description": "沉稳睿智的老者", "recommended": False},
    "Nini": {"name": "邻家妹妹", "description": "糯米糍一样又软又黏", "recommended": False},
}

@app.get("/api/avatar/voices")
async def get_voice_types():
    """获取可用的声音类型列表"""
    return {"voices": VOICE_TYPES}

@app.websocket("/ws/avatar")
async def websocket_avatar(websocket: WebSocket, client_id: Optional[str] = None):
    # 处理query参数
    if client_id is None:
        # 尝试从query字符串获取client_id
        query_params = websocket.query_params
        client_id = query_params.get("client_id") if hasattr(websocket, 'query_params') else None
    
    if not client_id:
        client_id = f"client_{int(time.time())}"
    
    await manager.connect(websocket, client_id)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data['type'] == 'user-message':
                    # 处理用户消息
                    user_text = message_data['content']
                    
                    # 生成AI回复
                    try:
                        system_prompt = "你是一个专业的面试官，用简短的语言提问和评价面试者的回答"
                        response = await asyncio.to_thread(global_doubao_client.generate_response, system_prompt,
                            user_text,
                            temperature=0.7,
                            max_tokens=300)
                        
                        if response:
                            await websocket.send_text(json.dumps({
                                'type': 'message',
                                'content': response
                            }))
                    except Exception as e:
                        print(f"数字人AI回复失败: {e}")
                        await websocket.send_text(json.dumps({
                            'type': 'message',
                            'content': '抱歉，系统暂时无法处理您的请求，请稍后重试。'
                        }))
                
                elif message_data['type'] == 'ice-candidate':
                    # 处理WebRTC ICE候选
                    pass
                    
                elif message_data['type'] == 'avatar-select':
                    # 处理数字人形象选择
                    avatar_type = message_data.get('avatar_type', 'default')
                    await websocket.send_text(json.dumps({
                        'type': 'avatar-selected',
                        'avatar_type': avatar_type,
                        'content': f'已切换到{avatar_type}形象'
                    }))
                    
            except json.JSONDecodeError:
                print("收到无效的JSON数据")
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'content': '收到无效的JSON数据'
                }))
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(client_id)

@app.post("/api/avatar/asr")
async def avatar_asr(request: Request):
    """完整数字人面试流程：文本 + 时长 → 真实语速计算 → 语气/自信度分析 → AI回答 → TTS"""
    try:
        import os

        form_data = await request.form()
        audio_file = form_data.get('audio')
        user_text = form_data.get('text', '')
        voice_type = form_data.get('voice_type', 'Cherry')
        duration_str = form_data.get('duration', '5000')

        try:
            audio_duration_ms = int(duration_str)
        except:
            audio_duration_ms = 5000

        if not user_text and not audio_file:
            return {"error": "未提供文本或音频"}

        recognized_text = user_text.strip() if user_text else "用户语音回答"

        speech_analysis = doubao_client.analyze_speech(recognized_text)

        ai_response = doubao_client.generate_digital_human_response(recognized_text)

        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        tts_audio_url = None

        if dashscope_key and ai_response:
            try:
                import dashscope
                dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

                tts_response = await asyncio.to_thread(dashscope.MultiModalConversation.call, model="qwen3-tts-flash",
                    api_key=dashscope_key,
                    text=ai_response,
                    voice=voice_type,
                    language_type="Chinese",
                    stream=False)

                if tts_response.status_code == 200:
                    tts_audio_url = tts_response.output.audio.url
            except Exception as tts_error:
                print(f"TTS生成失败: {tts_error}")

        text_length = len(recognized_text) if recognized_text else 0
        speech_rate_score = speech_analysis.get("speech_rate_score", 70) if speech_analysis else 70
        confidence_score = speech_analysis.get("confidence_score", 60) if speech_analysis else 60

        speech_rate = 0.0
        if text_length > 0 and audio_duration_ms > 0:
            speech_rate = text_length / (audio_duration_ms / 1000)

        return {
            "success": True,
            "text": recognized_text,
            "speech_analysis": speech_analysis,
            "ai_response": ai_response,
            "tts_audio_url": tts_audio_url,
            "metrics": {
                "speech_rate": round(speech_rate, 1) if speech_rate > 0 else speech_rate_score / 10,
                "clarity": confidence_score / 100,
                "confidence": confidence_score / 100,
                "duration": audio_duration_ms,
                "char_count": text_length,
                "sentence_count": 1
            }
        }

    except Exception as e:
        print(f"数字人面试流程失败: {e}")
        import traceback
        traceback.print_exc()
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "处理失败: " + _msg}

@app.post("/api/avatar/tts")
async def avatar_tts(request: AvatarMessage):
    try:
        text = request.text
        voice_type = request.voice_type or "aixia"
        
        # 如果声音类型不在列表中，使用默认
        if voice_type not in VOICE_TYPES:
            voice_type = "aixia"
        
        # 阿里云TTS API调用 - 使用DashScope SDK
        try:
            import os
            import io
            
            # 设置DashScope API
            import dashscope
            dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
            
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return {"error": "未配置DASHSCOPE_API_KEY环境变量"}
            
            print(f"TTS请求: voice={voice_type}, text={text[:50]}...")
            
            # 调用DashScope TTS API
            response = await asyncio.to_thread(dashscope.MultiModalConversation.call, model="qwen3-tts-flash",
                api_key=api_key,
                text=text,
                voice=voice_type,
                language_type="Chinese",
                stream=False)
            
            if response.status_code == 200:
                # 获取音频URL并下载
                audio_url = response.output.audio.url
                print(f"TTS音频URL: {audio_url}")
                
                # 下载音频数据
                import requests as req
                audio_response = req.get(audio_url)
                
                if audio_response.status_code == 200:
                    return Response(
                        content=audio_response.content,
                        media_type="audio/wav"
                    )
                else:
                    return {"error": f"下载音频失败: {audio_response.status_code}"}
            else:
                return {"error": f"TTS API错误: {response.message}"}
                
        except Exception as tts_error:
            print(f"阿里云TTS调用失败: {tts_error}")
            import traceback
            traceback.print_exc()
            _trace = log_exception("main.py", tts_error)
            _msg = "服务器内部错误 (trace_id=%s)" % _trace
            return {"error": "TTS服务暂时不可用: " + _msg}

    except Exception as e:
        print(f"TTS处理失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": _msg}

# 数字人视频生成相关API
class AvatarVideoRequest(BaseModel):
    text: str
    avatar: Optional[str] = "default_2d_male_01"  # 数字人形象
    voice: Optional[str] = "longxiaochun"  # 音色

# 数字人形象选项
AVATAR_OPTIONS = {
    "default_2d_male_01": {"name": "男面试官", "gender": "male"},
    "default_2d_female_01": {"name": "女面试官", "gender": "female"},
}

# 音色选项
VOICE_OPTIONS = {
    "longxiaochun": {"name": "龙小春", "gender": "male"},
    "aiqier": {"name": "AI琪尔", "gender": "female"},
    "aiyue": {"name": "AI悦", "gender": "female"},
}

@app.get("/api/avatar/video/options")
async def get_video_options():
    """获取数字人视频选项"""
    return {
        "avatars": AVATAR_OPTIONS,
        "voices": VOICE_OPTIONS
    }

@app.post("/api/avatar/video/generate")
async def generate_avatar_video(request: AvatarVideoRequest):
    """生成数字人视频 - 纯HTTP请求方式"""
    try:
        import os
        import time
        import requests as http_requests
        
        # 获取阿里云AK/SK
        ak_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID")
        ak_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET") or os.getenv("ACCESS_KEY_SECRET")
        
        if not ak_id or not ak_secret:
            return {"error": "未配置阿里云AccessKey，请检查环境变量"}
        
        # 阿里云数字人接口地址
        url = "https://avatar.cn-beijing.aliyuncs.com/"
        
        # 提交任务参数
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        params = {
            "Action": "SubmitJob",
            "Version": "2022-01-30",
            "AccessKeyId": ak_id,
            "Format": "JSON",
            "Timestamp": timestamp,
            "SignatureMethod": "HMAC-SHA1",
            "SignatureVersion": "1.0",
            "SignatureNonce": str(int(time.time() * 1000)),
            "AppId": "default_app",
            "JobType": "2D",
            "Text": request.text,
            "Avatar": request.avatar or "default_2d_male_01",
            "Voice": request.voice or "longxiaochun",
            "VideoCodec": "mp4",
            "Width": "720",
            "Height": "1080"
        }
        
        print(f"提交数字人视频任务: text={request.text[:50]}...")
        
        # 发送请求
        response = http_requests.get(url, params=params, timeout=30)
        result = response.json()
        print(f"任务提交响应: {result}")
        
        # 检查是否成功
        if "TaskId" not in result.get("Data", {}):
            error_msg = result.get("Message") or result.get("Code") or str(result)
            return {"error": f"提交失败: {error_msg}"}
        
        task_id = result["Data"]["TaskId"]
        print(f"任务提交成功，TaskId: {task_id}")
        
        # 轮询查询结果
        max_wait_time = 120
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            time.sleep(3)
            
            query_params = {
                "Action": "GetJobResult",
                "Version": "2022-01-30",
                "AccessKeyId": ak_id,
                "TaskId": task_id,
                "Format": "JSON"
            }
            
            query_response = http_requests.get(url, params=query_params, timeout=30)
            query_result = query_response.json()
            
            if query_result.get("Data"):
                status = query_result["Data"]["Status"]
                print(f"任务状态: {status}")
                
                if status == "SUCCESS":
                    video_url = query_result["Data"]["VideoUrl"]
                    print(f"视频生成成功: {video_url}")
                    return {
                        "success": True,
                        "taskId": task_id,
                        "videoUrl": video_url
                    }
                elif status == "FAIL":
                    error_msg = query_result["Data"].get("ErrorMessage") or "未知错误"
                    print(f"任务失败: {error_msg}")
                    return {"error": f"视频生成失败: {error_msg}"}
        
        return {"error": "视频生成超时，请稍后重试"}
        
    except Exception as e:
        print(f"数字人视频生成失败: {e}")
        import traceback
        traceback.print_exc()
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "数字人视频生成失败: " + _msg}

@app.get("/api/exam/questions")
async def get_exam_questions(category: Optional[str] = None, limit: Optional[int] = None):
    questions = db.get_exam_questions(category, limit)
    return {"questions": questions}

@app.get("/api/exam/search")
async def search_exam_questions(keyword: str, category: Optional[str] = None):
    questions = db.search_exam_questions(keyword, category)
    return {"questions": questions}

@app.post("/api/exam/questions")
async def add_exam_question(question: str, answer: str, analysis: str, category: str):
    question_id = db.add_exam_question(question, answer, analysis, category)
    return {"message": "添加成功", "question_id": question_id}

@app.post("/api/learning/recommend-resources")
async def recommend_resources(request: RecommendResourcesRequest, _user: dict = Depends(get_current_user)):
    request.user_id = current_user_id(_user)
    try:
        interview_history = None
        if request.user_id:
            interviews = db.get_user_interviews(request.user_id)
            if interviews and len(interviews) > 0:
                interview_history = interviews

        try:
            resources = doubao_client.recommend_learning_resources(
                job_type=request.job_type,
                weak_areas=request.weak_areas,
                interview_history=interview_history
            )
        except AttributeError:
            resources = None

        if resources:
            return resources
        else:
            from data.job_knowledge_base import LEARNING_RESOURCES
            job_resources = LEARNING_RESOURCES.get(request.job_type, {})
            if isinstance(job_resources, dict):
                all_resources = []
                for category, items in job_resources.items():
                    if isinstance(items, list):
                        all_resources.extend(items)
                return {
                    "resources": all_resources[:8],
                    "study_advice": "根据岗位要求推荐的基础学习资源"
                }
            else:
                return {
                    "resources": [],
                    "study_advice": "暂无推荐资源"
                }
    except Exception as e:
        print(f"推荐学习资源失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {
            "error": "推荐失败",
            "message": _msg
        }

@app.get("/api/learning/history-analysis")
async def analyze_history(user_id: Optional[int] = None, _user: dict = Depends(get_current_user)):
    user_id = current_user_id(_user)
    try:
        interviews = db.get_user_interviews(user_id)
        if not interviews or len(interviews) == 0:
            return {"message": "暂无面试记录"}

        detailed_interviews = []
        for interview in interviews:
            interview_id = interview.get('id')
            report = db.get_evaluation_report(interview_id)
            detailed_interviews.append({
                **interview,
                "report": report
            })

        analysis = doubao_client.analyze_interview_history(user_id, detailed_interviews)

        if analysis:
            return analysis
        else:
            return {
                "message": "分析完成",
                "interview_count": len(interviews)
            }
    except Exception as e:
        print(f"历史分析失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {
            "error": "分析失败",
            "message": _msg
        }

CATEGORIES = ["组织协调", "应急应变", "技术能力", "言语表达", "项目经验"]

def generate_single_question(category, question_type, difficulty="medium"):
    """使用AI生成单个题目"""
    try:
        difficulty_text = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty, "中等")
        question_type_text = "单选题" if question_type == "single" else "多选题"

        system_prompt = f"""你是一位专业的面试题库专家。请为"事业单位结构化面试"生成一道精选题目。

题目要求：
1. 题型：{question_type_text}（{question_type}）
2. 类别：{category}
3. 难度：{difficulty_text}
4. 题目必须符合事业单位面试风格

单选题要求：4个选项，只有1个正确选项，correct_answer格式为单个字母如"A"
多选题要求：4个选项，有2-4个正确选项，correct_answer格式为多个字母用逗号分隔如"A,B"或"A,C,D"

请按以下JSON格式返回（不要有任何额外内容）：
{{"question": "题目内容", "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"], "correct_answer": "A", "analysis": "解析内容"}}"""

        user_prompt = f"请为{category}类别生成一道{question_type_text}。"

        response = global_doubao_client.generate_response(system_prompt, user_prompt, temperature=0.7, max_tokens=500)

        if response:
            import re
            json_match = extract_json(response)
            if json_match:
                import json as json_lib
                return json_match

    except Exception as e:
        print(f"AI生成题目失败: {e}")

    return None


def generate_selected_questions_batch(count_per_category=2, question_type="single"):
    """批量生成精选题目"""
    questions = []
    for category in CATEGORIES:
        for i in range(count_per_category):
            difficulty = "easy" if i == 0 else "medium"
            question = generate_single_question(category, question_type, difficulty)
            if question:
                questions.append({
                    "question_type": question_type,
                    "category": category,
                    "difficulty": difficulty,
                    **question
                })
    return questions


@app.get("/api/selected-questions")
async def get_selected_questions(
    category: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: Optional[int] = None
):
    """获取精选题库列表"""
    try:
        questions = db.get_selected_questions(
            category=category,
            question_type=question_type,
            difficulty=difficulty,
            limit=limit
        )

        for q in questions:
            if isinstance(q.get('options'), str):
                import json as json_lib
                try:
                    q['options'] = json_lib.loads(q['options'])
                    q['correct_answer'] = json_lib.loads(q['correct_answer']) if isinstance(q.get('correct_answer'), str) else q.get('correct_answer')
                except:
                    pass

        return {"questions": questions, "total": len(questions)}
    except Exception as e:
        print(f"获取精选题库失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"questions": [], "total": 0, "error": _msg}


@app.get("/api/selected-questions/categories")
async def get_categories():
    """获取所有分类"""
    return {"categories": CATEGORIES}


@app.post("/api/selected-questions/generate")
async def generate_selected_questions_api(count_per_category: int = 2, question_type: str = "single"):
    """AI生成精选题目"""
    try:
        if question_type not in ["single", "multiple"]:
            question_type = "single"

        generated = await asyncio.to_thread(generate_selected_questions_batch, count_per_category, question_type)

        saved_count = 0
        for q in generated:
            try:
                options = q.get('options', [])
                correct_answer = q.get('correct_answer', '')

                if isinstance(correct_answer, list):
                    correct_answer = json.dumps(correct_answer)
                elif isinstance(correct_answer, str) and not correct_answer.startswith('['):
                    pass

                db.add_selected_question(
                    question_type=q.get('question_type', question_type),
                    question=q.get('question', ''),
                    options=options,
                    correct_answer=correct_answer,
                    analysis=q.get('analysis', ''),
                    category=q.get('category', ''),
                    difficulty=q.get('difficulty', 'medium')
                )
                saved_count += 1
            except Exception as e:
                print(f"保存题目失败: {e}")

        return {
            "message": f"成功生成并保存 {saved_count} 道题目",
            "generated_count": saved_count
        }
    except Exception as e:
        print(f"生成精选题库失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "生成失败", "message": _msg}


@app.get("/api/selected-questions/stats")
async def get_question_stats():
    """获取题库统计信息"""
    try:
        stats = {}
        for category in CATEGORIES:
            single_count = db.get_selected_questions_count(category=category, question_type="single")
            multiple_count = db.get_selected_questions_count(category=category, question_type="multiple")
            stats[category] = {
                "single": single_count,
                "multiple": multiple_count,
                "total": single_count + multiple_count
            }

        total = sum(s["total"] for s in stats.values())

        return {
            "stats": stats,
            "total": total,
            "categories": CATEGORIES
        }
    except Exception as e:
        print(f"获取题库统计失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": _msg}


@app.delete("/api/selected-questions/{question_id}")
async def delete_question(question_id: int):
    """删除题目"""
    success = db.delete_selected_question(question_id)
    if success:
        return {"message": "删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")


@app.get("/api/selected-questions/search")
async def search_questions(keyword: str, category: Optional[str] = None, question_type: Optional[str] = None):
    """搜索精选题目"""
    try:
        questions = db.search_selected_questions(keyword, category, question_type)

        for q in questions:
            if isinstance(q.get('options'), str):
                import json as json_lib
                try:
                    q['options'] = json_lib.loads(q['options'])
                    q['correct_answer'] = json_lib.loads(q['correct_answer']) if isinstance(q.get('correct_answer'), str) else q.get('correct_answer')
                except:
                    pass

        return {"questions": questions, "total": len(questions)}
    except Exception as e:
        print(f"搜索失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"questions": [], "total": 0, "error": _msg}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message("AI: 您好，这是一条模拟回复。在实际应用中，我会根据您的回答生成更有针对性的内容。", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

        return comprehensive_report


# ==================== 语音处理相关功能 ====================

class SpeechUploadRequest(BaseModel):
    interview_id: int
    text: str
    duration: Optional[float] = 0.0  # 语音时长（秒）

@app.post("/api/speech/upload")
async def upload_speech(request: Request, _user: dict = Depends(get_current_user)):
    """上传语音并进行分析"""
    try:
        form_data = await request.form()
        interview_id = form_data.get('interview_id')
        user_text = form_data.get('text', '')
        duration_str = form_data.get('duration', '0')
        audio_file = form_data.get('audio')

        try:
            interview_id = int(interview_id)
        except:
            return {"error": "无效的面试ID"}

        try:
            duration = float(duration_str)
        except:
            duration = 0.0

        audio_data = None
        if audio_file:
            audio_data = await audio_file.read()

        recognized_text = user_text.strip() if user_text else ""
        volume_db = 0.0
        volume_level = "正常"
        speed_wpm = 0
        speed_level = "正常"
        confidence = 50

        if not recognized_text and audio_data:
            try:
                import numpy as np
                import io as io_module

                samples, sample_rate = convert_audio_to_whisper_format(audio_data)
                print(f"音频转换结果: samples长度={len(samples) if samples is not None else 'None'}, sample_rate={sample_rate}")

                if samples is not None and len(samples) > 1600:
                    rms = np.sqrt(np.mean(np.square(samples)) + 1e-10)
                    volume_db_test = 20 * np.log10(rms)
                    print(f"音频RMS: {rms:.6f}, 音量dB: {volume_db_test:.2f}")

                    try:
                        print(f"开始语音识别...")
                        result = await asyncio.to_thread(speech_recognizer.recognize, audio_data)
                        recognized_text = result.get("text", "").strip()
                        print(f"识别结果: '{recognized_text}'")
                    except Exception as e:
                        print(f"Whisper识别失败: {e}")
                        import traceback
                        traceback.print_exc()

                    rms = np.sqrt(np.mean(np.square(samples)) + 1e-10)
                    volume_db = round(20 * np.log10(rms), 2)

                    if volume_db > -20:
                        volume_level = "大声"
                    elif volume_db < -40:
                        volume_level = "小声"
                    else:
                        volume_level = "正常"

                    audio_duration = len(samples) / sample_rate
                    if audio_duration > 0.5 and recognized_text:
                        char_count = len(recognized_text.strip())
                        speed_wpm = int(char_count / audio_duration * 60)
                        if speed_wpm > 180:
                            speed_level = "偏快"
                        elif speed_wpm < 100:
                            speed_level = "偏慢"
                        else:
                            speed_level = "正常"

                        if -35 < volume_db < -20:
                            confidence = min(100, 40 + (40 if 120 < speed_wpm < 180 else (25 if 100 < speed_wpm < 200 else 20)) + 20)
                        elif volume_db > -20:
                            confidence = min(100, 30 + (40 if 120 < speed_wpm < 180 else (25 if 100 < speed_wpm < 200 else 20)) + 20)
                        else:
                            confidence = min(100, 25 + (40 if 120 < speed_wpm < 180 else (25 if 100 < speed_wpm < 200 else 20)) + 20)
            except Exception as asr_error:
                print(f"本地语音识别失败: {asr_error}")

        if not recognized_text:
            recognized_text = "语音回答"

        speech_analysis = doubao_client.analyze_speech(recognized_text)

        speech_rate = 0.0
        if len(recognized_text) > 0 and duration > 0:
            speech_rate = len(recognized_text) / duration

        speech_rate_score = speech_analysis.get("speech_rate_score", 70) if speech_analysis else 70
        if speed_wpm > 0:
            speech_rate_score = min(100, max(0, 50 + (speed_wpm - 120) // 3))
        confidence_score = confidence
        tone_type = speech_analysis.get("tone_type", "neutral") if speech_analysis else "neutral"
        overall_analysis = speech_analysis.get("overall_analysis", "") if speech_analysis else ""

        speech_record_id = db.save_speech_record(
            interview_id=interview_id,
            message_id=None,
            audio_data=audio_data,
            audio_format='webm',
            duration=duration,
            speech_rate=speech_rate_score,
            confidence_score=confidence_score,
            tone_type=tone_type,
            overall_analysis=overall_analysis
        )

        return {
            "success": True,
            "speech_record_id": speech_record_id,
            "text": recognized_text,
            "speech_analysis": speech_analysis,
            "metrics": {
                "speech_rate": round(float(speech_rate), 1),
                "speech_rate_score": int(speech_rate_score),
                "confidence_score": int(confidence_score),
                "tone_type": tone_type,
                "duration": round(float(duration), 2),
                "char_count": len(recognized_text),
                "volume_db": float(volume_db),
                "volume": volume_level,
                "speed_wpm": int(speed_wpm),
                "speed": speed_level
            }
        }
    except Exception as e:
        print(f"语音上传失败: {e}")
        import traceback
        traceback.print_exc()
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "处理失败: " + _msg}

@app.get("/api/speech/record/{record_id}")
async def get_speech_record(record_id: int, _user: dict = Depends(get_current_user)):
    """获取语音记录"""
    try:
        record = db.get_speech_record_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="语音记录不存在")
        
        if record.get('audio_data'):
            return Response(
                content=record['audio_data'],
                media_type=f"audio/{record.get('audio_format', 'webm')}"
            )
        else:
            return {"error": "无音频数据"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取语音记录失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "获取失败: " + _msg}

@app.get("/api/speech/records/{interview_id}")
async def get_speech_records(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取面试的所有语音记录"""
    assert_interview_owner(db, interview_id, _user)
    try:
        records = db.get_speech_records(interview_id)
        for record in records:
            if record.get('audio_data'):
                record['audio_data'] = None  # 不返回音频数据，只返回元数据
        return {"records": records}
    except Exception as e:
        print(f"获取语音记录失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "获取失败: " + _msg}

@app.get("/api/speech/summary/{interview_id}")
async def get_speech_summary(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取语音分析汇总"""
    assert_interview_owner(db, interview_id, _user)
    try:
        summary = db.get_speech_analysis_summary(interview_id)
        if summary:
            return {
                "status": "success",
                "summary": summary
            }
        else:
            return {
                "status": "not_found",
                "message": "暂无语音分析数据"
            }
    except Exception as e:
        print(f"获取语音分析汇总失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "获取失败: " + _msg}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



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

        user_prompt = f"以下是候选人的简历，请提取关键信息：\n{resume_text}"

        response = global_doubao_client.generate_response(
            system_prompt,
            user_prompt,
            temperature=0.3,
            max_tokens=2000
        )

        if response:
            import re
            json_match = extract_json(response)
            if json_match:
                import json as json_lib
                return json_match

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

        user_prompt = f"以下是候选人的简历，请进行评价：\n{resume_text}"

        response = global_doubao_client.generate_response(
            system_prompt,
            user_prompt,
            temperature=0.5,
            max_tokens=1500
        )

        if response:
            import re
            json_match = extract_json(response)
            if json_match:
                import json as json_lib
                evaluation = json_match
                
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
        user_prompt = f"候选人简历信息：\n{resume_json}\n\n请生成{question_count}个针对性问题。"

        response = global_doubao_client.generate_response(
            system_prompt,
            user_prompt,
            temperature=0.7,
            max_tokens=800
        )

        if response:
            import re
            json_match = extract_json(response)
            if json_match:
                result = json_match
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
        resume_info = await asyncio.to_thread(extract_resume_info, request.resume_text, request.job_type)
        return {"status": "success", "resume_info": resume_info}
    except Exception as e:
        print(f"简历提取API失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"status": "error", "message": _msg}


@app.post("/api/resume/evaluate")
async def evaluate_resume(request: ResumeEvaluationRequest, _user: dict = Depends(get_current_user)):
    """评价简历制作质量"""
    assert_interview_owner(db, request.interview_id, _user)
    try:
        interview = db.get_interview(request.interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")

        resume_text = interview.get('resume_text', '')
        if not resume_text:
            raise HTTPException(status_code=400, detail="简历内容不存在")

        evaluation = await asyncio.to_thread(evaluate_resume_quality, resume_text, request.job_type, request.interview_id)
        return {"status": "success", "evaluation": evaluation}
    except HTTPException:
        raise
    except Exception as e:
        print(f"简历评价API失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"status": "error", "message": _msg}


@app.get("/api/resume/evaluation/{interview_id}")
async def get_resume_evaluation(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取简历评价结果"""
    assert_interview_owner(db, interview_id, _user)
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
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"status": "error", "message": _msg}


@app.post("/api/resume/generate-questions")
async def generate_questions_from_resume(request: ResumeExtractRequest):
    """根据简历生成针对性问题"""
    try:
        resume_info = await asyncio.to_thread(extract_resume_info, request.resume_text, request.job_type)
        questions = await asyncio.to_thread(generate_resume_based_questions, resume_info, request.job_type, 3)
        return {"status": "success", "questions": questions, "resume_info": resume_info}
    except Exception as e:
        print(f"生成简历问题API失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"status": "error", "message": _msg}


MAX_RESUME_PDF_BYTES = 10 * 1024 * 1024


@app.post("/api/resume/parse-pdf")
async def parse_resume_pdf(file: UploadFile = File(...), _user: dict = Depends(get_current_user)):
    """解析 PDF 简历。

    修复前：不校验类型和大小，整份文件直接 read() 进内存（任意大小都收），
    且 pdfplumber 抛异常时会跳过 os.unlink，临时文件持续泄漏。
    """
    import tempfile

    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    content = await file.read(MAX_RESUME_PDF_BYTES + 1)
    if len(content) > MAX_RESUME_PDF_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 10 MB 限制")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="文件内容不是有效的 PDF")

    tmp_path = None
    try:
        import pdfplumber

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return {"status": "success", "text": "", "message": "PDF 中未提取到文本"}

        return {"status": "success", "text": text.strip()}
    except ImportError:
        logger.warning("未安装 pdfplumber，PDF 解析不可用")
        raise HTTPException(status_code=503, detail="服务端未安装 PDF 解析组件")
    except Exception as exc:
        trace_id = log_exception("parse_resume_pdf", exc)
        return {"status": "error", "message": "PDF 解析失败 (trace_id=%s)" % trace_id}
    finally:
        # 无论成功失败都清理临时文件
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                logger.warning("临时文件删除失败: %s", tmp_path)


# ==================== 面部分析相关功能 ====================

class FaceAnalysisRequest(BaseModel):
    image: str
    prompt: Optional[str] = "分析这张图片中的人物表情和状态"

@app.post("/api/doubao/face-analysis")
async def analyze_face(request: FaceAnalysisRequest):
    """使用豆包大模型进行面部分析"""
    try:
        import base64
        import json as json_lib

        # 构建提示词
        system_prompt = """你是一位专业的面试教练，擅长通过面部表情分析面试者的情绪和状态。
请根据提供的图片，分析面试者的以下维度：
1. 情绪状态（紧张/放松/焦虑/自信/平静等）
2. 自信度评分（0-100分）
3. 面试状态（专注/走神/疲惫/活跃等）
4. 简短改进建议（1-2句话）

请以JSON格式返回，字段为：emotion, confidence, focus, suggestion"""

        user_prompt = "请分析这张图片中人物的表情和面试状态"

        # 如果有图片数据，解码并临时保存
        image_data = None
        if request.image:
            try:
                image_data = base64.b64decode(request.image)
            except Exception as decode_error:
                print(f"图片解码失败: {decode_error}")

        if image_data:
            # 使用临时文件
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name

            try:
                response = global_doubao_client.analyze_face_expression(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            response = None

        if response:
            try:
                result = json_lib.loads(response)
                return result
            except:
                return {
                    "emotion": "平静",
                    "confidence": 70,
                    "focus": "专注",
                    "suggestion": "保持当前状态，继续积极表达"
                }

        # 默认响应
        return {
            "emotion": "平静",
            "confidence": 75,
            "focus": "专注",
            "suggestion": "保持良好状态，继续积极展示自己的能力"
        }

    except Exception as e:
        print(f"面部分析失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "emotion": "未知",
            "confidence": 0,
            "focus": "未知",
            "suggestion": "分析失败，请稍后重试"
        }


@app.post("/api/interview/save-face-analysis")
async def save_face_analysis(request: Request, _user: dict = Depends(get_current_user)):
    """保存面部分析结果"""
    try:
        data = await request.json()
        interview_id = data.get('interview_id')
        emotion = data.get('emotion', '')
        confidence = data.get('confidence', 0)
        focus = data.get('focus', '')
        suggestion = data.get('suggestion', '')
        timestamp = data.get('timestamp')

        if not interview_id:
            return {"error": "缺少面试ID"}

        # 保存到数据库
        analysis_id = db.save_face_analysis(
            interview_id=interview_id,
            emotion=emotion,
            confidence=confidence,
            focus=focus,
            suggestion=suggestion,
            timestamp=timestamp
        )

        return {
            "status": "success",
            "analysis_id": analysis_id
        }
    except Exception as e:
        print(f"保存面部分析失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "保存失败: " + _msg}


@app.get("/api/interview/face-analysis/{interview_id}")
async def get_face_analysis(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取面试的面部分析结果"""
    assert_interview_owner(db, interview_id, _user)
    try:
        analyses = db.get_face_analyses(interview_id)
        summary = db.get_face_analysis_summary(interview_id)

        return {
            "status": "success",
            "analyses": analyses,
            "summary": summary
        }
    except Exception as e:
        print(f"获取面部分析失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "获取失败: " + _msg}


@app.get("/api/interview/face-analysis-summary/{interview_id}")
async def get_face_analysis_summary_api(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取面部分析汇总"""
    assert_interview_owner(db, interview_id, _user)
    try:
        summary = db.get_face_analysis_summary(interview_id)
        if summary:
            return {
                "status": "success",
                "summary": summary
            }
        else:
            return {
                "status": "not_found",
                "message": "暂无面部分析数据"
            }
    except Exception as e:
        print(f"获取面部分析汇总失败: {e}")
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "获取失败: " + _msg}



class ComprehensiveReportRequest(BaseModel):
    interview_id: int

@app.post("/api/interview/comprehensive-report")
async def generate_comprehensive_report(request: ComprehensiveReportRequest, _user: dict = Depends(get_current_user)):
    """生成综合评估报告（整合对话+简历+面部分析）"""
    assert_interview_owner(db, request.interview_id, _user)
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
        
        # 6. 获取语音分析汇总
        speech_summary = db.get_speech_analysis_summary(interview_id)

        # 7. 计算综合评分
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
        
        if speech_summary and speech_summary.get('avg_confidence'):
            total_score += speech_summary['avg_confidence']
            score_count += 1

        final_score = round(total_score / score_count, 1) if score_count > 0 else 0

        # 8. 生成综合建议
        suggestions = []

        if face_summary:
            if face_summary.get('dominant_emotion') == '紧张':
                suggestions.append("建议：在面试中保持放松心态，可以尝试深呼吸和积极自我暗示")
            elif face_summary.get('dominant_emotion') == '焦虑':
                suggestions.append("建议：面试前做好充分准备，熟悉岗位要求和公司背景")

            if face_summary.get('dominant_focus') == '走神':
                suggestions.append("建议：面试时保持专注，认真倾听面试官的问题")
        
        if speech_summary:
            if speech_summary.get('avg_speech_rate', 0) < 5:
                suggestions.append("建议：说话时语速可以适当加快，让表达更有节奏感")
            elif speech_summary.get('avg_speech_rate', 0) > 10:
                suggestions.append("建议：说话时语速可以适当放缓，让表达更清晰")
            
            if speech_summary.get('dominant_tone') == 'nervous':
                suggestions.append("建议：面试时可以通过深呼吸和积极自我暗示来缓解紧张情绪")
            elif speech_summary.get('dominant_tone') == 'anxious':
                suggestions.append("建议：面试前多做模拟练习，增强自信心")

        if resume_evaluation:
            improvements = resume_evaluation.get('improvements', [])
            if improvements:
                for imp in improvements[:2]:
                    suggestions.append(f"简历优化：{imp}")

        if evaluation_report:
            suggestions_from_report = evaluation_report.get('improvement_suggestions', [])
            for suggestion in suggestions_from_report[:3]:
                suggestions.append(f"面试技巧：{suggestion}")

        # 9. 组装综合报告
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
            "speech_analysis": speech_summary,
            "improvement_plan": improvement_plan,
            "comprehensive_suggestions": suggestions,
            "overall_assessment": generate_overall_assessment(final_score, face_summary, resume_evaluation, speech_summary)
        }

        return comprehensive_report

    except Exception as e:
        print(f"生成综合报告失败: {e}")
        import traceback
        traceback.print_exc()
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "生成综合报告失败: " + _msg}


def generate_overall_assessment(score, face_summary, resume_evaluation, speech_summary=None):
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
    
    additional_comments = []
    
    if speech_summary:
        if speech_summary.get('avg_confidence', 0) >= 80:
            additional_comments.append("语音表达自信沉稳，给面试官留下良好印象。")
        elif speech_summary.get('avg_confidence', 0) < 50:
            additional_comments.append("建议加强语音表达的自信心训练。")
        
        if speech_summary.get('dominant_tone') == 'confident':
            additional_comments.append("语气自信坚定，展现出良好的心理素质。")
        elif speech_summary.get('dominant_tone') == 'nervous':
            additional_comments.append("面试时略显紧张，建议多进行模拟练习。")
    
    if additional_comments:
        description += " " + " ".join(additional_comments)

    return {
        "level": level,
        "description": description
    }


@app.get("/api/interview/full-evaluation/{interview_id}")
async def get_full_evaluation(interview_id: int, _user: dict = Depends(get_current_user)):
    """获取完整评估报告"""
    assert_interview_owner(db, interview_id, _user)
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
        _trace = log_exception("main.py", e)
        _msg = "服务器内部错误 (trace_id=%s)" % _trace
        return {"error": "获取完整评估失败: " + _msg}


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    token: Optional[str] = None


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """登录成功后下发签名令牌。

    修复前：不下发任何凭证，且 role 是拿用户名跟
    {"admin","administrator","管理员"} 做字符串比对算出来的 ——
    注册一个叫 admin 的账号就是管理员。现在 role 只认数据库 users.role 列。
    """
    user = db.login_user(request.username, request.password)
    if not user:
        return AuthResponse(success=False, message="用户名或密码错误")

    role = user.get("role") or "user"
    return AuthResponse(
        success=True,
        message="登录成功",
        user_id=user["id"],
        username=user["username"],
        role=role,
        token=create_token(user),
    )
