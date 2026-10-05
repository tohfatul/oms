namespace OrderManagement.Domain.Entities;

public class OutboxMessage
{
    public Guid Id { get; set; }

    public required string Type { get; set; }

    public required string Payload { get; set; }

    public DateTimeOffset CreatedAt { get; set; }

    public DateTimeOffset? ProcessedAt { get; set; }

    public int RetryCount { get; set; }

    public string? Error { get; set; }
}