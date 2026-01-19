import os
from django.template.loader import render_to_string
from rent_manager import settings


def generate_transaction_html(transaction):
    file_name = f"{transaction.tnx_no}.html"

    dir_path = os.path.join(settings.MEDIA_ROOT, "receipts", "html")
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, file_name)

    html_content = render_to_string(
        "invoice.html",
        {
            "transaction": transaction,
            "COMPANY_EMAIL": settings.COMPANY_EMAIL,
            "MONTH": transaction.ts.strftime("%B %Y").upper(),
        }
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return f"receipts/html/{file_name}"
