import asyncio
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from agent.translation_agent import workflow




if __name__ == '__main__':
    load_dotenv()
    app = workflow.compile(checkpointer=MemorySaver())
    # app = workflow.compile()
    async def main():
        inputs = {"origin_query": "帮我把这句话翻译为英文  魔法师艾丽娅:这本咒语书记录着远古的秘密 玩家:什么秘密 魔法师艾丽娅:那是操控时间之流的力量.......太危险了？"}
        thread_config = {"configurable": {"thread_id": "1"}}
        print("Starting interaction...")
        async for event in app.astream(inputs, config=thread_config):
            if "call_model" in event:
                print(f"最终结果------------: {event}")





        # # inputs = {"origin_query": "帮我把上面这句话翻译成繁体"}
        # inputs = {"origin_query": "玩家:什么秘密"}
        # thread_config = {"configurable": {"thread_id": "1"}}
        # print("Starting interaction...")
        # async for event in app.astream(inputs, config=thread_config, stream_mode="values"):
        #     print(f"Event: {event}")
        #
        # inputs = {"origin_query": "魔法师艾丽娅:那是操控时间之流的力量.......太危险了"}
        # thread_config = {"configurable": {"thread_id": "1"}}
        # print("Starting interaction...")
        # async for event in app.astream(inputs, config=thread_config, stream_mode="values"):
        #     print(f"Event: {event}")


    asyncio.run(main())