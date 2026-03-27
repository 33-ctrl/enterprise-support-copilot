import os
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

from support_graph import build_graph, execute_ticket_after_approval

# ========= 环境变量 =========
load_dotenv()
api_key = os.getenv("ZAI_API_KEY")

if not api_key:
    raise ValueError("没有读取到 ZAI_API_KEY，请检查 .env 文件。")

# ========= 大模型客户端 =========
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

graph = build_graph(client, model_name="glm-4-air")

# ========= 页面配置 =========
st.set_page_config(
    page_title="智能助理",
    page_icon="💬",
    layout="wide"
)

# ========= 样式 =========
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(245,247,250,0.9) 0%, rgba(255,255,255,1) 35%),
        linear-gradient(180deg, #ffffff 0%, #fcfcfd 100%);
    color: #161616;
}

.block-container {
    max-width: 980px;
    padding-top: 1.15rem;
    padding-bottom: 2rem;
}

/* 顶部欢迎区 */
.hero-wrap {
    position: relative;
    overflow: hidden;
    background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
    border: 1px solid #efefef;
    border-radius: 26px;
    padding: 26px 24px 20px 24px;
    box-shadow: 0 14px 40px rgba(0,0,0,0.04);
    margin-bottom: 18px;
}

.hero-wrap::after {
    content: "";
    position: absolute;
    right: -40px;
    top: -40px;
    width: 180px;
    height: 180px;
    background: radial-gradient(circle, rgba(240,240,245,0.9) 0%, rgba(255,255,255,0) 70%);
    border-radius: 999px;
}

.hero-topline {
    display: inline-block;
    font-size: 0.82rem;
    color: #666;
    background: #f5f5f5;
    border: 1px solid #ececec;
    padding: 6px 10px;
    border-radius: 999px;
    margin-bottom: 12px;
}

.main-title {
    font-size: 2.18rem;
    font-weight: 760;
    letter-spacing: -0.02em;
    margin-bottom: 0.35rem;
    color: #111111;
}

.sub-title {
    color: #5f6368;
    line-height: 1.75;
    font-size: 1rem;
    max-width: 760px;
    margin-bottom: 0.4rem;
}

.mini-meta {
    color: #8a8a8a;
    font-size: 0.9rem;
    margin-top: 10px;
}

/* 快捷卡片 */
.quick-wrap {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}

.quick-card {
    border: 1px solid #ececec;
    border-radius: 18px;
    padding: 14px 16px;
    background: rgba(255,255,255,0.85);
    box-shadow: 0 8px 22px rgba(0,0,0,0.03);
}

.quick-card-title {
    font-size: 0.95rem;
    font-weight: 650;
    margin-bottom: 6px;
    color: #141414;
}

.quick-card-desc {
    font-size: 0.9rem;
    line-height: 1.7;
    color: #666;
}

/* 空状态 */
.empty-wrap {
    border: 1px dashed #e6e6e6;
    border-radius: 22px;
    padding: 26px 20px;
    background: rgba(255,255,255,0.8);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
    margin-top: 10px;
    margin-bottom: 18px;
    text-align: center;
}

.empty-icon {
    font-size: 2.2rem;
    margin-bottom: 6px;
}

.empty-title {
    font-size: 1.05rem;
    font-weight: 650;
    color: #222;
    margin-bottom: 6px;
}

.empty-desc {
    color: #7a7a7a;
    font-size: 0.94rem;
    line-height: 1.8;
}

/* 聊天气泡 */
div[data-testid="stChatMessage"] {
    border-radius: 20px;
    margin-bottom: 10px;
}

div[data-testid="stChatMessageContent"] {
    border-radius: 20px;
    padding-top: 4px;
    line-height: 1.8;
    font-size: 0.98rem;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    line-height: 1.8;
}

.message-time {
    color: #9a9a9a;
    font-size: 0.78rem;
    margin-top: 4px;
}

/* 按钮 */
.stButton > button {
    border-radius: 14px;
    border: 1px solid #e8e8e8;
    background: #ffffff;
    color: #111111;
    min-height: 44px;
    font-weight: 550;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #d9d9d9;
    background: #fafafa;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}

/* 输入框 */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.96);
}

/* 侧边栏 */
section[data-testid="stSidebar"] {
    background: #fcfcfc;
    border-left: 1px solid #efefef;
}

/* 柔和信息块 */
.soft-box {
    border: 1px solid #ececec;
    background: #ffffff;
    border-radius: 18px;
    padding: 14px 16px;
    margin-top: 10px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.025);
}

