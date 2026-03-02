from langchain_core.prompts import ChatPromptTemplate

PROMPT = ChatPromptTemplate.from_template(
    """
    你是一名经验丰富游戏翻译,请根据用户的要求进行翻译
    """
)