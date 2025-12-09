import pytest
from unittest.mock import AsyncMock, patch

from temporalio.exceptions import ActivityError

from activities.order_activities import reserve_inventory_activity
from temporal_models import OrderFulfillmentInput, TemporalOrderItem

@pytest.mark.asyncio
async def test_reserve_inventory_success():
    order = OrderFulfillmentInput(
        user_id=1,
        order_id=123,
        items=[
            TemporalOrderItem(product_id=1, quantity=5, price=10.0),
            TemporalOrderItem(product_id=2, quantity=3, price=20.0),
        ]
    )

    # Mock the httpx response
    with patch('inventory_client.httpx.AsyncClient.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"reservationId": "res-123"}
        mock_post.return_value = mock_response

        result = await reserve_inventory_activity(order)

        assert len(result) == 2
        assert result == ["res-123", "res-123"]


@pytest.mark.asyncio
async def test_reserve_inventory_failure():
    order = OrderFulfillmentInput(
        user_id=1,
        order_id=123,
        items=[TemporalOrderItem(product_id=1, quantity=100, price=10.0)]
    )

    with patch('inventory_client.httpx.AsyncClient.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {"error": "INSUFFICIENT_STOCK", "message": "Only 5 available"}
        mock_post.return_value = mock_response

        with pytest.raises(ActivityError):
            await reserve_inventory_activity(order)