using Amazon.SimpleNotificationService;
using Amazon.SimpleNotificationService.Model;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using OrderManagement.Infrastructure.Persistence;

namespace OrderManagement.Infrastructure.Messaging;

public class OutboxPublisher(
    IServiceScopeFactory scopeFactory,
    IAmazonSimpleNotificationService snsClient,
    IOptions<SnsSettings> settings,
    ILogger<OutboxPublisher> logger)
    : BackgroundService
{
    protected override async Task ExecuteAsync(
        CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await PublishPendingMessages(stoppingToken);
            }
            catch (Exception ex)
            {
                logger.LogError(
                    ex,
                    "Error processing outbox messages.");
            }

            await Task.Delay(
                TimeSpan.FromSeconds(5),
                stoppingToken);
        }
    }

    private async Task PublishPendingMessages(
        CancellationToken cancellationToken)
    {
        using var scope = scopeFactory.CreateScope();

        var dbContext =
            scope.ServiceProvider.GetRequiredService<OrderDbContext>();

        var messages = await dbContext.OutboxMessages
            .Where(x => x.ProcessedAt == null)
            .OrderBy(x => x.CreatedAt)
            .Take(10)
            .ToListAsync(cancellationToken);

        foreach (var message in messages)
        {
            try
            {
                var request = new PublishRequest
                {
                    TopicArn = settings.Value.TopicArn,
                    Message = message.Payload,

                    MessageAttributes =
                        new Dictionary<string, MessageAttributeValue>
                        {
                            ["EventType"] =
                                new MessageAttributeValue
                                {
                                    DataType = "String",
                                    StringValue = message.Type
                                }
                        }
                };

                await snsClient.PublishAsync(
                    request,
                    cancellationToken);

                message.ProcessedAt =
                    DateTimeOffset.UtcNow;

                message.Error = null;

                logger.LogInformation(
                    "Published outbox message {MessageId} of type {EventType}.",
                    message.Id,
                    message.Type);
            }
            catch (Exception ex)
            {
                message.RetryCount++;

                message.Error = ex.Message;

                logger.LogError(
                    ex,
                    "Failed to publish outbox message {MessageId}.",
                    message.Id);
            }

            await dbContext.SaveChangesAsync(
                cancellationToken);
        }
    }
}