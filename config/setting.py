import os

from pydantic_settings import BaseSettings, SettingsConfigDict

env = os.getenv("TRANSLATION-AGENT-ENV", "dev")

class Settings(BaseSettings):

    
    # 应用配置
    APP_NAME: str = "Translation Agent"
    
    # Milvus 配置
    MILVUS_CONNECTION_URL: str = "http://localhost:19530"
    MILVUS_DATABASE_NAME: str = "translation_db"
    MILVUS_COLLECTION_NAME: str = "translation_collection"
    MILVUS_CONSISTENCY_LEVEL: str = "Session"
    MILVUS_DIMENSION: int = 1024
    
    # Ollama 嵌入模型配置
    OLLAMA_EMBEDDING_MODEL: str = "bge-m3"
    OLLAMA_EMBEDDING_BASE_URL: str = "http://localhost:11434"
    model_config = SettingsConfigDict(
        env_file=f"../.env.{env}"
    )



# 创建一个全局的配置实例
settings = Settings()
current_working_directory = os.getcwd()
print("当前工作目录:", current_working_directory)
print(settings.model_dump())