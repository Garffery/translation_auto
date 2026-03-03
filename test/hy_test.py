import asyncio

from agent.vector_store.milvus_service import milvus_service

if __name__ == '__main__':
    async def main():
        res = await milvus_service.hy_query(collection_name="collection_hy_1", query_str="血量")
        print(f"混合检索结果：{res}")


    asyncio.run(main())