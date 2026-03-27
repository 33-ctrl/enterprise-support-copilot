from support_core import (
    get_order_status,
    get_refund_eligibility,
    create_support_ticket,
    retrieve_knowledge,
)

TOOLS_REGISTRY = {
    "retrieve_knowledge": {
        "description": "检索订单、退款、故障排查等知识内容",
        "handler": retrieve_knowledge,
    },
    "get_order_status": {
        "description": "查询订单当前状态",
        "handler": get_order_status,
    },
    "get_refund_eligibility": {
        "description": "判断订单当前是否适合申请退款",
        "handler": get_refund_eligibility,
    },
    "create_support_ticket": {
        "description": "创建人工跟进工单",
        "handler": create_support_ticket,
    },
}