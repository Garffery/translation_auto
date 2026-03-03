from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from .vector_store.milvus_service import milvus_service
from config.setting import settings
class QueryInput(BaseModel):
    query: str = Field( description= "用于检索的字符串")


@tool(args_schema=QueryInput, return_direct= True)
async def milvus_hy_search(query: str) -> List[dict]:
    """从Milvus向量数据库检索信息的时候调用"""
    res = await milvus_service.hy_query(query)
    print(res)
    return res