using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;
using Microsoft.EntityFrameworkCore;
using OrderManagement.Application.Orders.CreateOrder;
using OrderManagement.Infrastructure.Orders;
using OrderManagement.Infrastructure.Persistence;
using OrderManagement.Api.Middleware;
using Amazon;
using Amazon.Runtime;
using Amazon.SimpleNotificationService;
using OrderManagement.Infrastructure.Messaging;

var builder = WebApplication.CreateBuilder(args);

// Register application services
builder.Services.AddControllers();
builder.Services.AddOpenApi();

// Register PostgreSQL / EF Core
//builder.Services.AddDbContext<OrderDbContext>(options =>
//{
//    options.UseNpgsql(
//        builder.Configuration.GetConnectionString("OrderDatabase"));
//});

builder.Services.AddDbContext<OrderDbContext>(options =>
{
    var connectionString =
        builder.Configuration.GetConnectionString("OrderDatabase");

    if (string.IsNullOrWhiteSpace(connectionString))
    {
        var host =
            builder.Configuration["Database:Host"];

        var port =
            builder.Configuration["Database:Port"] ?? "5432";

        var database =
            builder.Configuration["Database:Name"];

        var username =
            builder.Configuration["Database:Username"];

        var password =
            builder.Configuration["Database:Password"];

        connectionString =
            $"Host={host};" +
            $"Port={port};" +
            $"Database={database};" +
            $"Username={username};" +
            $"Password={password}";
    }

    options.UseNpgsql(connectionString);
});

// Register order service
builder.Services.AddScoped<IOrderService, OrderService>();

builder.Services.Configure<SnsSettings>(
    builder.Configuration.GetSection(SnsSettings.SectionName));

var snsSettings =
    builder.Configuration
        .GetSection(SnsSettings.SectionName)
        .Get<SnsSettings>()
    ?? new SnsSettings();

builder.Services.AddSingleton<IAmazonSimpleNotificationService>(_ =>
{
    if (!string.IsNullOrWhiteSpace(snsSettings.ServiceUrl))
    {
        // LocalStack
        var credentials =
            new BasicAWSCredentials("test", "test");

        var config =
            new AmazonSimpleNotificationServiceConfig
            {
                ServiceURL = snsSettings.ServiceUrl,
                AuthenticationRegion = snsSettings.Region
            };

        return new AmazonSimpleNotificationServiceClient(
            credentials,
            config);
    }

    // Real AWS
    return new AmazonSimpleNotificationServiceClient(
        RegionEndpoint.GetBySystemName(snsSettings.Region));
});

builder.Services.AddHostedService<OutboxPublisher>();

// entra id authentication/ authorization
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(
        builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization();

// cors config
builder.Services.AddCors(options =>
{
    options.AddPolicy("OmsWeb", policy =>
    {
        policy
            .WithOrigins("http://localhost:5173", "https://app.digizerones.com")
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

var app = builder.Build();

// Seed development data
//using (var scope = app.Services.CreateScope())
//{
//    var dbContext =
//        scope.ServiceProvider.GetRequiredService<OrderDbContext>();

//    await DatabaseSeeder.SeedAsync(dbContext);
//}

//using (var scope = app.Services.CreateScope())
//{
//    var dbContext =
//        scope.ServiceProvider.GetRequiredService<OrderDbContext>();

//    if (app.Environment.IsDevelopment())
//    {
//        await dbContext.Database.MigrateAsync();
//    }

//    await DatabaseSeeder.SeedAsync(dbContext);
//}

var runMigrationsOnly =
    app.Configuration.GetValue<bool>("Database:RunMigrationsOnly");

using (var scope = app.Services.CreateScope())
{
    var dbContext =
        scope.ServiceProvider.GetRequiredService<OrderDbContext>();

    if (runMigrationsOnly)
    {
        app.Logger.LogInformation(
            "Running database migrations...");

        await dbContext.Database.MigrateAsync();

        app.Logger.LogInformation(
            "Database migrations completed.");

        await DatabaseSeeder.SeedAsync(dbContext);

        app.Logger.LogInformation(
            "Database seed completed.");

        return;
    }

    if (app.Environment.IsDevelopment())
    {
        await dbContext.Database.MigrateAsync();
    }

    await DatabaseSeeder.SeedAsync(dbContext);
}

// Development-only OpenAPI endpoint
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseMiddleware<ExceptionHandlingMiddleware>();

app.UseCors("OmsWeb");

app.UseAuthentication();
app.UseAuthorization();

// We are using HTTP locally for now
// app.UseHttpsRedirection();

// Map attribute-routed controllers
app.MapControllers();

app.MapGet("/health/live", () =>
{
    return Results.Ok(new
    {
        status = "Healthy"
    });
});

app.MapGet("/health/ready", async (
    OrderDbContext dbContext,
    CancellationToken cancellationToken) =>
{
    var canConnect =
        await dbContext.Database.CanConnectAsync(cancellationToken);

    if (!canConnect)
    {
        return Results.Json(
            new { status = "Unhealthy" },
            statusCode: StatusCodes.Status503ServiceUnavailable);
    }

    return Results.Ok(new
    {
        status = "Healthy"
    });
});

app.Run();