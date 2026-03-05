import asyncio
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from agent.translation_agent import workflow




if __name__ == '__main__':
    load_dotenv()
    # app = workflow.compile(checkpointer=MemorySaver())
    app = workflow.compile()
    async def translate(input_str):
        thread_config = {"configurable": {"thread_id": "1"}}
        res = None
        input = {"origin_query": input_str}
        async for event in app.astream(input, config=thread_config, stream_mode="values"):
            if "final_result" in event:
                res = event["final_result"].content
        return res
    async def main():
        data = ["帮我把这句话翻译为英文  恭喜你获得了异界生命核，太幸运了吧", "帮我把这句话翻译为英文  恭喜你获得了异界生命核，太幸运了吧"]
        res_list = []
        for each in data:
            res = await translate(each)
            res_list.append(res)


        print(res_list)


    asyncio.run(main())