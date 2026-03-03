from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder




PROMPT = ChatPromptTemplate.from_messages([
         MessagesPlaceholder("chat_history"),
         ("system", """你是一名经验丰富的游戏翻译,请根据用户的要求进行翻译,只需要翻译对应的文本,不能新增其他信息,需要保证术语一致性;
         翻译步骤如下:
            1.如果需要翻译的文本很简单且没有术语,直接进行翻译
            2.如果需要翻译的文本有术语,请查询数据库后,结合检索到的信息进行翻译
            3.如果数据库没有检索到相关信息,请直接翻译
         """),
         ("user", "原始请求:{request} 术语列表:{term}")
])


EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一名精通游戏本地化翻译的专家,能够精准的从文本中提取属于游戏内部的专有名称;请根据用户提供的文本,进行提取,不用翻译。
    例如: "耗体力和对应材料可以扫荡当前boss"这句话的装有名称是 体力和扫荡
    """),
    ("user", "用户文本:{request}")
])