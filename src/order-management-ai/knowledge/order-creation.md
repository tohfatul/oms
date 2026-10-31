\# Creating Orders



To create an order, the user must provide a customer ID and at least one product with a quantity.



Products may be identified by product name, SKU, or product ID.



An example request is:



Create an order for customer CUST-100 with 2 Business Laptop and 1 Wireless Mouse.



Multiple products may be included in the same order.



Before an AI-assisted order is submitted, OrderFlow prepares a draft containing the customer, products, quantities, prices, and total amount.



The AI assistant must request explicit user confirmation before submitting the order.



A prepared order is not considered created until the user confirms it and the OrderFlow API successfully creates the order.

