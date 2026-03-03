from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from .vector_store.milvus_service import milvus_service
from config.setting import settings
class QueryInput(BaseModel):
    query: str = Field( description= "用于检索的字符串")


@tool(args_schema=QueryInput, return_direct= True)
async def milvus_hy_search(query: str) -> str:
    """从Milvus向量数据库检索信息的时候调用"""
    res = await milvus_service.hy_query("collection_hy_1", query)
    print(f"检索到的原始数据：{res}")
    res1 = []
    for item in res:
        res1.append(item["entity"]["source"])
    res_str = "检索到的信息" +  ",".join(res1)
    print(f"混合检索结果：{res_str}")
    return res_str