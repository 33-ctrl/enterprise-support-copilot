# 智能助理

一个基于 **Python + Streamlit + LangGraph + 多轮工具调用** 构建的智能助理原型。  
它可以帮助用户查询订单进度、解释规则、判断是否适合申请退款、分析异常问题，并在需要时生成待确认的人工跟进事项。

---

## 项目简介

这是一个更贴近 AI Agent / LLM Application 场景的应用原型。  
系统并不是简单地直接回答问题，而是采用了更接近真实业务的处理方式：

- 先理解用户问题
- 再根据需要调用不同工具
- 检索知识内容
- 查询订单信息
- 判断退款条件
- 在必要时生成待确认的人工处理事项
- 最后输出自然、面向用户的回复

当前版本已经具备：

- 多轮工具调用闭环
- 基于知识内容的检索增强回答
- 人工确认后再执行敏感操作
- MCP-ready 的结构化设计（tools / resources / prompts）
- 面向真实用户的前端界面

---

## 核心功能

### 1. 订单查询
支持根据订单号查询当前进度，例如：

- 是否已支付
- 是否已发货
- 当前库存情况

### 2. 退款判断
支持结合订单状态判断当前是否适合申请退款。

### 3. 知识检索
支持从本地知识内容中检索订单规则、退款说明、异常排查手册，并把结果作为回复依据。

### 4. 异常问题分析
支持处理类似“接口报错”“状态异常”“应该如何排查”这类问题。

### 5. 人工跟进建议
当系统判断问题可能需要人工继续处理时，会先生成待确认内容，等待用户确认后再创建工单。

### 6. 对话式交互界面
提供聊天式前端界面，支持：

- 连续提问
- 快捷问题
- 消息时间
- 当前状态摘要
- 导出对话

---

## 技术栈

- Python
- Streamlit
- OpenAI Python SDK（用于兼容智谱接口）
- 智谱 AI OpenAI 兼容接口
- LangGraph
- scikit-learn
- langchain-text-splitters
- python-dotenv

---

## 项目结构

```text
enterprise-support-copilot/
├─ app.py
├─ graph_app.py
├─ support_core.py
├─ support_graph.py
├─ mcp_server.py
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env
├─ data/
│  ├─ faq_order.txt
│  ├─ refund_policy.txt
│  ├─ incident_playbook.txt
│  ├─ mock_orders.json
│  └─ mock_tickets.json
├─ mcp_tools/
│  └─ registry.py
├─ mcp_resources/
│  └─ registry.py
└─ mcp_prompts/
   └─ templates.py
