using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OrderManagement.Infrastructure.Persistence;

namespace OrderManagement.Api.Controllers;

[ApiController]
[Route("api/products")]
[Authorize]
public class ProductsController(OrderDbContext dbContext) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetProducts(
        CancellationToken cancellationToken)
    {
        var products = await dbContext.Products
            .AsNoTracking()
            .Where(x => x.IsActive)
            .Select(x => new
            {
                x.Id,
                x.Sku,
                x.Name,
                x.Description,
                x.Price
            })
            .ToListAsync(cancellationToken);

        return Ok(products);
    }
}