using System.Text.Json;
using Amazon.SQS;
using Amazon.SQS.Model;
using Microsoft.Extensions.Options;
using OrderManagement.Application.Events;

namespace OrderManagement.NotificationWorker;

public class Worker(
    IAmazonSQS sqsClient,
    IOptions<SqsSettings> settings,
    ILogger<Worker> logger)
    : BackgroundService
{
    protected override async Task ExecuteAsync(
        CancellationToken stoppingToken)
    {
        logger.LogInformation(
            "Notification Worker started.");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ReceiveMessagesAsync(stoppingToken);
            }
            catch (OperationCanceledException)
                when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                logger.LogError(
                    ex,
                    "Error receiving notification messages.");

                await Task.Delay(
                    TimeSpan.FromSeconds(5),
                    stoppingToken);
            }
        }
    }

    private async Task ReceiveMessagesAsync(
        CancellationToken cancellationToken)
    {
        var response =
            await sqsClient.ReceiveMessageAsync(
                new ReceiveMessageRequest
                {
                    QueueUrl = settings.Value.QueueUrl,
                    MaxNumberOfMessages = 10,
                    WaitTimeSeconds = 20,
                    VisibilityTimeout = 30
                },
                cancellationToken);

        foreach (var message in response.Messages)
        {
            await ProcessMessageAsync(
                message,
                cancellationToken);
        }
    }

    private async Task ProcessMessageAsync(
        Message message,
        CancellationToken cancellationToken)
    {
        try
        {
            var orderCreated =
                JsonSerializer.Deserialize<OrderCreatedEvent>(
                    message.Body);

            if (orderCreated is null)
            {
                logger.LogWarning(
                    "Unable to deserialize notification message.");
                return;
            }

            // Simulate user notification
            logger.LogInformation(
                "Sending notification: Order {OrderNumber} " +
                "was submitted successfully for customer {CustomerId}.",
                orderCreated.OrderNumber,
                orderCreated.CustomerId);

            await Task.Delay(
                TimeSpan.FromSeconds(1),
                cancellationToken);

            logger.LogInformation(
                "Notification sent for order {OrderNumber}.",
                orderCreated.OrderNumber);

            await sqsClient.DeleteMessageAsync(
                settings.Value.QueueUrl,
                message.ReceiptHandle,
                cancellationToken);
        }
        catch (Exception ex)
        {
            logger.LogError(
                ex,
                "Failed to process notification message {MessageId}.",
                message.MessageId);
        }
    }
}