import asyncio

from agent.vector_store.milvus_service import milvus_service

if __name__ == '__main__':
    async def main():
        res = await milvus_service.hy_query(collection_name="collection_hy_1", query_str="命中率")
        print(res)
        res1 = []
        for item in res:
            res1.append(item["entity"]["source"])
        res_str = ",".join(res1)
        print(f"混合检索结果：{res_str}")


    asyncio.run(main())