from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
# from typing import List, Tuple


class MailSender:

    # smtp_host: str
    # smtp_port: str
    # smtp_user: str
    # smtp_pass: str
    # smtpObj: SMTP_SSL

    def __init__(
        self,
        smtp_host: str,
        smtp_port: str,
        smtp_user: str,
        smtp_pass: str
    ):
        """

        Classe responsável por envio de e-mails via SMTP.



        Obs.: Esta classe somente suporta login via SSL (não TLS).

        Portanto, utilize a porta para SSL de seu servidor de e-mails.



        :smtp_host: Host para login via SMTP

        :smtp_port: Porta para login via SMTP

        :smtp_user: Usuário para login via SMTP

        :smtp_pass: Senha para login via SMTP

        """

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def enviar(
        self,
        assunto: str,
        remetente: str,
        destinatarios,
        msg_html: str,
        images = None,
        anexos = None
    ) -> None:
        """

        Método capaz de enviar um e-mail em formato HTML. Parâmetros a seguir:



        :assunto: Assunto da mensagem a ser enviada por e-mail

        :remetente: Remetente da mensagem a ser enviada por e-mail

        :destinatarios: Lista de destinatátios da mensagem

        :msg_html: Mensagem em formato html a ser enviada por e-mail

        :imagem: Lista de imagens a serem enviadas como partes do corpo da mensagem. Cada imagem é uma tupla, onde a primeira posição contem o ID da imagem (referido no HTML, por uma tag img similar a: <img src="cid:image1">), e a segunda posição contém o path em disco da imagem.

        :anexos: Lista de arquivos para anexar no e-mail. Cada anexo é uma tupla, onde a primeira posição contem o nome do arquivo a ser exibido no e-mail, e a segunda posição contém o path em disco do anexo.

        """

        # Construindo o e-mail
        msg = MIMEMultipart()

        msg['From'] = remetente
        msg['To'] = ', '.join(destinatarios)
        msg['Subject'] = assunto

        msg.attach(MIMEText(msg_html, 'html'))

        # Adicionando as imagens como partes MIME no mensagem de e-mail:
        # Onde o ID de cada parte é de acordo com a tupla da imagem, o caminho também
        if images != None:
            for image in images:
                with open(image[1], 'rb') as file:
                    msgImage = MIMEImage(file.read())

                msgImage.add_header('Content-ID', '<{}>'.format(image[0]))
                msg.attach(msgImage)

        # Adicionando os anexos como partes MIME na mensagem de e-mail:
        if anexos != None:
            for anexo in anexos:
                msgAnexo = MIMEBase('application', 'octet-stream')

                with open(anexo[1], 'rb') as file:
                    msgAnexo.set_payload(file.read())

                encoders.encode_base64(msgAnexo)
                msgAnexo.add_header(
                    'Content-Disposition', "attachment; filename= {}".format(anexo[0]))
                msg.attach(msgAnexo)

        # Enviando o e-mail
        # context = ssl.create_default_context()
        import ssl
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        
        with SMTP_SSL(self.smtp_host, self.smtp_port, context=ctx) as smtpObj:
        # with SMTP_SSL(self.smtp_host, self.smtp_port) as smtpObj:
            # smtpObj.starttls(context=ctx)
            smtpObj.login(self.smtp_user, self.smtp_pass)
            smtpObj.send_message(msg)


class GmailSender(MailSender):

    def __init__(
        self,
        gmail_user: str,
        gmail_pass: str
    ):
        super().__init__('smtp.gmail.com', '465', gmail_user, gmail_pass)

if __name__ == '__main__':
    mail = MailSender('smtp.office365.com', '587', 'sergio.rocha.silva@outlook.com', 'S151625t#')
    mail.enviar('Teste', 'sergio.rocha.silva@outlook.com', ['sergiosilva@nasajon.com.br'], 'teste')