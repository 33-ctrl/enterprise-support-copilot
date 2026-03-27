import os
import json
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

# ========= 读取环境变量 =========
load_dotenv()
api_key = os.getenv("ZAI_API_KEY")

if not api_key:
    raise ValueError("没有读取到 ZAI_API_KEY，请检查 .env 文件。")

# ========= 创建客户端 =========
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

MODEL_NAME = "glm-4-air"

# ========= 页面设置 =========
st.set_page_config(page_title="Enterprise Support Copilot", page_icon="🛠️")
st.title("🛠️ Enterprise Support Copilot")
st.write("输入一个订单、退款或故障相关问题，系统会结合知识库和本地工具数据生成答案。")

# ========= 读取知识库 =========
def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

faq_order_text = load_text_file("data/faq_order.txt")
refund_policy_text = load_text_file("data/refund_policy.txt")
incident_playbook_text = load_text_file("data/incident_playbook.txt")

knowledge_base = {
    "订单": faq_order_text,
    "发货": faq_order_text,
    "退款": refund_policy_text,
    "故障": incident_playbook_text,
    "502": incident_playbook_text,
    "报错": incident_playbook_text,
    "API": incident_playbook_text
}

# ========= 读取模拟数据 =========
def load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

mock_orders = load_json_file("data/mock_orders.json")
mock_tickets = load_json_file("data/mock_tickets.json")

# ========= 工具函数 =========
def get_order_status(order_id: str):
    for order in mock_orders:
        if order["order_id"] == order_id:
            return order
    return {"error": f"没有找到订单 {order_id}"}

def get_refund_eligibility(order_id: str):
    for order in mock_orders:
        if order["order_id"] == order_id:
            return {
                "order_id": order_id,
                "refund_eligible": order["refund_eligible"]
            }
    return {"error": f"没有找到订单 {order_id}"}

def search_ticket_history(customer_id: str):
    results = []
    for ticket in mock_tickets:
        if ticket["customer_id"] == customer_id:
            results.append(ticket)
    if results:
        return results
    return {"message": f"客户 {customer_id} 没有历史工单"}

# ========= 简单检索函数（RAG 雏形） =========
def retrieve_knowledge(query: str) -> str:
    matched_docs = []

    for keyword, content in knowledge_base.items():
        if keyword.lower() in query.lower():
            matched_docs.append(content)

    if not matched_docs:
        return "未命中知识库内容。"

    # 去重后拼接
    unique_docs = list(set(matched_docs))
    return "\n\n".join(unique_docs)

# ========= 提取订单号（超简化版） =========
def extract_order_id(text: str):
    words = text.replace("，", " ").replace("。", " ").split()
    for word in words:
        if word.startswith("A") and len(word) >= 5:
            return word.strip(" ,.!?")
    return None

# ========= 路由逻辑（超简化版） =========
def decide_actions(user_query: str):
    actions = {
        "need_knowledge": False,
        "need_order_tool": False,
        "need_refund_tool": False
    }

    if any(k in user_query for k in ["退款", "规则", "发货", "订单", "报错", "502", "故障"]):
        actions["need_knowledge"] = True

    if "订单" in user_query or extract_order_id(user_query):
        actions["need_order_tool"] = True

    if "退款" in user_query:
        actions["need_refund_tool"] = True

    return actions

# ========= 统一模型调用 =========
def generate_answer(user_query: str, knowledge: str, order_info, refund_info):
    prompt = f"""
你是一名企业支持 Copilot，请根据以下信息回答用户问题。

用户问题：
{user_query}

知识库检索结果：
{knowledge}

订单工具查询结果：
{order_info}

退款工具查询结果：
{refund_info}

请按以下结构输出：
1. 问题判断
2. 证据来源
3. 处理建议
4. 给用户的回复草稿

要求：
- 用中文
- 如果没有查到数据，要明确说明
- 不要编造系统里没有的信息
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "你是一名谨慎、专业的企业支持智能助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

# ========= 页面输入 =========
user_query = st.text_area(
    "请输入问题：",
    height=150,
    placeholder="例如：订单 A12345 为什么还没发货？如果还没发货，能不能退款？"
)

if st.button("开始分析"):
    if not user_query.strip():
        st.warning("请先输入问题。")
        st.stop()

    actions = decide_actions(user_query)

    knowledge_result = "未检索知识库。"
    order_result = "未调用订单工具。"
    refund_result = "未调用退款工具。"

    order_id = extract_order_id(user_query)

    if actions["need_knowledge"]:
        knowledge_result = retrieve_knowledge(user_query)

    if actions["need_order_tool"] and order_id:
        order_result = get_order_status(order_id)

    if actions["need_refund_tool"] and order_id:
        refund_result = get_refund_eligibility(order_id)

    with st.spinner("正在生成分析结果..."):
        final_answer = generate_answer(
            user_query=user_query,
            knowledge=knowledge_result,
            order_info=order_result,
            refund_info=refund_result
        )

    tab1, tab2, tab3 = st.tabs(["最终回答", "知识库结果", "工具结果"])

    with tab1:
        st.markdown(final_answer)

    with tab2:
        st.text(knowledge_result)

    with tab3:
        st.write("订单工具结果：")
        st.json(order_result)
        st.write("退款工具结果：")
        st.json(refund_result)