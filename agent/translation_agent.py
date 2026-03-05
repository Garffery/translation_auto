from langchain_deepseek import ChatDeepSeek
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from agent.prompts import PROMPT as TranslationAgentPrompt, EXTRACTION_PROMPT
from agent.state import TranslationState, Term
from agent.tools import milvus_hy_search


async def get_translation_tools():
    return [milvus_hy_search]



async def term_extraction(state:TranslationState):
    llm = ChatDeepSeek(model="deepseek-chat").with_structured_output(Term)
    chain = EXTRACTION_PROMPT | llm
    message = state["origin_query"]
    response = await chain.ainvoke({"request":message})
    print(f"提取到的术语:{response.term_list}")
    return {"term": response.term_list}




async def call_model(state:TranslationState):
    tools = await get_translation_tools()
    llm = ChatDeepSeek(model="deepseek-chat").bind_tools(tools)
    chain = TranslationAgentPrompt | llm
    message = state["origin_query"]
    print(f"消息：{message}")
    term_list = state["term"]
    print(f"术语列表:{term_list}")
    term_str = ",".join(term_list)
    response = await chain.ainvoke({"request":message, "chat_history":state["messages"], "term":term_str})
    print(response)
    return {"messages": response}


async def tool_node(state: TranslationState):
    print(f"进入工具节点-------------》")
    message = state["messages"][-1]
    tools = await get_translation_tools()
    tool_map = {t.name: t for t in tools}
    response = []
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        print(f"工具名称:{tool_name}")
        if tool_name in tool_map:
            selected_tool = tool_map[tool_name]
            try:
                print(f"工具参数：{tool_call["args"]}")
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
workflow.add_node("term_extraction_node", term_extraction)

workflow.add_edge(START, "term_extraction_node")
workflow.add_edge("term_extraction_node", "call_model")
workflow.add_conditional_edges("call_model", should_use_tool, [END, "tool_node"])
workflow.add_edge("tool_node", "call_model")


