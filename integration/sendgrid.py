import asyncio

from aiohttp_sendgrid import Sendgrid

import config

def send_email(from_address: str, to_addresses: list, subject: str, body_html: str,
                     cc_addresses: list=None, bcc_addresses: list=None):
    api_key = config.sendgrid['api_key']
    mailer = Sendgrid(api_key=api_key)

    email = mailer.send(to=to_addresses, sender=from_address, subject=subject, content=body_html)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(email)