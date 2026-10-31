from app.services.llm_service import ToolDefinition


SEARCH_PRODUCTS_TOOL = ToolDefinition(
    name="search_products",
    description=(
        "Retrieve or search products from the OrderFlow product catalog. "
        "Use this tool whenever the user asks about available products, "
        "product prices, SKUs, product IDs, or searches for a product. "
        "If the user asks for all available products, use an empty query."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Product name, SKU, product ID, or description. "
                    "Use an empty string to retrieve all products."
                ),
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
)


GET_ORDER_TOOL = ToolDefinition(
    name="get_order",
    description=(
        "Retrieve an OrderFlow order by its order ID. "
        "Use this whenever the user asks about a specific existing order."
    ),
    parameters={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The UUID of the order.",
            }
        },
        "required": ["order_id"],
        "additionalProperties": False,
    },
)


PREPARE_ORDER_TOOL = ToolDefinition(
    name="prepare_order",
    description=(
        "Prepare an OrderFlow order draft when the user actually wants "
        "to create or place an order. "
        "Do NOT use this tool when the user is merely asking how to create "
        "an order or requesting instructions/examples. "
        "Products may be identified by product name, SKU, or product ID. "
        "Multiple products may be included. "
        "This tool NEVER submits the order; explicit confirmation is required."
    ),
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID for the order.",
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_query": {
                            "type": "string",
                            "description": (
                                "Product ID, SKU, product name, or other "
                                "product text supplied by the user."
                            ),
                        },
                        "quantity": {
                            "type": "integer",
                            "minimum": 1,
                        },
                    },
                    "required": [
                        "product_query",
                        "quantity",
                    ],
                    "additionalProperties": False,
                },
                "minItems": 1,
            },
        },
        "required": [
            "customer_id",
            "items",
        ],
        "additionalProperties": False,
    },
)


CONFIRM_ORDER_TOOL = ToolDefinition(
    name="confirm_order",
    description=(
        "Submit the existing pending OrderFlow order draft. "
        "ONLY use this when the user clearly confirms that the pending "
        "order should be created. The existing validated draft is used; "
        "this tool accepts no order details."
    ),
    parameters={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)

SEARCH_KNOWLEDGE_TOOL = ToolDefinition(
    name="search_knowledge",
    description=(
        "Search the official OrderFlow knowledge base. "
        "Use this for questions about OrderFlow architecture, "
        "features, order processing, AI behavior, order creation "
        "instructions, supported capabilities, and project documentation. "
        "Use this instead of relying on general model knowledge when "
        "the question is specifically about OrderFlow."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The user's OrderFlow documentation question."
                ),
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
)

BASE_OMS_TOOLS = [
    SEARCH_PRODUCTS_TOOL,
    GET_ORDER_TOOL,
    PREPARE_ORDER_TOOL,
    SEARCH_KNOWLEDGE_TOOL,
]