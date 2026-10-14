using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OrderManagement.Application.Orders.CreateOrder;
using System.Security.Claims;
using Microsoft.Identity.Web;

namespace OrderManagement.Api.Controllers;

[ApiController]
[Route("api/orders")]
[Authorize]
public class OrdersController(IOrderService orderService) : ControllerBase
{
    [HttpPost]
    public async Task<ActionResult<CreateOrderResponse>> CreateOrder(
    CreateOrderRequest request,
    CancellationToken cancellationToken)
    {
        var currentUser = GetCurrentUser();

        if (currentUser is null)
        {
            return Unauthorized();
        }

        var order = await orderService.CreateAsync(
            request,
            currentUser.Value.TenantId,
            currentUser.Value.UserObjectId,
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
        var currentUser = GetCurrentUser();

        if (currentUser is null)
        {
            return Unauthorized();
        }

        var order = await orderService.GetByIdAsync(
            id,
            currentUser.Value.TenantId,
            currentUser.Value.UserObjectId,
            cancellationToken);

        if (order is null)
        {
            return NotFound();
        }

        return Ok(order);
    }

    // helpers
    private (string TenantId, string UserObjectId)? GetCurrentUser()
    {
        var tenantId = User.GetTenantId();
        var userObjectId = User.GetObjectId();

        if (string.IsNullOrWhiteSpace(tenantId) ||
            string.IsNullOrWhiteSpace(userObjectId))
        {
            return null;
        }

        return (tenantId, userObjectId);
    }
}