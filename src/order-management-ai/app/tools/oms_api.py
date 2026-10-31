from typing import Any
from uuid import UUID

import httpx

from app.core.config import settings


class OmsApiError(Exception):
    pass


class OmsApiClient:
    def __init__(self):
        self.base_url = settings.oms_api_base_url.rstrip("/")

    def _headers(
        self,
        access_token: str,
    ) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

    async def get_products(
        self,
        access_token: str,
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/products"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers=self._headers(access_token),
            )

        if response.status_code == 401:
            raise OmsApiError(
                "User is not authorized to access products."
            )

        if response.status_code != 200:
            raise OmsApiError(
                f"Unable to retrieve products. "
                f"OMS API returned {response.status_code}."
            )

        return response.json()

    async def search_products(
        self,
        query: str,
        access_token: str,
    ) -> list[dict[str, Any]]:
        products = await self.get_products(
            access_token,
        )

        normalized_query = query.strip().lower()

        if not normalized_query:
            return products

        results = []

        for product in products:
            searchable_values = [
                str(product.get("sku", "")),
                str(product.get("name", "")),
                str(product.get("description", "")),
            ]

            if any(
                normalized_query in value.lower()
                for value in searchable_values
            ):
                results.append(product)

        return results

    async def get_order(
        self,
        order_id: str,
        access_token: str,
    ) -> dict[str, Any] | None:
        try:
            UUID(order_id)
        except ValueError as exc:
            raise OmsApiError(
                "Invalid order ID."
            ) from exc

        url = f"{self.base_url}/api/orders/{order_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers=self._headers(access_token),
            )

        if response.status_code == 404:
            return None

        if response.status_code == 401:
            raise OmsApiError(
                "User is not authorized to access this order."
            )

        if response.status_code != 200:
            raise OmsApiError(
                f"Unable to retrieve order. "
                f"OMS API returned {response.status_code}."
            )

        return response.json()

    async def create_order(
        self,
        customer_id: str,
        items: list[dict[str, Any]],
        access_token: str,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/api/orders"

        payload = {
            "customerId": customer_id,
            "items": items,
        }

        headers = self._headers(access_token)
        headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        if response.status_code == 401:
            raise OmsApiError(
                "User is not authorized to create orders."
            )

        if response.status_code not in (200, 201):
            raise OmsApiError(
                f"Unable to create order. "
                f"OMS API returned {response.status_code}: "
                f"{response.text}"
            )

        return response.json()


oms_api_client = OmsApiClient()