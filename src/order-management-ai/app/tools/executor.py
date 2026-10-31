from difflib import SequenceMatcher
from typing import Any
from uuid import UUID

from app.models.order_draft import (
    DraftOrderItem,
    PendingOrderDraft,
)
from app.services.llm_service import (
    ToolCall,
    ToolResult,
)
from app.tools.oms_api import (
    OmsApiError,
    oms_api_client,
)
from app.rag.retriever import knowledge_retriever

FUZZY_AUTO_MATCH_THRESHOLD = 0.88
FUZZY_SUGGEST_THRESHOLD = 0.65


async def execute_tool(
    tool_call: ToolCall,
    access_token: str,
    pending_order: PendingOrderDraft | None = None,
) -> ToolResult:
    try:
        if tool_call.name == "search_products":
            query = str(
                tool_call.arguments.get("query", "")
            )

            result = await search_products_smart(
                query=query,
                access_token=access_token,
            )

            return ToolResult(
                call_id=tool_call.call_id,
                output=result,
            )

        if tool_call.name == "get_order":
            order_id = str(
                tool_call.arguments.get(
                    "order_id",
                    "",
                )
            )

            result = await oms_api_client.get_order(
                order_id=order_id,
                access_token=access_token,
            )

            if result is None:
                return ToolResult(
                    call_id=tool_call.call_id,
                    output={
                        "found": False,
                        "message": "Order was not found.",
                    },
                )

            return ToolResult(
                call_id=tool_call.call_id,
                output={
                    "found": True,
                    "order": result,
                },
            )

        if tool_call.name == "search_knowledge":
            query = str(
                tool_call.arguments.get(
                    "query",
                    "",
                )
            ).strip()

            if not query:
                return ToolResult(
                    call_id=tool_call.call_id,
                    output={
                        "error": "Knowledge search query is required.",
                    },
                )

            results = knowledge_retriever.search(
                query=query,
                limit=4,
            )

            sources = sorted({
                item.source
                for item in results
            })

            return ToolResult(
                call_id=tool_call.call_id,
                output={
                    "results": [
                        {
                            "source": item.source,
                            "title": item.title,
                            "content": item.content,
                            "similarity": round(
                                item.similarity,
                                4,
                            ),
                        }
                        for item in results
                    ],
                    "sources": sources,
                },
            )
        
        if tool_call.name == "prepare_order":
            return await prepare_order(
                tool_call=tool_call,
                access_token=access_token,
            )

        if tool_call.name == "confirm_order":
            return await confirm_order(
                tool_call=tool_call,
                access_token=access_token,
                pending_order=pending_order,
            )

        return ToolResult(
            call_id=tool_call.call_id,
            output={
                "error": f"Unknown tool: {tool_call.name}",
            },
        )

    except OmsApiError as exc:
        return ToolResult(
            call_id=tool_call.call_id,
            output={
                "error": str(exc),
            },
        )


async def search_products_smart(
    query: str,
    access_token: str,
) -> list[dict[str, Any]]:
    products = await oms_api_client.get_products(
        access_token
    )

    normalized_query = query.strip().lower()

    if not normalized_query:
        return products

    matches = []

    for product in products:
        product_id = str(
            product.get("id", "")
        ).lower()

        sku = str(
            product.get("sku", "")
        ).lower()

        name = str(
            product.get("name", "")
        ).lower()

        description = str(
            product.get("description", "")
        ).lower()

        if normalized_query in {
            product_id,
            sku,
            name,
        }:
            matches.append(product)
            continue

        if (
            normalized_query in sku
            or normalized_query in name
            or normalized_query in description
        ):
            matches.append(product)

    return matches


def is_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def similarity(
    first: str,
    second: str,
) -> float:
    return SequenceMatcher(
        None,
        first.lower(),
        second.lower(),
    ).ratio()


