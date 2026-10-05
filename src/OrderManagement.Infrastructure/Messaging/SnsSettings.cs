namespace OrderManagement.Infrastructure.Messaging;

public class SnsSettings
{
    public const string SectionName = "AWS:SNS";

    public string TopicArn { get; set; } = string.Empty;

    public string Region { get; set; } = "us-east-1";

    public string? ServiceUrl { get; set; }
}