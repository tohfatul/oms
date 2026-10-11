using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Domain.Entities
{
    public class Product
    {
        public Guid Id { get; set; }

        public required string Sku { get; set; }

        public required string Name { get; set; }
        public string? Description { get; set; }

        public decimal Price { get; set; }

        public bool IsActive { get; set; } = true;
    }
}
