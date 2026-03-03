import os

from pydantic_settings import BaseSettings, SettingsConfigDict

env = os.getenv("TRANSLATION-AGENT-ENV", "dev")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{env}", env_file_encoding="utf-8"  # 根据环境动态选择 .env 文件
    )



# 创建一个全局的配置实例
settings = Settings()