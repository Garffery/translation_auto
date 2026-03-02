from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

PROMPT = ChatPromptTemplate.from_template(
    """
    你是一名经验丰富游戏翻译,请根据用户的要求进行翻译
    用户的要求：{request}
    """
)


PROMPT = ChatPromptTemplate.from_messages([
         ("system", "你是一名经验丰富游戏翻译,请根据用户的要求进行翻译."),
         MessagesPlaceholder("chat_history"),
         ("user", "{request}")
])