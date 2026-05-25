from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langsmith import traceable

from src.tools.sql_db_schema import SqlDbSchemaTool
from src.tools.sql_db_query import SqlDbQueryTool
from src.tools.sql_db_checker import SqlDbCheckerTool
from src.prompts.sql_prompts import get_financial_analysis_prompt

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    id: int

class FinancialAgent:
    def __init__(self):
        self.tools = [SqlDbSchemaTool(), SqlDbCheckerTool(), SqlDbQueryTool()]
        self.model = ChatAnthropic(
            model="claude-sonnet-4-6",
            max_retries=10,
        ).bind_tools(self.tools)
        self.app = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        
        @traceable(name="agent_call", tags=["node:agent"])
        def model_call(state: AgentState):
            system_prompt = SystemMessage(
                content=get_financial_analysis_prompt(state["id"])
            )
            response = self.model.invoke([system_prompt] + state["messages"])
            return {"messages": [response]}
        
        @traceable(name="should_continue", tags=["node:conditional"])
        def should_continue(state: AgentState):
            last_message = state["messages"][-1]
            if not last_message.tool_calls:
                return "end"
            return "continue"

        graph.add_node("agent", model_call)
        
        tool_node = ToolNode(tools=self.tools)
        graph.add_node("tools", tool_node)
        
        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
        graph.add_edge("tools", "agent")
        
        return graph.compile()

    @traceable(name="analyze_financials", tags=["workflow:financial_analysis"])
    async def analyze(self, id: int) -> str:
        prompt = f"Please perform a complete cash flow and spending analysis for the user with id {id}."
        inputs = {"messages": [("user", prompt)], "id": id}
        
        final_state = None
        # Use stream to process internally
        async for s in self.app.astream(inputs, stream_mode="values"):
            final_state = s
            
        return final_state["messages"][-1].content
