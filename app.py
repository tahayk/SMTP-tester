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
from time import sleep
from email.mime.image import MIMEImage
import base64

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


HTML_1 = """<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif; color: #6c757d">
<table width="100%" border="0" style="background-color: #f6f6f6">
    <tr>
        <td>
            <div style="border-radius: 3px; border-radius:4px; overflow: hidden; background-color: #ffffff; max-width: 600px; margin:20px auto;">
                <table style="margin:20px auto; border:1px solid transparent; border-collapse:collapse; background-color: #ffffff; max-width:600px"
                       width="100%">
                    <tr>
                        <td style="padding:10px 30px;">
                            a HTML email.
                        </td>
                    </tr>
                </table>
            </div>
        </td>
    </tr>
</table>
</body>
</html>
"""
HTML_2 = """<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif; color: #6c757d">
<table width="100%" border="0" style="background-color: #f6f6f6">
    <tr>
        <td>
            <div style="border-radius: 3px; border-radius:4px; overflow: hidden; background-color: #ffffff; max-width: 600px; margin:20px auto;">
                <table style="margin:20px auto; border:1px solid transparent; border-collapse:collapse; background-color: #ffffff; max-width:600px"
                       width="100%">
                    <!--Main Image-->
                    <tr>
                        <td style="padding:10px 30px;">
                            <center>
                                <img src="cid:img_0" alt="OpenReplay" width="100%" style="max-width: 120px;">
                            </center>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding-top: 30px">
                            a HTML email with attachment.
                        </td>
                    </tr>
                </table>
            </div>
        </td>
    </tr>
</table>
</body>
</html>
"""

if __name__ == "__main__":
    with SMTPClient() as s:
        msg = MIMEMultipart()
        msg['Subject'] = Header("Text email", 'utf-8')
        msg['From'] = config("emailFrom")
        msg['To'] = To
        body = MIMEText("a text email.")
        msg.attach(body)
        try:
            s.sendmail(msg['FROM'], [To], msg.as_string().encode('ascii'))
        except Exception as e:
            print("!! email failed: "),
            print(e)
        print("Text email sent!")

        sleep(1)
        msg = MIMEMultipart()
        msg['Subject'] = Header("HTML email", 'utf-8')
        msg['From'] = config("emailFrom")
        msg['To'] = To
        body = MIMEText(HTML_1.encode('utf-8'), 'html', "utf-8")
        msg.attach(body)
        try:
            s.sendmail(msg['FROM'], [To], msg.as_string().encode('ascii'))
        except Exception as e:
            print("!! HTML email failed: "),
            print(e)
        print("HTML email sent!")

        sleep(1)
        msg = MIMEMultipart()
        msg['Subject'] = Header("HTML-attachment email", 'utf-8')
        msg['From'] = config("emailFrom")
        msg['To'] = To
        body = MIMEText(HTML_2.encode('utf-8'), 'html', "utf-8")
        msg.attach(body)
        with open('./logo.png', "rb") as image_file:
            img = base64.b64encode(image_file.read()).decode('utf-8')
        img = MIMEImage(base64.standard_b64decode(img))
        img.add_header('Content-ID', f'<img_0>')
        msg.attach(img)
        try:
            s.sendmail(msg['FROM'], [To], msg.as_string().encode('ascii'))
        except Exception as e:
            print("!! HTML-attachment email failed: "),
            print(e)
        print("HTML-attachment email sent!")
