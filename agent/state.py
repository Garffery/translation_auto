from typing import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


class TranslationState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

