from langchain_core.messages import RemoveMessage, AIMessage, HumanMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from agent.prompts import PROMPT as TranslationAgentPrompt, EXTRACTION_PROMPT, REWRITE_PROMPT
from agent.state import TranslationState, Term
from agent.tools import milvus_hy_search


async def get_translation_tools():
    return [milvus_hy_search]

async def query_rewrite_node(state:TranslationState):
    llm = ChatDeepSeek(model="deepseek-chat")
    chain = REWRITE_PROMPT | llm
    message = state["origin_query"]
    response = await chain.ainvoke({"request": message, "chat_history":state["messages"]})
    print(f"改写结果:{response}")
    return {"origin_query": response}


async def term_extraction(state:TranslationState):
    llm = ChatDeepSeek(model="deepseek-chat").with_structured_output(Term)
    chain = EXTRACTION_PROMPT | llm
    message = state["origin_query"]
    response = await chain.ainvoke({"request":message})
    return {"term": response.term_list}

async def summary_node(state: TranslationState):
    messages = state["messages"]
    origin = state["origin_query"]
    res = messages[-1].content
    return {"messages":[RemoveMessage(id=REMOVE_ALL_MESSAGES), HumanMessage(content=origin.content), AIMessage(content=res)], "final_result":AIMessage(content=res)}


async def call_model(state:TranslationState):
    tools = await get_translation_tools()
    llm = ChatDeepSeek(model="deepseek-chat").bind_tools(tools)
    chain = TranslationAgentPrompt | llm
    message = state["origin_query"]
    term_list = state["term"]
    term_str = ",".join(term_list)
    response = await chain.ainvoke({"request":message, "chat_history":state["messages"], "term":term_str})
    return {"messages": response}


async def tool_node(state: TranslationState):
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
    message = state["messages"][-1]
    if hasattr(message, 'tool_calls') and message.tool_calls:
        return "tool_node"
    else:
        return "summary_node"


workflow = StateGraph(TranslationState)

workflow.add_node("call_model", call_model)
workflow.add_node("tool_node", tool_node)
workflow.add_node("term_extraction_node", term_extraction)
workflow.add_node("query_rewrite_node", query_rewrite_node)
workflow.add_node("summary_node", summary_node)

workflow.add_edge(START, "query_rewrite_node")
workflow.add_edge("query_rewrite_node", "term_extraction_node")
workflow.add_edge("term_extraction_node", "call_model")
workflow.add_conditional_edges("call_model", should_use_tool, ["summary_node", "tool_node"])
workflow.add_edge("tool_node", "call_model")
workflow.add_edge("summary_node", END)


