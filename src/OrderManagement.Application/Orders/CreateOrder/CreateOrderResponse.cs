using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Application.Orders.CreateOrder;

public record CreateOrderResponse(Guid OrderId, string OrderNumber, decimal TotalAmount, string Status);