def resolve_product(
    product_query: str,
    products: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized = product_query.strip().lower()

    # 1. Exact Product ID
    if is_uuid(product_query.strip()):
        matches = [
            product
            for product in products
            if str(
                product.get("id", "")
            ).lower() == normalized
        ]

        if len(matches) == 1:
            return {
                "status": "resolved",
                "product": matches[0],
                "match_type": "product_id",
            }

    # 2. Exact SKU
    sku_matches = [
        product
        for product in products
        if str(
            product.get("sku", "")
        ).lower() == normalized
    ]

    if len(sku_matches) == 1:
        return {
            "status": "resolved",
            "product": sku_matches[0],
            "match_type": "sku",
        }

    # 3. Exact name
    name_matches = [
        product
        for product in products
        if str(
            product.get("name", "")
        ).lower() == normalized
    ]

    if len(name_matches) == 1:
        return {
            "status": "resolved",
            "product": name_matches[0],
            "match_type": "exact_name",
        }

    # 4. Partial match
    partial_matches = [
        product
        for product in products
        if (
            normalized
            in str(product.get("name", "")).lower()
            or normalized
            in str(product.get("sku", "")).lower()
        )
    ]

    if len(partial_matches) == 1:
        return {
            "status": "resolved",
            "product": partial_matches[0],
            "match_type": "partial",
        }

    if len(partial_matches) > 1:
        return {
            "status": "ambiguous",
            "matches": partial_matches,
        }

    # 5. Fuzzy matching for typos
    scored_products = []

    for product in products:
        name_score = similarity(
            product_query,
            str(product.get("name", "")),
        )

        sku_score = similarity(
            product_query,
            str(product.get("sku", "")),
        )

        score = max(
            name_score,
            sku_score,
        )

        if score >= FUZZY_SUGGEST_THRESHOLD:
            scored_products.append(
                {
                    "product": product,
                    "score": score,
                }
            )

    scored_products.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if not scored_products:
        return {
            "status": "not_found",
        }

    best = scored_products[0]

    second_score = (
        scored_products[1]["score"]
        if len(scored_products) > 1
        else 0
    )

    # Automatically accept only a very strong,
    # clearly better match.
    if (
        best["score"] >= FUZZY_AUTO_MATCH_THRESHOLD
        and best["score"] - second_score >= 0.10
    ):
        return {
            "status": "resolved",
            "product": best["product"],
            "match_type": "fuzzy",
            "original_query": product_query,
        }

    return {
        "status": "suggestions",
        "matches": [
            item["product"]
            for item in scored_products[:5]
        ],
    }


async def prepare_order(
    tool_call: ToolCall,
    access_token: str,
) -> ToolResult:
    customer_id = str(
        tool_call.arguments.get(
            "customer_id",
            "",
        )
    ).strip()

    requested_items: Any = tool_call.arguments.get(
        "items",
        [],
    )

    if not customer_id:
        return ToolResult(
            call_id=tool_call.call_id,
            output={
                "error": "Customer ID is required.",
            },
        )

    if (
        not isinstance(requested_items, list)
        or not requested_items
    ):
        return ToolResult(
            call_id=tool_call.call_id,
            output={
                "error": (
                    "At least one order item is required."
                ),
            },
        )

    products = await oms_api_client.get_products(
        access_token
    )

    draft_items: list[DraftOrderItem] = []

    for requested_item in requested_items:
        product_query = str(
            requested_item.get(
                "product_query",
                "",
            )
        ).strip()

        try:
            quantity = int(
                requested_item.get(
                    "quantity",
                    0,
                )
            )
        except (TypeError, ValueError):
            quantity = 0

        if not product_query:
            return ToolResult(
                call_id=tool_call.call_id,
                output={
                    "error": (
                        "Each item must include a product."
                    ),
                },
            )

        if quantity <= 0:
            return ToolResult(
                call_id=tool_call.call_id,
                output={
                    "error": (
                        "Order quantities must be greater "
                        "than zero."
                    ),
                },
            )

        resolution = resolve_product(
            product_query=product_query,
            products=products,
        )

        if resolution["status"] == "not_found":
            return ToolResult(
                call_id=tool_call.call_id,
                output={
                    "error": (
                        f'No product could be matched to '
                        f'"{product_query}".'
                    ),
                    "message": (
                        "Ask the user for a product name, "
                        "SKU, or product ID."
                    ),
                },
            )

        if resolution["status"] in {
            "ambiguous",
            "suggestions",
        }:
            return ToolResult(
                call_id=tool_call.call_id,
                output={
                    "error": (
                        f'I could not safely determine which '
                        f'product "{product_query}" refers to.'
                    ),
                    "matches": resolution["matches"],
                    "message": (
                        "Show these matching products to the "
                        "user and ask them to choose one."
                    ),
                },
            )

        product = resolution["product"]

        draft_items.append(
            DraftOrderItem(
                product_id=str(product["id"]),
                sku=str(product["sku"]),
                name=str(product["name"]),
                quantity=quantity,
                unit_price=float(
                    product["price"]
                ),
            )
        )

    total_amount = sum(
        item.unit_price * item.quantity
        for item in draft_items
    )

    pending_order = PendingOrderDraft(
        customer_id=customer_id,
        items=draft_items,
        total_amount=round(
            total_amount,
            2,
        ),
    )

    return ToolResult(
        call_id=tool_call.call_id,
        output={
            "action": "order_draft_prepared",
            "pending_order": (
                pending_order.model_dump()
            ),
            "message": (
                "The order has only been prepared. "
                "It has NOT been submitted. "
                "Summarize it and ask the user "
                "for explicit confirmation."
            ),
        },
    )


async def confirm_order(
    tool_call: ToolCall,
    access_token: str,
    pending_order: PendingOrderDraft | None,
) -> ToolResult:
    if pending_order is None:
        return ToolResult(
            call_id=tool_call.call_id,
            output={
                "error": (
                    "There is no pending order "
                    "to confirm."
                ),
            },
        )

    items = [
        {
            "productId": item.product_id,
            "quantity": item.quantity,
        }
        for item in pending_order.items
    ]

    order = await oms_api_client.create_order(
        customer_id=pending_order.customer_id,
        items=items,
        access_token=access_token,
    )

    return ToolResult(
        call_id=tool_call.call_id,
        output={
            "action": "order_created",
            "order": order,
        },
    )