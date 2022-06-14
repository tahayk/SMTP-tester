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
# ---------- ---------- ----------


import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


if __name__ == "__main__":
    with SMTPClient() as s:
        msg = MIMEMultipart()
        msg['Subject'] = Header("Test", 'utf-8')
        msg['From'] = config("emailFrom")
        msg['To'] = "tahayk2@gmail.com"
        body = MIMEText("test message")
        msg.attach(body)
        try:
            s.sendmail(msg['FROM'], ["tahayk2@gmail.com"], msg.as_string().encode('ascii'))
        except Exception as e:
            print("!! email failed: "),
            print(e)
        print("email sent!")
