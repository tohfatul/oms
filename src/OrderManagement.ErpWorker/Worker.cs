using System.Text.Json;
using Amazon.SQS;
using Amazon.SQS.Model;
using Microsoft.Extensions.Options;
using OrderManagement.Application.Events;

namespace OrderManagement.ErpWorker;

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
            "ERP Worker started. Listening to {QueueUrl}",
            settings.Value.QueueUrl);

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
                    "Error receiving messages from ERP queue.");

                await Task.Delay(
                    TimeSpan.FromSeconds(5),
                    stoppingToken);
            }
        }
    }

    private async Task ReceiveMessagesAsync(
        CancellationToken cancellationToken)
    {
        var request = new ReceiveMessageRequest
        {
            QueueUrl = settings.Value.QueueUrl,

            MaxNumberOfMessages = 10,

            // SQS long polling
            WaitTimeSeconds = 20,

            VisibilityTimeout = 30
        };

        var response =
            await sqsClient.ReceiveMessageAsync(
                request,
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
                    "Unable to deserialize message {MessageId}.",
                    message.MessageId);

                return;
            }

            if (orderCreated.CustomerId == "FAIL-ERP")
            {
                throw new InvalidOperationException(
                    "Simulated ERP processing failure.");
            }

            logger.LogInformation(
                "ERP processing order {OrderNumber}, OrderId {OrderId}",
                orderCreated.OrderNumber,
                orderCreated.OrderId);

            // Simulate ERP processing
            await Task.Delay(
                TimeSpan.FromSeconds(2),
                cancellationToken);

            logger.LogInformation(
                "ERP successfully processed order {OrderNumber}.",
                orderCreated.OrderNumber);

            // Delete only AFTER successful processing
            await sqsClient.DeleteMessageAsync(
                settings.Value.QueueUrl,
                message.ReceiptHandle,
                cancellationToken);

            logger.LogInformation(
                "Deleted message {MessageId} from ERP queue.",
                message.MessageId);
        }
        catch (JsonException ex)
        {
            logger.LogError(
                ex,
                "Invalid JSON received in message {MessageId}.",
                message.MessageId);
        }
        catch (Exception ex)
        {
            logger.LogError(
                ex,
                "Failed processing SQS message {MessageId}.",
                message.MessageId);

            // Intentionally do NOT delete.
            // SQS will make the message visible again
            // after the visibility timeout.
        }
    }
}