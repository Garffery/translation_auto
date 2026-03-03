from langchain_deepseek import ChatDeepSeek
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from agent.prompts import PROMPT as TranslationAgentPrompt
from agent.state import TranslationState


async def get_translation_tools():
    return []



async def call_model(state:TranslationState):
    print(state)
    tools = await get_translation_tools()
    llm = ChatDeepSeek(model="deepseek-chat").bind_tools(tools)
    chain = TranslationAgentPrompt | llm
    message = state["messages"][-1]
    print(f"消息：{message}")
    response = await chain.ainvoke({"request":message.content, "chat_history":[]})
    return {"messages": response}


async def tool_node(state: TranslationState):
    print(f"进入工具节点-------------》")
    message = state["messages"][-1]
    tools = await get_translation_tools()
    tool_map = {t.name: t for t in tools}
    response = []
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        if tool_name in tool_map:
            selected_tool = tool_map[tool_name]
            try:
                observation = await selected_tool.ainvoke(tool_call["args"])
            except Exception as e:
                observation = f"Error executing tool {tool_name}: {str(e)}"

            response.append({
                "role": "tool",
                "content": observation,
                "name": tool_name,
                "tool_call_id": tool_call["id"]
            })
        else:
            response.append({
                "role": "tool",
                "content": f"Error: Tool {tool_name} not found.",
                "name": tool_name,
                "tool_call_id": tool_call["id"]
            })
    return {"messages": response}


async def should_use_tool(state: TranslationState):
    print(f"-----------判断是否执行工具界面------------")
    message = state["messages"][-1]
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print("确定进入工具界面")
        return "tool_node"
    else:
        print("结束流程")
        return END


workflow = StateGraph(TranslationState)

workflow.add_node("call_model", call_model)
workflow.add_node("tool_node", tool_node)

workflow.add_edge(START, "call_model")
workflow.add_conditional_edges("call_model", should_use_tool, [END, "tool_node"])
workflow.add_edge("tool_node", "call_model")


