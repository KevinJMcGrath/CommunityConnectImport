import asyncio
import base64
import csv
import io
import logging


from aiohttp_sendgrid import Sendgrid
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
from sendgrid import SendGridAPIClient

import config

def send_email_async(from_address: str, to_addresses: list, subject: str, body_html: str,
                     cc_addresses: list=None, bcc_addresses: list=None):
    api_key = config.sendgrid['api_token']

    mailer = Sendgrid(api_key=api_key)

    email = mailer.send(to=to_addresses, sender=from_address, subject=subject, content=body_html)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(email)


def send_email(from_address: str, to_addresses: list, subject: str, body_html: str,
                     cc_addresses: list=None, bcc_addresses: list=None, attachment_list: list=None):
    api_key = config.sendgrid['api_token']

    sg = SendGridAPIClient(api_key=api_key)

    email = Mail(from_email=from_address,
                 to_emails=to_addresses,
                 subject=subject,
                 html_content=body_html)

    for e in cc_addresses:
        email.add_cc(e)

    for e in bcc_addresses:
        email.add_bcc(e)

    for att_tuple in attachment_list:
        filename = att_tuple[0]
        column_names = att_tuple[1]
        data = att_tuple[2]

        att = create_attachment_csv(filename, column_names, data)
        email.add_attachment(att)

    try:
        resp = sg.send(email)
    except Exception as ex:
        logging.exception(ex)


def create_attachment_csv(filename:str, headers: list, data: list):
    csv_buffer = io.StringIO()

    writer = csv.writer(csv_buffer, delimiter=",", lineterminator="\n")

    writer.writerow(headers)
    for row in data:
        writer.writerow(row)

    # Convert CSV data to base64 string required by SendGrid
    content_str = csv_buffer.getvalue()
    content_bytes = bytes(content_str, encoding='utf-8')
    content_64 = base64.b64encode(content_bytes).decode()

    att = Attachment()
    att.file_content = FileContent(content_64)
    att.file_type = FileType('text/csv')
    att.file_name = FileName(filename)
    att.disposition = Disposition('attachment')

    return att