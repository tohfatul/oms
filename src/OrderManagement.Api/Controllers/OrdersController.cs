using Microsoft.AspNetCore.Mvc;
using OrderManagement.Application.Orders.CreateOrder;

namespace OrderManagement.Api.Controllers;

[ApiController]
[Route("api/orders")]
public class OrdersController(IOrderService orderService) : ControllerBase
{
    [HttpPost]
    public async Task<ActionResult<CreateOrderResponse>> CreateOrder(
        CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        var order = await orderService.CreateAsync(
            request,
            cancellationToken);

        return Created(
            $"/api/orders/{order.OrderId}",
            order);
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetOrder(
        Guid id,
        CancellationToken cancellationToken)
    {
        var order = await orderService.GetByIdAsync(
            id,
            cancellationToken);

        if (order is null)
        {
            return NotFound();
        }

        return Ok(order);
    }
}