.small-note {
    color: #6a6a6a;
    font-size: 0.92rem;
    line-height: 1.75;
}

.status-pill {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    background: #f6f6f6;
    border: 1px solid #ececec;
    color: #666;
    font-size: 0.8rem;
    margin-right: 6px;
    margin-bottom: 6px;
}

[data-testid="stStatusWidget"] {
    border-radius: 16px;
}

hr {
    border: none;
    border-top: 1px solid #f0f0f0;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ========= Session State =========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好，我在这里。你可以把情况直接发给我，我会先帮你梳理重点，再看看能不能继续往下处理。",
            "time": datetime.now().strftime("%H:%M")
        }
    ]

if "last_graph_result" not in st.session_state:
    st.session_state.last_graph_result = None

if "pending_ticket" not in st.session_state:
    st.session_state.pending_ticket = None

if "tool_traces" not in st.session_state:
    st.session_state.tool_traces = []

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None


# ========= 工具函数 =========
def now_time() -> str:
    return datetime.now().strftime("%H:%M")


def export_chat_as_text(messages):
    lines = []
    for msg in messages:
        role = "用户" if msg["role"] == "user" else "助理"
        msg_time = msg.get("time", "")
        prefix = f"[{msg_time}] " if msg_time else ""
        lines.append(f"{prefix}{role}：{msg['content']}")
    return "\n\n".join(lines)


def append_message(role: str, content: str):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "time": now_time()
    })


def render_message(msg: dict):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("time"):
            st.markdown(
                f'<div class="message-time">{msg["time"]}</div>',
                unsafe_allow_html=True
            )


def handle_user_prompt(user_prompt: str):
    append_message("user", user_prompt)
    render_message(st.session_state.messages[-1])

    chat_history_for_graph = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    with st.chat_message("assistant"):
        with st.status("正在整理信息...", expanded=False) as status:
            result = graph.invoke({
                "user_query": user_prompt,
                "chat_history": chat_history_for_graph,
                "plan": {},
                "order_id": None,
                "customer_id": None,
                "retrieved_docs": [],
                "order_result": "未调用",
                "refund_result": "未调用",
                "approval_required": False,
                "proposed_ticket": None,
                "executed_ticket": None,
                "final_answer": ""
            })
            status.update(label="已整理完成", state="complete")

        st.markdown(result["final_answer"])
        st.markdown(
            f'<div class="message-time">{now_time()}</div>',
            unsafe_allow_html=True
        )

    append_message("assistant", result["final_answer"])

    st.session_state.last_graph_result = result
    st.session_state.pending_ticket = result.get("proposed_ticket") if result.get("approval_required") else None

    st.session_state.tool_traces.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "query": user_prompt,
        "plan": result.get("plan"),
        "retrieved_docs": result.get("retrieved_docs"),
        "order_result": result.get("order_result"),
        "refund_result": result.get("refund_result")
    })


# ========= 顶部欢迎区 =========
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-topline">在线协助 · 查询 · 解释 · 整理建议</div>
        <div class="main-title">智能助理</div>
        <div class="sub-title">
            我可以帮你查询进度、解释规则、分析问题，也可以把下一步建议整理得更清楚一点。
            你只需要把情况发给我，我会先帮你把线索理顺。
        </div>
        <div class="mini-meta">适合处理：订单问题、规则说明、退款判断、异常排查、人工跟进建议</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ========= 快捷说明区 =========
