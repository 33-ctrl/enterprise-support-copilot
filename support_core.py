import json
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========= 加载知识库 =========
faq_order_text = load_text_file("data/faq_order.txt")
refund_policy_text = load_text_file("data/refund_policy.txt")
incident_playbook_text = load_text_file("data/incident_playbook.txt")

raw_docs = [
    {"source": "订单常见问题", "text": faq_order_text},
    {"source": "退款规则说明", "text": refund_policy_text},
    {"source": "异常排查手册", "text": incident_playbook_text},
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=120,
    chunk_overlap=20,
)

chunks: List[Dict[str, str]] = []
for doc in raw_docs:
    split_texts = splitter.split_text(doc["text"])
    for chunk in split_texts:
        chunks.append({
            "source": doc["source"],
            "text": chunk,
        })

chunk_texts = [c["text"] for c in chunks]
vectorizer = TfidfVectorizer()
chunk_vectors = vectorizer.fit_transform(chunk_texts)


def retrieve_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, chunk_vectors)[0]
    ranked_indices = scores.argsort()[::-1][:top_k]

    results: List[Dict[str, Any]] = []
    for idx in ranked_indices:
        results.append({
            "source": chunks[idx]["source"],
            "text": chunks[idx]["text"],
            "score": float(scores[idx]),
        })
    return results


# ========= 模拟数据 =========
ORDERS_PATH = "data/mock_orders.json"
TICKETS_PATH = "data/mock_tickets.json"

mock_orders = load_json_file(ORDERS_PATH)
mock_tickets = load_json_file(TICKETS_PATH)


def get_order_status(order_id: str) -> Dict[str, Any]:
    for order in mock_orders:
        if order["order_id"] == order_id:
            shipment_map = {
                "pending": "暂未发货",
                "shipped": "已发货",
            }
            payment_map = {
                "paid": "已支付",
                "unpaid": "未支付",
            }
            inventory_map = {
                "in_stock": "库存充足",
                "out_of_stock": "暂时缺货",
            }

            return {
                "订单号": order["order_id"],
                "客户编号": order["customer_id"],
                "支付状态": payment_map.get(order["payment_status"], order["payment_status"]),
                "发货进度": shipment_map.get(order["shipment_status"], order["shipment_status"]),
                "库存情况": inventory_map.get(order["inventory_status"], order["inventory_status"]),
            }

    return {"错误": f"没有找到订单 {order_id}"}


def get_refund_eligibility(order_id: str) -> Dict[str, Any]:
    for order in mock_orders:
        if order["order_id"] == order_id:
            return {
                "订单号": order_id,
                "当前是否适合申请退款": "可以" if order["refund_eligible"] else "暂不建议",
                "说明": "该判断基于当前订单状态的模拟规则，仅供演示。",
            }

    return {"错误": f"没有找到订单 {order_id}"}


def search_ticket_history(customer_id: str):
    results = []
    for ticket in mock_tickets:
        if ticket["customer_id"] == customer_id:
            results.append(ticket)

    if results:
        return results
    return {"提示": f"客户 {customer_id} 暂无历史工单"}


def create_support_ticket(
    title: str,
    description: str,
    priority: str,
    customer_id: str = "UNKNOWN",
) -> Dict[str, Any]:
    global mock_tickets

    next_id_number = 9000 + len(mock_tickets) + 1
    new_ticket = {
        "ticket_id": f"T{next_id_number}",
        "customer_id": customer_id,
        "title": title,
        "priority": priority,
        "status": "open",
        "description": description,
    }

    mock_tickets.append(new_ticket)
    save_json_file(TICKETS_PATH, mock_tickets)
    return new_ticket


def extract_order_id(text: str):
    words = text.replace("，", " ").replace("。", " ").split()
    for word in words:
        cleaned = word.strip(" ,.!?？、；;：:")
        if cleaned.startswith("A") and len(cleaned) >= 5:
            return cleaned
    return None


def extract_customer_id(text: str):
    words = text.replace("，", " ").replace("。", " ").split()
    for word in words:
        cleaned = word.strip(" ,.!?？、；;：:")
        if cleaned.startswith("C") and len(cleaned) >= 5:
            return cleaned
    return None