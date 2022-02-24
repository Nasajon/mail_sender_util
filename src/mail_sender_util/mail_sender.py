import enum
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mail_sender_util.exception import TLSVersionMissingExcpetion
from smtplib import SMTP, SMTP_SSL
from typing import Any, Dict, List, Tuple


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
        dest_copia: List[str] = None,
        dest_copia_oculta: List[str] = None,
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

        # Convertendo os parâmetros num Dict
        mail = {
            'assunto': assunto,
            'remetente': remetente,
            'destinatarios': destinatarios,
            'msg_html': msg_html
        }

        if dest_copia is not None:
            mail['dest_copia'] = dest_copia,

        if dest_copia_oculta is not None:
            mail['dest_copia_oculta'] = dest_copia_oculta,

        if images is not None:
            image_list = []

            for imagem in images:
                img = {
                    'id': imagem[0],
                    'path': imagem[1]
                }
                image_list.append(img)

            mail['images'] = image_list

        if anexos is not None:
            anexo_list = []

            for anexo in anexos:
                anx = {
                    'file_name': anexo[0],
                    'path': anexo[1]
                }
                anexo_list.append(anx)

            mail['anexos'] = anexo_list

        # Enviando
        self.enviar(
            [mail]
        )

    def enviar_lista(
        self,
        mail_msgs: List[Dict[str, Any]]
    ) -> None:
        """
        Método capaz de enviar uma lista de e-mails em formato HTML.

        o parâmetro "mail_msg" contém uma lista de dicionários, onde cada dicionário contém os parâmetros de um e-mail:
        :assunto: Assunto da mensagem a ser enviada por e-mail
        :remetente: Remetente da mensagem a ser enviada por e-mail
        :destinatarios: Lista de stings, representando os endereços dos destinatátios da mensagem
        :msg_html: Mensagem em formato html a ser enviada por e-mail
        :dest_copia: Lista de stings, representando os destinatátios em cópia, na mensagem
        :dest_copia_oculta: Lista de stings, representandoos  destinatátios em cópia oculta, na mensagem (não visíveis pelos destinatários diretos)
        :imagem: Lista de dicionários, representando as imagens a serem enviadas como partes do corpo da mensagem. Cada dicionário de imagem contém os parâmetros: "id", que representa o ID da imagem (referido no HTML, por uma tag img similar a: <img src="cid:image1">); e "path", que contém o path em disco da imagem.
        :anexos: Lista de dicionários, representanto os arquivos para anexar no e-mail. Cada dicionário contém os parâmetros: "file_name" com o nome do arquivo a ser exibido no e-mail; e "path", com o caminho em disco do anexo.
        """

        # Convertendo as mensagens
        msgs_multipart = []
        for mail_msg in mail_msgs:

            # Construindo o e-mail
            msg = MIMEMultipart()

            msg['From'] = mail_msg['remetente']
            msg['To'] = ', '.join(mail_msg['destinatarios'])
            msg['Subject'] = mail_msg['assunto']

            if 'dest_copia' in mail_msg:
                msg['Cc'] = ', '.join(mail_msg['dest_copia'])

            if 'dest_copia_oculta' in mail_msg:
                msg['Bcc'] = ', '.join(mail_msg['dest_copia_oculta'])

            msg.attach(MIMEText(mail_msg['msg_html'], 'html'))

            # Adicionando as imagens como partes MIME no mensagem de e-mail:
            # Onde o ID de cada parte é de acordo com a tupla da imagem, o caminho também
            if 'images' in mail_msg:
                for image in mail_msg['images']:
                    with open(image['path'], 'rb') as file:
                        msgImage = MIMEImage(file.read())

                    msgImage.add_header(
                        'Content-ID', '<{}>'.format(image['id']))
                    msg.attach(msgImage)

            # Adicionando os anexos como partes MIME na mensagem de e-mail:
            if 'anexos' in mail_msg:
                for anexo in mail_msg['anexos']:
                    msgAnexo = MIMEBase('application', 'octet-stream')

                    with open(anexo['path'], 'rb') as file:
                        msgAnexo.set_payload(file.read())

                    encoders.encode_base64(msgAnexo)
                    msgAnexo.add_header(
                        'Content-Disposition', "attachment; filename= {}".format(anexo['file_name']))
                    msg.attach(msgAnexo)

            msgs_multipart.append(msg)

        # Enviando o e-mail
        smtp_obj = None
        try:
            # Estabelecendo a conexão
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

            # Autenticando
            smtp_obj.login(self.smtp_user, self.smtp_pass)

            # Enviando as mensagens
            for msg in msgs_multipart:
                smtp_obj.send_message(msg)
        finally:
            # Finalizando a conexão
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

    # TODO Linha de comando
    # TODO Empacotamento

    mail1 = {
        'assunto': 'Teste 1',
        'remetente': 'ana@nasajon.com.br',
        'destinatarios': ['sergiosilva@nasajon.com.br'],
        'msg_html': 'Teste 1'
    }

    mail2 = {
        'assunto': 'Teste 3',
        'remetente': 'ana@nasajon.com.br',
        'destinatarios': ['sergiosilva@nasajon.com.br'],
        'msg_html': 'Teste 3',
        'dest_copia': ['sergio.confidencial@gmail.com'],
        'dest_copia_oculta': ['sergio.confidencial@outlook.com']
    }

    mails = [mail1, mail2]

    sender = GmailSender('ana@nasajon.com.br', '*********')
    sender.enviar_lista(mails)
