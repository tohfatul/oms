using OrderManagement.Application.Common;

namespace OrderManagement.Api.Middleware;

public class ExceptionHandlingMiddleware(
    RequestDelegate next,
    ILogger<ExceptionHandlingMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await next(context);
        }
        catch (ValidationException ex)
        {
            context.Response.StatusCode =
                StatusCodes.Status400BadRequest;

            context.Response.ContentType =
                "application/json";

            await context.Response.WriteAsJsonAsync(new
            {
                status = 400,
                error = "Validation failed",
                message = ex.Message
            });
        }
        catch (Exception ex)
        {
            logger.LogError(
                ex,
                "Unhandled exception occurred.");

            context.Response.StatusCode =
                StatusCodes.Status500InternalServerError;

            context.Response.ContentType =
                "application/json";

            await context.Response.WriteAsJsonAsync(new
            {
                status = 500,
                error = "Internal server error",
                message = "An unexpected error occurred."
            });
        }
    }
}