using OrderManagement.Domain.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Domain.Entities
{
    public class Order
    {
        public Guid Id { get; set; }

        public required string OrderNumber { get; set; }

        public required string CustomerId { get; set; }

        public string UserTenantId { get; set; } = string.Empty;

        public string UserObjectId { get; set; } = string.Empty;

        public OrderStatus Status { get; set; }

        public decimal TotalAmount { get; set; }

        public DateTimeOffset CreatedAt { get; set; }

        public ICollection<OrderItem> Items { get; set; } = [];

    }
}
