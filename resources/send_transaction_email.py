from django.core.mail import send_mail, EmailMessage

from rent_manager import settings


def send_transaction_email(transaction):
    email = EmailMessage(
        subject="Payment Receipt",
        body=f"""
Hi {transaction.rm_map.person.f_name},

Payment received successfully.

Transaction No: {transaction.tnx_no}
Month: {transaction.ts.strftime("%B %Y").upper()}
Amount: ₹{transaction.amount}
Comment: ₹{transaction.comment}
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[transaction.rm_map.person.email],
    )

    if transaction.receipt:
        email.attach_file(transaction.receipt.path)

    email.send()
