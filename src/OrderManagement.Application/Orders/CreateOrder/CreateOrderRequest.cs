using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Application.Orders.CreateOrder;

public record CreateOrderRequest(string CustomerId, List<CreateOrderItemRequest> Items);

public record CreateOrderItemRequest(Guid ProductId, int Quantity);

