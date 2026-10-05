namespace OrderManagement.NotificationWorker;

public class SqsSettings
{
    public const string SectionName = "AWS:SQS";

    public string Region { get; set; } = "us-east-1";

    public string? ServiceUrl { get; set; }

    public string QueueUrl { get; set; } = string.Empty;
}