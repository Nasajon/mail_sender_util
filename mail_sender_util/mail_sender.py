import enum
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mail_sender_util.exception import TLSVersionMissingExcpetion
from smtplib import SMTP, SMTP_SSL, SMTPRecipientsRefused, SMTPSenderRefused
from typing import Any, Dict, List, Tuple


class CryptMethod(enum.Enum):
    NONE = 'null'
    SSL_OR_TLS = 'ssl_tls'
    START_TLS = 'start_tls'


class TLSVersion(enum.Enum):
    TLS_1_0 = 'v1.0'
    TLS_1_1 = 'v1.1'
    TLS_1_2 = 'v1.2'


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
            raise TLSVersionMissingExcpetion('Faltando parâmetro: tls_version')

    def enviar(
        self,
        erros_msgs: Dict[int, List[str]],
        assunto: str,
        remetente: str,
        destinatarios: List[str],
        msg_html: str,
        dest_copia: List[str] = None,
        dest_copia_oculta: List[str] = None,
        imagens: List[Tuple[str, str]] = None,
        anexos: List[Tuple[str, str]] = None
    ) -> None:
        """
        Método capaz de enviar um e-mail em formato HTML. Parâmetros a seguir:
        :assunto: Assunto da mensagem a ser enviada por e-mail
        :remetente: Remetente da mensagem a ser enviada por e-mail
        :destinatarios: Lista de destinatátios da mensagem
        :msg_html: Mensagem em formato html a ser enviada por e-mail
        :imagens: Lista de imagens a serem enviadas como partes do corpo da mensagem. Cada imagem é uma tupla, onde a primeira posição contem o ID da imagem (referido no HTML, por uma tag img similar a: <img src="cid:image1">), e a segunda posição contém o path em disco da imagem.
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

        if imagens is not None:
            image_list = []

            for imagem in imagens:
                img = {
                    'id': imagem[0],
                    'path': imagem[1]
                }
                image_list.append(img)

            mail['imagens'] = image_list

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
            [mail],
            erros_msgs
        )

    def enviar_lista(
        self,
        mail_msgs: List[Dict[str, Any]],
        erros_msgs: Dict[int, List[str]]
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
        :imagens: Lista de dicionários, representando as imagens a serem enviadas como partes do corpo da mensagem. Cada dicionário de imagem contém os parâmetros: "id", que representa o ID da imagem (referido no HTML, por uma tag img similar a: <img src="cid:image1">); e "path", que contém o path em disco da imagem.
        :anexos: Lista de dicionários, representanto os arquivos para anexar no e-mail. Cada dicionário contém os parâmetros: "file_name" com o nome do arquivo a ser exibido no e-mail; e "path", com o caminho em disco do anexo.
        """

        # Convertendo as mensagens
        msgs_multipart = {}
        for i in range(0, len(mail_msgs)):
            try:
                # Pulando a mensagem, se já foram identificados erros anteriores de composição da mesma
                if i in erros_msgs:
                    continue

                mail_msg = mail_msgs[i]

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
                if 'imagens' in mail_msg:
                    for image in mail_msg['imagens']:

                        try:
                            with open(image['path'], 'rb') as file:
                                msgImage = MIMEImage(file.read())
                        except FileNotFoundError as e:
                            erros = erros_msgs.setdefault(i, [])
                            erros.append(
                                f"Imagem não encontrada no caminho: {image['path']}. Mensagem original do erro: {e}")
                            continue
                        except Exception as e:
                            erros = erros_msgs.setdefault(i, [])
                            erros.append(
                                f"Erro de leitura da imagem no caminho: {image['path']}. Mensagem original do erro: {e}")
                            continue

                        msgImage.add_header(
                            'Content-ID', '<{}>'.format(image['id']))
                        msg.attach(msgImage)

                # Adicionando os anexos como partes MIME na mensagem de e-mail:
                if 'anexos' in mail_msg:
                    for anexo in mail_msg['anexos']:
                        msgAnexo = MIMEBase('application', 'octet-stream')

                        try:
                            with open(anexo['path'], 'rb') as file:
                                msgAnexo.set_payload(file.read())
                        except FileNotFoundError as e:
                            erros = erros_msgs.setdefault(i, [])
                            erros.append(
                                f"Anexo não encontrada no caminho: {anexo['path']}. Mensagem original do erro: {e}")
                            continue
                        except Exception as e:
                            erros = erros_msgs.setdefault(i, [])
                            erros.append(
                                f"Erro de leitura do anexo no caminho: {anexo['path']}. Mensagem original do erro: {e}")
                            continue

                        encoders.encode_base64(msgAnexo)
                        # msgAnexo.add_header(
                        #     'Content-Disposition', 'attachment', filename=('utf-8', 'pt-br', anexo['file_name']))
                        msgAnexo.add_header(
                            'Content-Disposition', "attachment; filename= {}".format(self._convert_filename_to_ascii(anexo['file_name'])))
                        msg.attach(msgAnexo)

                msgs_multipart[i] = msg
            except Exception as e:
                erros = erros_msgs.setdefault(i, [])
                erros.append(
                    f"Erro desconhecido no preparo da mensagem. Mensagem original do erro: {e}")

        # Resolvendo versão TLS
        tls_version = None
        if self.tls_version is not None:
            if self.tls_version == TLSVersion.TLS_1_0:
                tls_version = ssl.PROTOCOL_TLSv1
            elif self.tls_version == TLSVersion.TLS_1_1:
                tls_version = ssl.PROTOCOL_TLSv1_1
            elif self.tls_version == TLSVersion.TLS_1_2:
                tls_version = ssl.PROTOCOL_TLSv1_2
            else:
                erros = erros_msgs.setdefault(-1, [])
                erros.append(
                    f"Versão TLS não suportada ou identificada: {self.tls_version}")
                return

        ctx = None
        if self.tls_version is not None:
            ctx = ssl.SSLContext(tls_version)

        # Enviando os e-mails
        smtp_obj = None
        try:
            # Estabelecendo a conexão
            try:
                if self.crypt_method is not None and self.crypt_method == CryptMethod.SSL_OR_TLS:
                    smtp_obj = SMTP_SSL(host=self.smtp_host,
                                        port=self.smtp_port, context=ctx)
                else:
                    smtp_obj = SMTP(host=self.smtp_host,
                                    port=self.smtp_port)

                smtp_obj.ehlo()
                if self.crypt_method is not None and self.crypt_method == CryptMethod.START_TLS:
                    smtp_obj.starttls(context=ctx)
            except Exception as e:
                erros = erros_msgs.setdefault(-1, [])
                erros.append(
                    f"Erro estabelecendo conexão com o servidor. Verifique dados de conexão e criptografia. Mensagem original do erro: {e}")
                return

            # Autenticando
            try:
                smtp_obj.login(self.smtp_user, self.smtp_pass)
            except Exception as e:
                erros = erros_msgs.setdefault(-1, [])
                erros.append(
                    f"Erro de autenticação com o servidor de e-mail. Verifique o usuário e senha passados. Mensagem original do erro: {e}")
                return

            # Enviando as mensagens
            for i in msgs_multipart:
                msg = msgs_multipart[i]
                try:
                    # Pulando a mensagem, se já foram identificados erros anteriores de composição da mesma
                    if i in erros_msgs:
                        continue

                    # Enviando o e-mail de fato
                    smtp_obj.send_message(msg)
                except SMTPRecipientsRefused as e:
                    erros = erros_msgs.setdefault(i, [])
                    erros.append(
                        f"Um ou mais destinatário não identificados: {e.recipients}. Mensagem original do erro: {e}")
                    continue
                except SMTPSenderRefused as e:
                    erros = erros_msgs.setdefault(i, [])
                    erros.append(
                        f"Remetente não identificado: {msg['From']}. Mensagem original do erro: {e}")
                    continue
                except Exception as e:
                    erros = erros_msgs.setdefault(i, [])
                    erros.append(
                        f"Erro desconhecido ao enviar a mensagem. Verifique o remetente e os destinatários passados. Mensagem original do erro: {e}")
                    continue

        finally:
            # Finalizando a conexão
            if smtp_obj is not None:
                smtp_obj.quit()

    def _convert_filename_to_ascii(self, value: str) -> str:
        """
        Troca os caracteres especiais (não ascii), para caracteres equivalentes, e omite os demais.
        """

        import unicodedata
        retorno = unicodedata.normalize("NFD", value)
        retorno = retorno.encode("ascii", "ignore")
        retorno = retorno.decode("utf-8")

        if len(retorno) <= 0:
            raise Exception(f"File name cannot be converted to ascii: {value}")

        return retorno


class GmailSender(MailSender):

    def __init__(
        self,
        gmail_user: str,
        gmail_pass: str
    ):
        super().__init__('smtp.gmail.com', '465', gmail_user,
                         gmail_pass, CryptMethod.SSL_OR_TLS, TLSVersion.TLS_1_2)
