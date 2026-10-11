using Microsoft.EntityFrameworkCore;
using OrderManagement.Domain.Entities;

namespace OrderManagement.Infrastructure.Persistence;

public static class DatabaseSeeder
{
    public static async Task SeedAsync(OrderDbContext dbContext)
    {
        if (await dbContext.Products.AnyAsync())
        {
            return;
        }

        var products = new[]
        {
            new Product
            {
                Id = Guid.NewGuid(),
                Sku = "SKU-1001",
                Name = "Laptop",
                Description = "Business laptop",
                Price = 999.00m,
                IsActive = true
            },
            new Product
            {
                Id = Guid.NewGuid(),
                Sku = "SKU-1002",
                Name = "Monitor",
                Description = "Business Monitor",
                Price = 299.00m,
                IsActive = true
            },
            new Product
            {
                Id = Guid.NewGuid(),
                Sku = "SKU-1003",
                Name = "Keyboard",
                Description = "Business Keyboard",
                Price = 79.00m,
                IsActive = true
            },
            new Product
            {
                Id = Guid.NewGuid(),
                Sku = "SKU-1004",
                Name = "Mouse",
                Description = "Business Mouse",
                Price = 49.00m,
                IsActive = true
            }
        };

        dbContext.Products.AddRange(products);

        await dbContext.SaveChangesAsync();
    }
}