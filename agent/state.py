from typing import TypedDict, List

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class TranslationState(TypedDict):
    origin_query: Annotated[str, "用户原始输入"]
    term: Annotated[list[str], "术语"]
    messages: Annotated[list[AnyMessage], add_messages]
    final_result: Annotated[AnyMessage,"最终结果"]


class Term(BaseModel):
    term_list: List[str] = Field(description="专业术语列表")