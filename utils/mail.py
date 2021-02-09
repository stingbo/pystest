# coding = utf-8
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
# from email.utils import COMMASPACE
import smtplib
import os


class Mail(object):
    def __init__(self, config, email_attachment_path):
        """
        init config
        """
        self.attachment_path = email_attachment_path
        self.smtp = smtplib.SMTP()
        self.username = config.get('SMTP').get('username')
        self.password = config.get('SMTP').get('password')
        self.sender = config.get('SMTP').get('username')
        self.host = config.get('SMTP').get('host')
        self.port = config.get('SMTP').get('port')
        self.receiver = config.get('receiver')

    def connect(self):
        """
        connect server
        """
        self.smtp.connect(self.host, self.port)

    def login(self):
        """
        login email
        """
        try:
            self.smtp.login(self.username, self.password)
        except:
            raise AttributeError('Can not login smtp!!!')

    def send(self, email_title, email_content):
        """
        send email
        """
        msg = MIMEMultipart()  # create MIMEMultipart
        msg['From'] = self.sender  # sender
        msg['To'] = ', '.join(self.receiver)
        msg['Subject'] = email_title  # email Subject
        content = MIMEText(email_content, _charset='gbk')  # add email content  ,coding is gbk, becasue chinese exist
        msg.attach(content)

        for attachment_name in os.listdir(self.attachment_path):
            attachment_file = os.path.join(self.attachment_path, attachment_name)

            with open(attachment_file, 'rb') as attachment:
                if 'application' == 'text':
                    attachment = MIMEText(attachment.read(), _subtype='octet-stream', _charset='GB2312')
                elif 'application' == 'image':
                    attachment = MIMEImage(attachment.read(), _subtype='octet-stream')
                elif 'application' == 'audio':
                    attachment = MIMEAudio(attachment.read(), _subtype='octet-stream')
                else:
                    attachment = MIMEApplication(attachment.read(), _subtype='octet-stream')

            attachment.add_header('Content-Disposition', 'attachment', filename=('gbk', '', attachment_name))
            # make sure "attachment_name is chinese" right
            msg.attach(attachment)

        self.smtp.sendmail(self.sender, self.receiver, msg.as_string())  # format  msg.as_string()

    def quit(self):
        self.smtp.quit()