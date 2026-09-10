from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIChatbot:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        self.model = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.memory = ConversationBufferMemory()
        self.prompt_template = ChatPromptTemplate.from_template(
            """你是一位专业的AI面试官，正在对候选人进行面试。
            岗位：{position}
            面试轮次：{round}
            对话历史：{history}
            候选人的回答：{input}
            
            请根据以上信息，生成下一步的面试问题或评价。
            回答要专业、针对性强，符合岗位要求。
            """
        )
    
    def generate_response(self, user_input, position, round):
        """生成AI面试官的回复"""
        # 获取对话历史
        history = self.memory.load_memory_variables({})["history"]
        
        # 构建提示词
        prompt = self.prompt_template.format(
            position=position,
            round=round,
            history=history,
            input=user_input
        )
        
        # 生成回复
        response = self.model.predict(prompt)
        
        # 更新对话历史
        self.memory.save_context({"input": user_input}, {"output": response})
        
        return response
    
    def start_interview(self, position, round):
        """开始面试，生成初始问题"""
        self.memory.clear()
        return f"你好！我是AI面试官，今天将对你进行{position}岗位的{round}面试。请先做一个简单的自我介绍。"
