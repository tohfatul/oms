\# OrderFlow AI Assistant



The OrderFlow AI assistant is implemented as a separate Python and FastAPI service.



LangGraph orchestrates AI reasoning and tool execution.



The assistant currently supports catalog product search, existing-order lookup, order preparation, and confirmed order creation.



Order creation requires explicit confirmation before the write operation is performed.



The assistant uses the authenticated user's Microsoft Entra access token when calling protected OrderFlow APIs.



The FastAPI service validates Microsoft Entra access tokens before allowing AI requests.



The assistant must not claim capabilities that are not implemented.



Unsupported capabilities currently include inventory quantity lookup, order cancellation, modification of submitted orders, refunds, payment processing, and shipment tracking.