st.markdown(
    """
    <div class="quick-wrap">
        <div class="quick-card">
            <div class="quick-card-title">订单进度</div>
            <div class="quick-card-desc">例如：订单 A12345 为什么还没有发货？</div>
        </div>
        <div class="quick-card">
            <div class="quick-card-title">退款判断</div>
            <div class="quick-card-desc">例如：订单 A11111 现在适合申请退款吗？</div>
        </div>
        <div class="quick-card">
            <div class="quick-card-title">异常排查</div>
            <div class="quick-card-desc">例如：用户反馈接口报 502，通常先看什么？</div>
        </div>
        <div class="quick-card">
            <div class="quick-card-title">人工跟进</div>
            <div class="quick-card-desc">例如：这件事如果需要人工继续跟进，麻烦帮我整理一下。</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ========= 快捷按钮 =========
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("查订单进度", use_container_width=True):
        st.session_state.suggested_prompt = "订单 A12345 为什么还没有发货？"
with c2:
    if st.button("看退款条件", use_container_width=True):
        st.session_state.suggested_prompt = "订单 A11111 现在适合申请退款吗？"
with c3:
    if st.button("排查报错", use_container_width=True):
        st.session_state.suggested_prompt = "用户反馈接口报 502，通常应该先看什么？"
with c4:
    if st.button("整理跟进建议", use_container_width=True):
        st.session_state.suggested_prompt = "这件事如果需要人工继续跟进，麻烦帮我整理一下。"

# ========= 空状态 / 消息区 =========
if len(st.session_state.messages) <= 1:
    st.markdown(
        """
        <div class="empty-wrap">
            <div class="empty-icon">✦</div>
            <div class="empty-title">现在还没有新的对话</div>
            <div class="empty-desc">
                你可以直接输入问题，也可以用上面的快捷入口开始。<br>
                如果问题里带上订单号或客户编号，通常会更容易快速定位。
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

for msg in st.session_state.messages:
    render_message(msg)

# ========= 快捷按钮触发 =========
if st.session_state.suggested_prompt:
    prompt = st.session_state.suggested_prompt
    st.session_state.suggested_prompt = None
    handle_user_prompt(prompt)

# ========= 用户输入 =========
user_prompt = st.chat_input("请输入你的问题")

if user_prompt:
    handle_user_prompt(user_prompt)

# ========= 待确认事项 =========
if st.session_state.pending_ticket:
    st.divider()
    st.markdown("### 还需要你确认一下")
    st.info("从目前的情况看，这件事可能需要人工继续跟进。要不要现在帮你提交？")

    with st.expander("查看准备提交的内容", expanded=True):
        st.json(st.session_state.pending_ticket)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("确认提交", use_container_width=True):
            created_ticket = execute_ticket_after_approval(st.session_state.pending_ticket)
            confirm_msg = f"已经帮你提交好了，后续可以按工单 **{created_ticket['ticket_id']}** 继续跟进。"
            append_message("assistant", confirm_msg)
            st.session_state.pending_ticket = None
            st.rerun()

    with col2:
        if st.button("先不提交", use_container_width=True):
            append_message("assistant", "好的，那我先不帮你提交。如果你愿意，我也可以继续帮你把处理建议整理得更细一点。")
            st.session_state.pending_ticket = None
            st.rerun()

# ========= 侧边栏 =========
with st.sidebar:
    st.markdown("## 当前会话")

    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "你好，我在这里。你可以把情况直接发给我，我会先帮你梳理重点，再看看能不能继续往下处理。",
                "time": now_time()
            }
        ]
        st.session_state.last_graph_result = None
        st.session_state.pending_ticket = None
        st.session_state.tool_traces = []
        st.session_state.suggested_prompt = None
        st.rerun()

    chat_export = export_chat_as_text(st.session_state.messages)
    st.download_button(
        label="导出对话",
        data=chat_export,
        file_name="chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("## 当前状态")

    if st.session_state.last_graph_result:
        result = st.session_state.last_graph_result
        pills = []

        if result.get("retrieved_docs"):
            pills.append("已参考说明")
        if isinstance(result.get("order_result"), dict) and "错误" not in result.get("order_result", {}):
            pills.append("已查看进度")
        if isinstance(result.get("refund_result"), dict) and "错误" not in result.get("refund_result", {}):
            pills.append("已判断条件")
        if result.get("approval_required"):
            pills.append("待你确认")

        if pills:
            st.markdown(
                "".join([f'<span class="status-pill">{p}</span>' for p in pills]),
                unsafe_allow_html=True
            )
        else:
            st.caption("当前还没有可展示的状态。")
    else:
        st.caption("当前还没有处理结果。")

    st.markdown("---")
    st.markdown("## 最近处理")

    if st.session_state.tool_traces:
        latest = st.session_state.tool_traces[-1]

        st.markdown(
            f"""
            <div class="soft-box">
                <div><strong>最近一次时间</strong></div>
                <div class="small-note">{latest["time"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("查看详细信息", expanded=False):
            st.write("处理规划：")
            st.json(latest["plan"])

            st.write("知识参考：")
            st.write(latest["retrieved_docs"])

            st.write("订单信息：")
            st.json(latest["order_result"])

            st.write("退款判断：")
            st.json(latest["refund_result"])
    else:
        st.caption("现在还没有处理记录。")

    st.markdown("---")
    st.markdown("## 使用建议")
    st.caption("如果你能提供订单号、客户编号或更具体的现象，通常会更容易得到清晰结论。")