using Amazon;
using Amazon.Runtime;
using Amazon.SQS;
using OrderManagement.NotificationWorker;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.Configure<SqsSettings>(
    builder.Configuration.GetSection(SqsSettings.SectionName));

var sqsSettings =
    builder.Configuration
        .GetSection(SqsSettings.SectionName)
        .Get<SqsSettings>()
    ?? new SqsSettings();

builder.Services.AddSingleton<IAmazonSQS>(_ =>
{
    if (!string.IsNullOrWhiteSpace(sqsSettings.ServiceUrl))
    {
        var credentials =
            new BasicAWSCredentials("test", "test");

        var config = new AmazonSQSConfig
        {
            ServiceURL = sqsSettings.ServiceUrl,
            AuthenticationRegion = sqsSettings.Region
        };

        return new AmazonSQSClient(
            credentials,
            config);
    }

    return new AmazonSQSClient(
        RegionEndpoint.GetBySystemName(
            sqsSettings.Region));
});

builder.Services.AddHostedService<Worker>();

var host = builder.Build();

host.Run();