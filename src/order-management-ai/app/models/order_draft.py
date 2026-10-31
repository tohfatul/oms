from pydantic import BaseModel, Field


class DraftOrderItem(BaseModel):
    product_id: str
    sku: str
    name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)


class PendingOrderDraft(BaseModel):
    customer_id: str = Field(min_length=1)

    items: list[DraftOrderItem] = Field(
        min_length=1,
    )

    total_amount: float = Field(ge=0)