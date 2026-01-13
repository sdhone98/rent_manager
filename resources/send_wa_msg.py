from twilio.rest import Client
from rent_manager import settings


def send_whatsapp_receipt(transaction):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message_body = f"""
    🧾 *Transaction Receipt*
    
    Txn No: {transaction.tnx_no}
    Person: {transaction.rm_map.person.f_name} {transaction.rm_map.person.l_name}
    Amount: ₹{transaction.amount}
    Mode: {transaction.payment_mode}
    Date: {transaction.ts.strftime('%Y-%m-%d %H:%M')}

    Thank you for your payment! 🙏
    """

    message = client.messages.create(
        body=message_body,
        from_='whatsapp:+14155238886',
        to=f"whatsapp:+91{transaction.rm_map.person.contacts.wa_no}",
    )
    return message.sid
