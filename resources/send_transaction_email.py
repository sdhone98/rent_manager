from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.db.models import Window, F
from django.db.models.functions import RowNumber
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
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


def send_de_allotment_email(room_allotment):
    person = room_allotment.person

    transactions = (
        room_allotment.transactions
        .annotate(
            no=Window(
                expression=RowNumber(),
                order_by=F("ts").asc()
            )
        )
        .values(
            "no",
            "tnx_no",
            "amount",
            "payment_mode",
            "comment",
            "ts"
        )
    )

    context = {
        "f_name": person.f_name,
        "m_name": person.m_name,
        "l_name": person.l_name,
        "COMPANY_EMAIL": settings.COMPANY_EMAIL,
        "room_no": room_allotment.room.r_no,
        "building_name": room_allotment.room.build_name,
        "start_date": room_allotment.start_date,
        "end_date": room_allotment.end_date,
        "actual_end_date": room_allotment.actual_end_date,
        "transactions": transactions,
        "date": timezone.now(),
    }

    html_content = render_to_string(
        "de_allotment_summary.html",
        context
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject="Room De-Allotment & Payment Summary",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[person.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
