import enum
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL
from typing import List, Tuple

from matplotlib.style import context


class TLSVersionMissingExcpetion(Exception):
    pass


class CryptMethod(enum.Enum):
    NONE = 0
    SSL_OR_TLS = 1
    START_TLS = 2


class TLSVersion(enum.Enum):
    TLS_1_0 = ssl.PROTOCOL_TLSv1
    TLS_1_1 = ssl.PROTOCOL_TLSv1_1
    TLS_1_2 = ssl.PROTOCOL_TLSv1_2


class MailSender:

    smtp_host: str
    smtp_port: str
    smtp_user: str
    smtp_pass: str
    smtp_obj: SMTP
    crypt_method: CryptMethod
    tls_version: TLSVersion

    def __init__(
        self,
        smtp_host: str,
        smtp_port: str,
        smtp_user: str,
        smtp_pass: str,
        crypt_method: CryptMethod = None,
        tls_version: TLSVersion = None
    ):
        """
        Classe responsável por envio de e-mails via SMTP.

        Obs.: Esta classe somente suporta login via SSL (não TLS).

        Portanto, utilize a porta para SSL de seu servidor de e-mails.
        :smtp_host: Host para login via SMTP
        :smtp_port: Porta para login via SMTP
        :smtp_user: Usuário para login via SMTP
        :smtp_pass: Senha para login via SMTP
        :tls_version: Versão da criptografia TLS desejada
        """

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.crypt_method = crypt_method
        self.tls_version = tls_version

        if crypt_method is not None and crypt_method != CryptMethod.NONE and tls_version is None:
            raise TLSVersionMissingExcpetion()

    def enviar(
        self,
        assunto: str,
        remetente: str,
        destinatarios: List[str],
        msg_html: str,
        images: List[Tuple[str, str]] = None,
        anexos: List[Tuple[str, str]] = None
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
        smtp_obj = None
        try:
            ctx = None
            if self.tls_version is not None:
                ctx = ssl.SSLContext(self.tls_version.value)

            if self.crypt_method is not None and self.crypt_method == CryptMethod.SSL_OR_TLS:
                smtp_obj = SMTP_SSL(host=self.smtp_host,
                                    port=self.smtp_port, context=ctx)
            else:
                smtp_obj = SMTP(host=self.smtp_host,
                                port=self.smtp_port)

            smtp_obj.ehlo()
            if self.crypt_method is not None and self.crypt_method == CryptMethod.START_TLS:
                smtp_obj.starttls(context=ctx)
            smtp_obj.login(self.smtp_user, self.smtp_pass)
            smtp_obj.send_message(msg)
        finally:
            if smtp_obj is not None:
                smtp_obj.quit()


class GmailSender(MailSender):

    def __init__(
        self,
        gmail_user: str,
        gmail_pass: str
    ):
        super().__init__('smtp.gmail.com', '465', gmail_user,
                         gmail_pass, CryptMethod.SSL_OR_TLS, TLSVersion.TLS_1_2)


if __name__ == '__main__':
    # mail = MailSender('smtp.office365.com', '587',
    #                   'sergio.rocha.silva@outlook.com', '*******', CryptMethod.START_TLS, TLSVersion.TLS_1_2)
    # mail.enviar('Teste2', 'sergio.rocha.silva@outlook.com',
    #             ['sergiosilva@nasajon.com.br'], 'teste')

    # mail = GmailSender('ana@nasajon.com.br', '***********')
    # mail.enviar('Teste', 'ana@nasajon.com.br',
    #             ['sergiosilva@nasajon.com.br'], 'teste')

    # TODO Envio de múltiplos e-mails em uma única conexão
    # TODO Service JSON
    # TODO Linha de comando
    # TODO Empacotamento
