from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class KnowledgeBase:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        self.vectorstore = None
        self.init_knowledge_base()
    
    def init_knowledge_base(self):
        """初始化知识库"""
        if os.path.exists(self.persist_directory):
            # 加载现有知识库
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # 创建新的知识库
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def add_document(self, file_path):
        """添加文档到知识库"""
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            
            # 分割文档
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.split_documents(documents)
            
            # 添加到向量数据库
            self.vectorstore.add_documents(docs)
            self.vectorstore.persist()
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def add_text(self, text, metadata=None):
        """添加文本到知识库"""
        try:
            self.vectorstore.add_texts([text], metadatas=[metadata] if metadata else None)
            self.vectorstore.persist()
            return True
        except Exception as e:
            print(f"添加文本失败: {e}")
            return False
    
    def query(self, query, k=3):
        """查询知识库"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"查询失败: {e}")
            return []
    
    def get_relevant_context(self, query, k=3):
        """获取相关上下文"""
        results = self.query(query, k=k)
        context = "\n".join([doc.page_content for doc in results])
        return context
