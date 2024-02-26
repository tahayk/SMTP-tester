# ---------- change this part ----------
To = "personal@gmail.com"
params = """
emailHost: 'smtp.eu.mailgun.org' # from SMTP settings section
emailPort: '587'
emailUser: 'openreplay@mycompany.com' # from SMTP credentials section
emailPassword: 'password' # the one copied when you created SMTP credentials
emailUseTls: 'true'
emailUseSsl: 'false'
emailSslKey: ''
emailSslCert: ''
emailFrom: 'openreplay@mycompany.com' # sender email, use your domain' 
"""
HTMLs = [
    "html/simple.html",
    "html/simple_with_image.html"
]
# ---------- ---------- ----------


import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from email.mime.image import MIMEImage
import base64
import re
import logging

_config = {}
for line in params.splitlines():
    if len(line) > 0:
        parts = line.split(':')
        if len(parts) != 2:
            continue
        vals = parts[1].split('\'')
        _config[parts[0]] = vals[1]

config = lambda key: _config[key]


class EmptySMTP:
    def sendmail(self, from_addr, to_addrs, msg, mail_options=(), rcpt_options=()):
        print("!! CANNOT SEND EMAIL, NO VALID SMTP CONFIGURATION FOUND")

    def send_message(self, msg):
        self.sendmail(msg["FROM"], msg["TO"], msg.as_string())


class SMTPClient:
    server = None

    def __init__(self):
        if config("emailHost") is None or len(config("emailHost")) == 0:
            return
        elif config("emailUseSsl").lower() == "false":
            self.server = smtplib.SMTP(host=config("emailHost"), port=int(config("emailPort")))
        else:
            if len(config("emailSslKey")) == 0 or len(config("emailSslCert")) == 0:
                self.server = smtplib.SMTP_SSL(host=config("emailHost"), port=int(config("emailPort")))
            else:
                self.server = smtplib.SMTP_SSL(host=config("emailHost"), port=int(config("emailPort")),
                                               keyfile=config("emailSslKey"), certfile=config("emailSslCert"))

    def __enter__(self):
        if self.server is None:
            return EmptySMTP()
        self.server.ehlo()
        if config("emailUseSsl").lower() == "false" and config("emailUseTls").lower() == "true":
            self.server.starttls()
            self.server.ehlo()
        self.server.login(user=config("emailUser"), password=config("emailPassword"))
        return self.server

    def __exit__(self, *args):
        if self.server is None:
            return
        self.server.quit()


def get_html_from_file(source):
    with open(source, "r") as body:
        BODY_HTML = body.read()

    return BODY_HTML


def replace_images(HTML):
    pattern_holder = re.compile(r'<img[\w\W\n]+?(src="[a-zA-Z0-9.+\/\\-]+")')
    pattern_src = re.compile(r'src="(.*?)"')
    mime_img = []
    swap = []
    for m in re.finditer(pattern_holder, HTML):
        sub = m.groups()[0]
        sub = str(re.findall(pattern_src, sub)[0])
        if sub not in swap:
            swap.append(sub)
            HTML = HTML.replace(sub, f"cid:img-{len(mime_img)}")
            sub = "html/" + sub
            with open(sub, "rb") as image_file:
                img = base64.b64encode(image_file.read()).decode('utf-8')
            mime_img.append(MIMEImage(base64.standard_b64decode(img)))
            mime_img[-1].add_header('Content-ID', f'<img-{len(mime_img) - 1}>')
    return HTML, mime_img


def send_html(BODY_HTML, SUBJECT, recipients):
    BODY_HTML, mime_img = replace_images(BODY_HTML)

    msg = MIMEMultipart()
    msg['Subject'] = Header(SUBJECT, 'utf-8')
    msg['From'] = config("emailFrom")
    msg['To'] = ""
    body = MIMEText(BODY_HTML.encode('utf-8'), 'html', "utf-8")
    msg.attach(body)
    for m in mime_img:
        msg.attach(m)

    with SMTPClient() as s:
        for r in recipients:
            msg.replace_header("To", r)
            r = [r]
            try:
                logging.info(f"Email sending to: {r}")
                s.send_message(msg)
            except Exception as e:
                logging.error("!!! Email error!")
                logging.error(e)


def send_text(recipients, text, subject):
    with SMTPClient() as s:
        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = config("emailFrom")
        msg['To'] = ", ".join(recipients)
        body = MIMEText(text)
        msg.attach(body)
        try:
            s.send_message(msg)
        except Exception as e:
            logging.error("!! Text-email failed: " + subject),
            logging.error(e)


if __name__ == "__main__":
    send_text(recipients=[To], text="a text email.", subject="Text email")
    logging.warning("Text email sent!")
    sleep(1)
    for f in HTMLs:
        send_html(BODY_HTML=get_html_from_file(f), SUBJECT=f'HTML email: {f}', recipients=[To])
        logging.warning(f"HTML email sent! {f}")
        sleep(1)
