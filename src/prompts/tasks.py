EMAIL_CATEGORIZER_TASK = """
Instructions:
    1. Review the provided email content thoroughly.
    2. Use the following rules to assign the correct category:
        - **product enquiry**: When the email seeks information about a product features, pricing, or availability.
        - **customer complaint**: When the email expresses dissatisfaction regarding a product, service, or support experience.
        - **customer feedback**: When the email provides suggestions, compliments, or general feedback about the product or service.
        - **unrelated**: When the email does not pertain to the company's products or services.
EMAIL CONTENT:
{email}

Notes:
    - Base your categorization strictly on the email content provided; avoid making assumptions beyond the text.
"""