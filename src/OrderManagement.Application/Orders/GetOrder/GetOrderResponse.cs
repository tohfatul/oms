using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Application.Orders.GetOrder;

public record GetOrderResponse(
    Guid OrderId,
    string OrderNumber,
    string CustomerId,
    string Status,
    decimal TotalAmount,
    DateTimeOffset CreatedAt,
    List<GetOrderItemResponse> Items);

public record GetOrderItemResponse(
    Guid ProductId,
    string ProductSku,
    string ProductName,
    decimal UnitPrice,
    int Quantity,
    decimal TotalPrice);
