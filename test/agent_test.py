import asyncio
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from agent.translation_agent import workflow




if __name__ == '__main__':
    load_dotenv()
    app = workflow.compile(checkpointer=MemorySaver())
    async def main():
        inputs = {"messages": ["帮我将烈风传说翻译为英文"]}
        thread_config = {"configurable": {"thread_id": "1"}}
        print("Starting interaction...")
        async for event in app.astream(inputs, config=thread_config, stream_mode="values"):
            print(f"Event: {event}")


    asyncio.run(main())