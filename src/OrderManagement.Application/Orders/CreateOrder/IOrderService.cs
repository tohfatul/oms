using OrderManagement.Application.Orders.GetOrder;
using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Application.Orders.CreateOrder;

public interface IOrderService
{
    Task<CreateOrderResponse> CreateAsync(
        CreateOrderRequest request,
        string tenantId,
        string userObjectId,
        CancellationToken cancellationToken);

    Task<GetOrderResponse?> GetByIdAsync(
        Guid id,
        string tenantId,
        string userObjectId,
        CancellationToken cancellationToken);
}
