import json
from typing import Any, Dict

from mcp_tools.registry import TOOLS_REGISTRY
from mcp_resources.registry import RESOURCES_REGISTRY
from mcp_prompts.templates import PROMPTS_REGISTRY


class MCPServerPrototype:
    """
    一个面向当前项目的 MCP server 原型。
    目标：
    - 提供 tools / resources / prompts 三类能力
    - 为后续演进成真正的 MCP server 做结构准备
    """

    def list_tools(self):
        results = []
        for _, tool in TOOLS_REGISTRY.items():
            results.append({
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["input_schema"],
            })
        return results

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        if tool_name not in TOOLS_REGISTRY:
            return {"error": f"未知工具：{tool_name}"}

        tool = TOOLS_REGISTRY[tool_name]
        handler = tool["handler"]

        try:
            result = handler(**arguments)
            return {
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result
            }
        except TypeError as e:
            return {
                "error": f"工具参数不匹配：{str(e)}"
            }
        except Exception as e:
            return {
                "error": f"工具调用失败：{str(e)}"
            }

    def list_resources(self):
        results = []
        for _, resource in RESOURCES_REGISTRY.items():
            results.append({
                "uri": resource["uri"],
                "title": resource["title"],
                "description": resource["description"],
            })
        return results

    def read_resource(self, uri: str):
        if uri not in RESOURCES_REGISTRY:
            return {"error": f"未知资源：{uri}"}

        resource = RESOURCES_REGISTRY[uri]
        path = resource["path"]

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "uri": resource["uri"],
                "title": resource["title"],
                "description": resource["description"],
                "content": content
            }
        except Exception as e:
            return {"error": f"读取资源失败：{str(e)}"}

    def list_prompts(self):
        results = []
        for _, prompt in PROMPTS_REGISTRY.items():
            results.append({
                "name": prompt["name"],
                "title": prompt["title"],
                "description": prompt["description"],
            })
        return results

    def get_prompt(self, prompt_name: str, variables: Dict[str, Any]):
        if prompt_name not in PROMPTS_REGISTRY:
            return {"error": f"未知提示模板：{prompt_name}"}

        prompt = PROMPTS_REGISTRY[prompt_name]
        template = prompt["template"]

        try:
            rendered = template.format(**variables)
            return {
                "name": prompt["name"],
                "title": prompt["title"],
                "description": prompt["description"],
                "rendered_prompt": rendered
            }
        except KeyError as e:
            return {
                "error": f"缺少模板变量：{str(e)}"
            }

    def debug_dump(self):
        return {
            "tools": self.list_tools(),
            "resources": self.list_resources(),
            "prompts": self.list_prompts(),
        }


if __name__ == "__main__":
    server = MCPServerPrototype()

    print("=== TOOLS ===")
    print(json.dumps(server.list_tools(), ensure_ascii=False, indent=2))

    print("\n=== RESOURCES ===")
    print(json.dumps(server.list_resources(), ensure_ascii=False, indent=2))

    print("\n=== PROMPTS ===")
    print(json.dumps(server.list_prompts(), ensure_ascii=False, indent=2))

    print("\n=== CALL TOOL DEMO ===")
    demo_tool_result = server.call_tool(
        "get_order_status",
        {"order_id": "A12345"}
    )
    print(json.dumps(demo_tool_result, ensure_ascii=False, indent=2))

    print("\n=== READ RESOURCE DEMO ===")
    demo_resource_result = server.read_resource("kb://faq/order")
    print(json.dumps(demo_resource_result, ensure_ascii=False, indent=2))

    print("\n=== RENDER PROMPT DEMO ===")
    demo_prompt_result = server.get_prompt(
        "planner",
        {
            "user_query": "订单 A12345 为什么还没发货？",
            "order_id": "A12345",
            "customer_id": "UNKNOWN"
        }
    )
    print(json.dumps(demo_prompt_result, ensure_ascii=False, indent=2))