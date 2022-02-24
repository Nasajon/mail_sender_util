import argparse
import sys

from mail_sender_util.mail_sender import CryptMethod, MailSender, TLSVersion
from mail_sender_util.exception import MailSenderException, MissingParameter
from nsj_gcf_utils import json_util
from typing import Any, Dict


def validar_entrada(entrada: Dict[str, Any]):
    # Validando parâmetros de conexão
    pars = ['host', 'port', 'user', 'password', 'crypt_method', 'emails']
    for par in pars:
        if not par in entrada:
            raise MissingParameter(f'Faltando parâmetro: {par}')

    # Validando parâmetros das mensagens
    for email in entrada['emails']:
        pars = ['assunto', 'remetente', 'destinatarios', 'msg_html']
        for par in pars:
            if not par in email:
                raise MissingParameter(
                    f'Faltando parâmetro: {par}; no escopo do e-mail: {email}')


def enviar_emails(entrada: Dict[str, Any]):
    try:
        # Validando entrada
        validar_entrada(entrada)

        # Instanciando o MailsSneder
        sender = MailSender(
            entrada['host'],
            entrada['port'],
            entrada['user'],
            entrada['password'],
            CryptMethod(entrada.get('crypt_method')),
            TLSVersion(entrada.get('tls_version'))
        )

        # Enviando mensagem
        sender.enviar_lista(entrada['emails'])

        sys.exit(0)
    except MailSenderException as e:
        print(str(e))
        sys.exit(e.error_code)


def main():
    # Initialize parser
    parser = argparse.ArgumentParser(
        description="""
Utilitário para envio de e-mails por linha de comando.

Para uso, enviei um JSON contendo:
- 'user': Conta do usuário para atenticaçaõ inicial junto ao servidor de e-mail
- 'password': Senha do usuário para atenticaçaõ inicial junto ao servidor de e-mail
- 'host': Endereço do servidor de e-mail
- 'port': Porta de comunicação do servidor de e-mail
- 'crypt_method': Método de criptografia a ser usado. Opções: "null" (nenhuma), "ssl_tls" (SMTP criptografa desde o íncío da comunicação com o servidor) ou "start_tls" (SMTP criptografado apenas na altura das mensagens em si.)
- 'tls_version': Versão da criptografia TLS utilizada. Opções: "v1.0", "v1.2" e V1.2"
- 'emails': Lista de e-mails a serem evniados, onde cada e-mail é um dicionários, contendo:

Cada mesnagem deve conter:
- 'assunto': Assunto do e-mail
- 'remetente': Endereço de e-mail do remetente
- 'destinatarios': Lista com os endereços de e-mail dos destinatarios
- 'msg_html': String com o corpo do e-mail, em texto plano ou em formato HTML
- 'dest_copia': Lista com os endereços de e-mail dos destinatarios em cópia
- 'dest_copia_oculta': Lista com os endereços de e-mail dos destinatarios em cópia oculta
- 'imagens': Lista de dicionários, representando as imagens a serem enviadas como partes do corpo da mensagem. Cada dicionário de imagem contém os parâmetros: "id", que representa o ID da imagem (referido no HTML, por uma tag img similar a: <img src="cid:image1">); e "path", que contém o path em disco da imagem.
- 'anexos': Lista de dicionários, representanto os arquivos para anexar no e-mail. Cada dicionário contém os parâmetros: "file_name" com o nome do arquivo a ser exibido no e-mail; e "path", com o caminho em disco do anexo.

Sendo que os parâmetros "dest_copia", "dest_copia_oculta", "imagens" e "anexos" são todos opcionais.

Exemplode mensagem:
"{
    "usuario": "teste@teste.com",
    "senha": "123456",
    "remetente": "teste@teste.com",
    "destinatarios": ["teste2@teste.com"],
    "msg_html": "Conteúdo de teste <img src="cid:image1">",
    "imagens": [
        {
            "id": "image1",
            "path": "c:/..."
        }
    ],
    "anexos": [
        {
            "file_name": "teste.txt",
            "path": "c:/..."
        }
    ]
}"
""")

    # Adding optional argument
    parser.add_argument(
        "-j", "--json", help="JSON de entrada, com os parâmetros necessários ao envio do e-mail")

    # Read arguments from command line
    args = parser.parse_args()

    if args.json is not None:
        entrada = json_util.json_loads(args.json)
        enviar_emails(entrada)


if __name__ == '__main__':
    main()
