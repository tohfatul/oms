import json

from openai import OpenAI

from app.core.config import settings
from app.services.llm_service import (
    ConversationMessage,
    LLMService,
    ToolCall,
    ToolDecision,
    ToolDefinition,
    ToolResult,
)
from app.core.capabilities import ORDERFLOW_CAPABILITIES

class OpenAIService(LLMService):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    def chat(
        self,
        message: str,
        history: list[ConversationMessage] | None = None,
    ) -> str:
        response = self.client.responses.create(
            model=settings.openai_model,
            instructions=(
                "You are the AI assistant for OrderFlow. "
                + ORDERFLOW_CAPABILITIES
                + "\nOnly describe capabilities that OrderFlow actually supports."
            ),
            input=self._build_input(
                message,
                history,
            ),
        )

        return response.output_text

    def _build_input(
        self,
        message: str,
        history: list[ConversationMessage] | None,
    ) -> list[dict[str, str]]:
        input_messages = []

        for item in history or []:
            input_messages.append({
                "role": item.role,
                "content": item.content,
            })

        input_messages.append({
            "role": "user",
            "content": message,
        })

        return input_messages

    @property
    def supports_tools(self) -> bool:
        return True

    def decide_with_tools(
        self,
        message: str,
        tools: list[ToolDefinition],
        history: list[ConversationMessage] | None = None,
    ) -> ToolDecision:
        response = self.client.responses.create(
            model=settings.openai_model,
            instructions=(
                "You are the AI assistant for OrderFlow, a cloud-native "
                "order processing application. "

                + ORDERFLOW_CAPABILITIES +

                "\n\nIMPORTANT CAPABILITY RULES: "
                "When the user asks what you can do, describe only capabilities "
                "listed as SUPPORTED above. "
                "Never infer additional capabilities merely because they are common "
                "in other order-management systems. "

                "OrderFlow has its own product catalog and order data. "
                "Never invent products, prices, SKUs, product IDs, orders, "
                "inventory levels, or order statuses. "

                "PRODUCT QUESTIONS: "
                "Whenever the user asks about catalog products, product prices, "
                "SKUs, product IDs, or searches for products, use search_products. "

                "Do not describe catalog products as being 'in stock' or 'available "
                "in inventory'. The product API currently indicates catalog products, "
                "not inventory quantities. "

                "EXISTING ORDERS: "
                "Whenever the user asks about a specific existing order and "
                "provides an order ID, use get_order. "

                "ORDER INSTRUCTIONS: "
                "If the user asks HOW to create an order, asks for an example "
                "order-creation prompt, or asks what information is required, "
                "DO NOT call prepare_order. Explain that they need a customer ID "
                "and one or more products with quantities. Products can be "
                "identified by product name, SKU, or product ID. "
                "Give an example such as: "
                "'Create an order for customer CUST-100 with 2 Business Laptop "
                "and 1 Wireless Mouse.' "

                "ORDER CREATION: "
                "Only use prepare_order when the user actually asks to create, "
                "place, prepare, or submit an order and provides enough information. "
                "Multiple products may be included. "

                "If customer ID, product, or quantity is missing, ask for the "
                "missing information rather than inventing it. "

                "Preparing an order NEVER submits it. After prepare_order succeeds, "
                "summarize the customer, products, quantities, prices, and total. "
                "Clearly state that the order has NOT been submitted and request "
                "explicit confirmation. "

                "If product resolution returns multiple matches, show the choices "
                "and ask the user which product they intended. Never guess. "

                "If confirm_order is available, a validated pending order exists. "
                "Only use confirm_order when the CURRENT message clearly confirms "
                "submission, such as 'confirm', 'place the order', 'submit it', "
                "or 'yes, create it'. "

                "Do not interpret unrelated yes/no statements as confirmation. "
                "Use conversation history to understand follow-up questions."

                "ORDERFLOW KNOWLEDGE: "
                "When the user asks about OrderFlow architecture, features, "
                "order-processing behavior, AI capabilities, order-creation guidance, "
                "technology choices, or how the system works, use search_knowledge. "
                "Base the answer on the retrieved OrderFlow knowledge. "
                "Do not invent OrderFlow-specific details that are not present in "
                "the retrieved knowledge. "

                "When search_knowledge returns sources, answer from those sources and "
                "mention the source document names when useful. "
            ),
            input=self._build_input(
                message,
                history,
            ),
            tools=[
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
                for tool in tools
            ],
        )

        tool_calls: list[ToolCall] = []

        for item in response.output:
            if item.type != "function_call":
                continue

            try:
                arguments = json.loads(item.arguments)
            except json.JSONDecodeError:
                arguments = {}

            tool_calls.append(
                ToolCall(
                    call_id=item.call_id,
                    name=item.name,
                    arguments=arguments,
                )
            )

        return ToolDecision(
            response_id=response.id,
            text=response.output_text,
            tool_calls=tool_calls,
        )

    def complete_with_tool_results(
        self,
        decision: ToolDecision,
        results: list[ToolResult],
        tools: list[ToolDefinition],
    ) -> str:
        response = self.client.responses.create(
            model=settings.openai_model,
            previous_response_id=decision.response_id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": result.call_id,
                    "output": json.dumps(result.output),
                }
                for result in results
            ],
            tools=[
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
                for tool in tools
            ],
        )

        return response.output_text

    