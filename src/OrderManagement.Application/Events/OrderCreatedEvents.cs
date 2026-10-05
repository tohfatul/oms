namespace OrderManagement.Application.Events;

public record OrderCreatedEvent(
    Guid EventId,
    Guid OrderId,
    string OrderNumber,
    string CustomerId,
    decimal TotalAmount,
    DateTimeOffset CreatedAt,
    List<OrderCreatedItem> Items);

public record OrderCreatedItem(
    Guid ProductId,
    string ProductSku,
    string ProductName,
    decimal UnitPrice,
    int Quantity);