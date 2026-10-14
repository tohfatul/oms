using Microsoft.EntityFrameworkCore;
using OrderManagement.Application.Orders.CreateOrder;
using OrderManagement.Domain.Entities;
using OrderManagement.Domain.Enums;
using OrderManagement.Infrastructure.Persistence;
using OrderManagement.Application.Orders.GetOrder;
using OrderManagement.Application.Common;
using System.Text.Json;
using OrderManagement.Application.Events;

namespace OrderManagement.Infrastructure.Orders;

public class OrderService(OrderDbContext dbContext) : IOrderService
{
    public async Task<CreateOrderResponse> CreateAsync(
     CreateOrderRequest request,
     string tenantId,
     string userObjectId,
     CancellationToken cancellationToken)
    {
        if (request.Items.Count == 0)
        {
            throw new ValidationException("An order must contain at least one item.");
        }

        if (request.Items.Any(x => x.Quantity <= 0))
        {
            throw new ValidationException("Quantity must be greater than zero.");
        }

        var productIds = request.Items
            .Select(x => x.ProductId)
            .Distinct()
            .ToList();

        var products = await dbContext.Products
            .Where(x => productIds.Contains(x.Id) && x.IsActive)
            .ToDictionaryAsync(
                x => x.Id,
                cancellationToken);

        if (products.Count != productIds.Count)
        {
            throw new ValidationException(
                "One or more products are invalid or inactive.");
        }

        var order = new Order
        {
            Id = Guid.NewGuid(),
            OrderNumber =
                $"ORD-{DateTime.UtcNow:yyyyMMddHHmmss}-{Random.Shared.Next(1000, 9999)}",
            CustomerId = request.CustomerId,

            UserTenantId = tenantId,
            UserObjectId = userObjectId,

            Status = OrderStatus.Submitted,
            CreatedAt = DateTimeOffset.UtcNow
        };

        foreach (var requestItem in request.Items)
        {
            var product = products[requestItem.ProductId];

            var totalPrice =
                product.Price * requestItem.Quantity;

            order.Items.Add(new OrderItem
            {
                Id = Guid.NewGuid(),
                ProductId = product.Id,
                ProductSku = product.Sku,
                ProductName = product.Name,
                UnitPrice = product.Price,
                Quantity = requestItem.Quantity,
                TotalPrice = totalPrice
            });
        }

        order.TotalAmount =
            order.Items.Sum(x => x.TotalPrice);

        dbContext.Orders.Add(order);

        var orderCreatedEvent = new OrderCreatedEvent(
            Guid.NewGuid(),
            order.Id,
            order.OrderNumber,
            order.CustomerId,
            order.TotalAmount,
            order.CreatedAt,
            order.Items
                .Select(x => new OrderCreatedItem(
                    x.ProductId,
                    x.ProductSku,
                    x.ProductName,
                    x.UnitPrice,
                    x.Quantity))
                .ToList());

        var outboxMessage = new OutboxMessage
        {
            Id = orderCreatedEvent.EventId,
            Type = "OrderCreated",
            Payload = JsonSerializer.Serialize(orderCreatedEvent),
            CreatedAt = DateTimeOffset.UtcNow,
            RetryCount = 0
        };

        dbContext.OutboxMessages.Add(outboxMessage);

        await dbContext.SaveChangesAsync(cancellationToken);

        return new CreateOrderResponse(
            order.Id,
            order.OrderNumber,
            order.TotalAmount,
            order.Status.ToString());
    }


    public async Task<GetOrderResponse?> GetByIdAsync(
    Guid id,
    string tenantId,
    string userObjectId,
    CancellationToken cancellationToken)
    {
        var order = await dbContext.Orders
            .AsNoTracking()
            .Include(x => x.Items)
            .FirstOrDefaultAsync(
                x => 
                x.Id == id &&
                x.UserTenantId == tenantId &&
                x.UserObjectId == userObjectId,
                cancellationToken);

        if (order is null)
        {
            return null;
        }

        return new GetOrderResponse(
            order.Id,
            order.OrderNumber,
            order.CustomerId,
            order.Status.ToString(),
            order.TotalAmount,
            order.CreatedAt,
            order.Items
                .Select(x => new GetOrderItemResponse(
                    x.ProductId,
                    x.ProductSku,
                    x.ProductName,
                    x.UnitPrice,
                    x.Quantity,
                    x.TotalPrice))
                .ToList());
    }
}