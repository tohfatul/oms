using OrderManagement.Application.Orders.GetOrder;
using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Application.Orders.CreateOrder;

public interface IOrderService
{
    Task<CreateOrderResponse> CreateAsync(CreateOrderRequest request, CancellationToken cancellationToken);
    Task<GetOrderResponse?> GetByIdAsync(Guid orderId, CancellationToken cancellationToken);
}
