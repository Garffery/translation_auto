import asyncio
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from agent.translation_agent import workflow




if __name__ == '__main__':
    load_dotenv()
    app = workflow.compile(checkpointer=MemorySaver())
    async def main():
        inputs = {"origin_query": "帮我把这句话翻译为英文  恭喜你获得了异界生命核，太幸运了吧"}
        thread_config = {"configurable": {"thread_id": "1"}}
        print("Starting interaction...")
        async for event in app.astream(inputs, config=thread_config, stream_mode="values"):
            print(f"Event: {event}")


        # inputs = {"origin_query": "帮我把上面这句话翻译成繁体"}
        inputs = {"origin_query": "这句话的繁体是怎么样的"}
        thread_config = {"configurable": {"thread_id": "1"}}
        print("Starting interaction...")
        async for event in app.astream(inputs, config=thread_config, stream_mode="values"):
            print(f"Event: {event}")


    asyncio.run(main())