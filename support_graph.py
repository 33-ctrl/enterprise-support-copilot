import json
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

from openai import OpenAI
from langgraph.graph import StateGraph, START, END

from support_core import (
    retrieve_knowledge,
    get_order_status,
    get_refund_eligibility,
    create_support_ticket,
    extract_order_id,
    extract_customer_id,
)


class SupportState(TypedDict):
    user_query: str
    chat_history: List[Dict[str, str]]
    plan: Dict[str, Any]
    order_id: Optional[str]
    customer_id: Optional[str]
    retrieved_docs: List[Dict[str, Any]]
    order_result: Dict[str, Any] | str
    refund_result: Dict[str, Any] | str
    approval_required: bool
    proposed_ticket: Dict[str, Any] | None
    executed_ticket: Dict[str, Any] | None
    final_answer: str


def build_graph(client: OpenAI, model_name: str = "glm-4-air"):
    def planner_node(state: SupportState):
        user_query = state["user_query"]
        order_id = extract_order_id(user_query)
        customer_id = extract_customer_id(user_query)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "retrieve_knowledge",
                    "description": "从知识库中检索与订单、退款、故障排查、规则说明相关的内容。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "用户问题或适合检索的查询语句",
                            }
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order_status",
                    "description": "查询某个订单的当前状态，包括支付情况、发货进度和库存情况。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "订单号，例如 A12345",
                            }
                        },
                        "required": ["order_id"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_refund_eligibility",
                    "description": "判断某个订单当前是否适合申请退款。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "订单号，例如 A12345",
                            }
                        },
                        "required": ["order_id"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "propose_ticket_creation",
                    "description": "当问题需要人工介入时，拟定工单内容，但此步骤不会直接创建工单。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "客户编号，例如 C10001；如果未知可填 UNKNOWN",
                            },
                        },
                        "required": ["title", "description", "priority", "customer_id"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
        ]

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个任务规划器。"
                        "请根据用户问题决定需要调用哪些工具。"
                        "如果需要人工介入，可以调用 propose_ticket_creation。"
                        "不要直接回答用户问题。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"用户问题：{user_query}\n"
                        f"已识别的订单号：{order_id}\n"
                        f"已识别的客户编号：{customer_id}\n"
                        "请根据需要选择工具。"
                    ),
                },
            ],
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
        )

        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None) or []

        plan = {
            "need_retrieval": False,
            "need_order_tool": False,
            "need_refund_tool": False,
            "need_ticket_creation": False,
            "reason": "已按工具调用结果生成计划。",
        }

        proposed_ticket = None

        for tc in tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)

            if name == "retrieve_knowledge":
                plan["need_retrieval"] = True

            elif name == "get_order_status":
                plan["need_order_tool"] = True
                if not order_id:
                    order_id = args.get("order_id")

            elif name == "get_refund_eligibility":
                plan["need_refund_tool"] = True
                if not order_id:
                    order_id = args.get("order_id")

            elif name == "propose_ticket_creation":
                plan["need_ticket_creation"] = True
                proposed_ticket = {
                    "title": args["title"],
                    "description": args["description"],
                    "priority": args["priority"],
                    "customer_id": args["customer_id"],
                }

        approval_required = bool(plan["need_ticket_creation"])

        return {
            "plan": plan,
            "order_id": order_id,
            "customer_id": customer_id,
            "approval_required": approval_required,
            "proposed_ticket": proposed_ticket,
        }

    def retrieve_node(state: SupportState):
        if not state["plan"].get("need_retrieval", False):
            return {"retrieved_docs": []}

        docs = retrieve_knowledge(state["user_query"], top_k=3)
        return {"retrieved_docs": docs}

    def tool_node(state: SupportState):
        order_result: Dict[str, Any] | str = "未调用订单相关查询"
        refund_result: Dict[str, Any] | str = "未调用退款判断"

        if state["plan"].get("need_order_tool") and state.get("order_id"):
            order_result = get_order_status(state["order_id"])

        if state["plan"].get("need_refund_tool") and state.get("order_id"):
            refund_result = get_refund_eligibility(state["order_id"])

        return {
            "order_result": order_result,
            "refund_result": refund_result,
        }

    def draft_node(state: SupportState):
        docs_text = "\n\n".join(
            [f"[来源: {d['source']}] {d['text']}" for d in state.get("retrieved_docs", [])]
        )

        proposed_ticket = state.get("proposed_ticket")
        executed_ticket = state.get("executed_ticket")

        prompt = f"""
你是一名可靠、克制、温和的智能助理。

用户问题：
{state["user_query"]}

系统收集到的信息：
- 知识参考：{docs_text if docs_text else "暂无相关知识参考"}
- 订单信息：{state.get("order_result", "未查询")}
- 退款判断：{state.get("refund_result", "未查询")}
- 是否需要人工确认：{"需要" if state.get("approval_required") else "暂不需要"}
- 待确认事项：{proposed_ticket}
- 已完成事项：{executed_ticket}

请输出一段自然、简洁、专业的中文回复：
1. 先直接回应用户最关心的问题
2. 如果有依据，简要说明依据
3. 如果适合，告诉用户下一步可以怎么做
4. 如果存在待确认事项，不要说已经完成，只提示用户确认
5. 如果已经完成了某项操作，要明确告诉用户结果
6. 禁止出现以下字样：graph、agent、节点、项目、tool call、function calling
7. 避免直接暴露程序字段名
"""

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一个真实产品中的智能助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        return {"final_answer": response.choices[0].message.content}

    graph = StateGraph(SupportState)
    graph.add_node("planner_node", planner_node)
    graph.add_node("retrieve_node", retrieve_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("draft_node", draft_node)

    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "retrieve_node")
    graph.add_edge("retrieve_node", "tool_node")
    graph.add_edge("tool_node", "draft_node")
    graph.add_edge("draft_node", END)

    return graph.compile()


def execute_ticket_after_approval(proposed_ticket: Dict[str, Any]):
    if not proposed_ticket:
        return None

    return create_support_ticket(
        title=proposed_ticket["title"],
        description=proposed_ticket["description"],
        priority=proposed_ticket["priority"],
        customer_id=proposed_ticket["customer_id"],
    )