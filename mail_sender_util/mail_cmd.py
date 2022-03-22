import argparse
import base64
import sys

from mail_sender_util.mail_sender import CryptMethod, MailSender, TLSVersion
from mail_sender_util.exception import TLSVersionMissingExcpetion, ParametrosGeraisIncorretosException
from nsj_gcf_utils import json_util
from typing import Any, Dict, List


def formata_erros(erros_msg: Dict[int, List[str]]):
    erros = {}

    if -1 in erros_msg:
        erros['erros_gerais'] = erros_msg[-1]
        del erros_msg[-1]

    if len(erros_msg) > 0:
        erros['erros_mensagens'] = erros_msg

    return json_util.json_dumps(erros)


def validar_entrada(entrada: Dict[str, Any], erros_msg: Dict[int, List[str]]):
    # Validando parâmetros de conexão
    pars = ['host', 'port', 'user', 'password', 'crypt_method', 'emails']
    for par in pars:
        if not par in entrada:
            erros = erros_msg.setdefault(-1, [])
            erros.append(f'Faltando parâmetro: {par}')

    if 'crypt_method' in entrada:
        try:
            CryptMethod(entrada.get('crypt_method')),
        except Exception as e:
            erros = erros_msg.setdefault(-1, [])
            erros.append(
                f"Parâmetro crypt_method inválido: {entrada.get('crypt_method')}")

    if 'tls_version' in entrada:
        try:
            TLSVersion(entrada.get('tls_version'))
        except Exception as e:
            erros = erros_msg.setdefault(-1, [])
            erros.append(
                f"Parâmetro tls_version inválido: {entrada.get('tls_version')}")

    # Validando parâmetros das mensagens
    if not('emails' in entrada):
        return

    for i in range(0, len(entrada['emails'])):
        email = entrada['emails'][i]

        pars = ['assunto', 'remetente', 'destinatarios', 'msg_html']
        for par in pars:
            if not par in email:
                erros = erros_msg.setdefault(i, [])
                erros.append(
                    f'Faltando parâmetro: {par}')


def enviar_emails(entrada: Dict[str, Any]):
    erros_msg = {}
    try:
        # Validando entrada
        validar_entrada(entrada, erros_msg)

        if -1 in erros_msg:
            raise ParametrosGeraisIncorretosException()

        # Instanciando o MailsSneder
        tls_version = None
        if 'tls_version' in entrada:
            tls_version = TLSVersion(entrada.get('tls_version'))

        sender = MailSender(
            entrada['host'],
            entrada['port'],
            entrada['user'],
            entrada['password'],
            CryptMethod(entrada.get('crypt_method')),
            tls_version
        )

        # Enviando mensagem
        sender.enviar_lista(entrada['emails'], erros_msg)
    except ParametrosGeraisIncorretosException as e:
        # Basta suprimir, pois é impresso a seguir
        pass
    except TLSVersionMissingExcpetion as e:
        erros = erros_msg.setdefault(-1, [])
        erros.append(str(e))
    except Exception as e:
        erros = erros_msg.setdefault(-1, [])
        erros.append(
            f'Erro desconhecido ao enviar e-mails. Mensagem original do erro: {e}')

    if len(erros_msg) > 0:
        print(formata_erros(erros_msg))
        sys.exit(1)
    else:
        print('ok')
        sys.exit(0)


def internal_main(json: str):
    entrada = json_util.json_loads(json)
    enviar_emails(entrada)


def main():
    try:
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

Exemplo de mensagem:
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
            json = base64.b64decode(args.json).decode(encoding='ansi')
            internal_main(json)
    except Exception as e:
        print(f'Erro fatal não identificado. Mensagem original do erro {e}')
        sys.exit(5)


if __name__ == '__main__':
    main()
    # internal_main(
    #     '{\"password\":\"*********\",\"host\":\"smtp.gmail.com\",\"crypt_method\":\"ssl_tls\",\"user\":\"ana@nasajon.com.br\",\"port\":\"465\",\"emails\":[{\"destinatarios\":[\"sergiosilva@nasajon.com.br\"],\"imagens\":[],\"anexos\":[{\"path\":\"C:/Users/Sergio Silva/Downloads/Transformational Leadership.pdf\",\"file_name\":\"anexo.pdf\"}],\"remetente\":\"ana@nasajon.com.br\",\"assunto\":\"Teste Assunto\",\"msg_html\":\"Corpo do e-mail\"}],\"tls_version\":\"v1.2\"}')
