\# Order Processing



OrderFlow uses event-driven processing for order workflows.



When an order is created, the backend persists the order in PostgreSQL.



Order-related events can be published through Amazon SNS and delivered to Amazon SQS queues.



Independent workers can process those messages for downstream ERP processing and notifications.



This architecture allows background processing to remain decoupled from the synchronous order-creation API.



The platform uses an outbox-based approach to improve reliability when publishing events associated with database changes.

