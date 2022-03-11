# mail_sender_util
Utilitário para envio de e-mails por linha de comando.

Este utilitário foi desenvolvido por conta da necessidade de atualizar a versão do TLS utilizada pelo ERP Desktop.

Se optou pelo uso da linguagem Python, e pelo fornecimento de um executável, porque está sendo estudada a possibilidade de realizar novos desenvolvimentos do dektop já em python, para permitir reaproveitamento de código para o ERP 4 e/ou JobManager.

Obs.: Esta documentação pressupõe que o programador esteja utilizado ambiente Windows (visto que se destina à integração com o ERP Desktop).

## Ambiente de Desenvolvimento

Siga os passos abaixo para montar o ambiente de desenvolvimento (pré requisito: Python 3.9.5, ou superior, e VSCode instalados):

1. Clone o repositório:

> git clone git@github.com:Nasajon/mail_sender_util.git

2. Crie um ambiente virtual python local:

> python -m venv .venv

3. Iniciei o ambiente:

> .\.venv\Scripts\activate.bat

4. Instale as dependências do projeto:

> pip install -r requirements

5. Faça uma cópia do arquivo ```.env.dist```, renomeando para ```.env```

6. Configure a variável PYTHONPATH, contida no arquivo ```.env```, para apontar para a raiz do projeto

7. Rode o comando abaixo para testar o envio de e-mail (substituindo por uma conta GMail válida, e configurada para envio por meio de aplicativos com menor nível de segurança; o que é uma exigência do GMail para usar o protocolo SMTP; e substituindo o endereço de destino do e-mail):

> python mail_sender_util/mail_cmd.py -j "{\"user\": \"USUARIO\", \"password\": \"SENHA\", \"host\": \"smtp.gmail.com\", \"port\": \"465\", \"crypt_method\": \"ssl_tls\", \"tls_version\": \"v1.2\", \"emails\": [{\"assunto\": \"Teste 1\", \"remetente\": \"USUARIO\", \"destinatarios\": [\"DESTINATARIO\"], \"msg_html\": \"Teste 1\"}]}

## Entrada do Comando

Se optou pelo desenvolvimento de um utilitário que receba um JSON como parâmetro de entrada, contendo os seguintes padrão:

```json
{
    "user": "str", // Conta de e-mail para autenticação junto ao servidor (normalmente igual ao remetente dos e-mails)
    "password": "str", // Senha do e-mail para autenticação junto ao servidor
    "port": "str", // Porta SMTP do servidor de e-mails
    "crypt_method": "str", // Método de criptografia para o envio dos e-mails (opções: "null", "ssl_tls" ou "start_tls")
    "tls_version": "str", // Versão da criptografia TLS, caso utilizada (opções: "v1.0", "v1.1" ou "v1.2")
    "emails": [ // Lista de e-mails a enviar
        {
            "assunto": "str", // Assunto do e-mail
            "remetente": "str", // Endereço de e-mail do rementente
            "destinatários": [ // Lista dos endereços de e-mails dos destinatários
                "str",
                ...
            ],
            "dest_copia": [ // Lista dos endereços de e-mails dos destinatários em cópia
                "str",
                ...
            ],
            "dest_copia_oculta": [ // Lista dos endereços de e-mails dos destinatários em cópia oculta
                "str",
                ...
            ],
            "msg_html": "str", // Corpo do e-mail, opcionalmente em HTML
            "anexos": [ // Lista de anexos a enviar junto ao e-mail
                {
                    "file_name": "str", // Nome do anexo no e-mail
                    "path": "str" // Path do arquivo no disco local (utilizar "/" como separador de diretórios)
                },
                ...
            ],
            "imagens": [ // Lista de imagens a enviar inline no corpo do e-mail
                {
                    "id": "str", // ID da imagem, que pode ser referenciado por meio de uma tag IMG, com o padrão: <img src="cid:ID">
                    "path": "str" // Path da imagem no disco local (utilizar "/" como separador de diretórios)
                },
                ...
            ]
        },
        ...
    ]
}
```

**Obs. 1: O JSON é recebido como o parâmetro "-j", e deve ser enviado como um string codificada em Base64.**

**Obs. 2: A diferença entre as opções do atributo "crypt_method" é:**
* "null": Sem criptografia
* "ssl_tls": A comunicação é criptografada por inteiro (e não apenas o contéudo dos e-mails)
* "start_tls": A comunicação é criptografada apenas na parte do corpo dos e-mails.

Caso se use algum tipo de criptografia, será necessário utilizar também a propriedade "tls_version".

## Saída do Comando

O comando retorna um status inteiro conforme os padrões a seguir:

* 0 em caso de sucesso
* 1 em caso de erro conhecido
  * _Neste caso, a saída do comando também contém um JSON descrevendo os erros ocorridos._
* 2 (ou outro) em caso de erro desconhecido

No caso de erro conhecido, o JSON de erros segue o padrão abaixo:

```json
{
    "erros_gerais": [ // Lista de mensagens de erros gerais ocorridos (erros de conexão e etc, e não erros de qualquer mensagem em particular)
        "str",
        ...
    ],
    "erros_mensagens": { // Objeto JSON com os erros das mensagens, onde as chaves do JSON correspondem ao índice de cada mensagem no vetor de entrada (isto é, o primeiro e-mail da entrada, terá seus erros descritos na chave "0", por exemplo)
        "0": [ // Lista de mensagens de erros ocorridos em cada mensagem (exemplo: endereço do remetente desconhecido)
            "str",
            ...
        ],
        ...
    }
}
```

## Empacotando num Executável

O PyInstaller é a ferramenta utilizada para empactar este utilitário num executável stand alone (que pode ser usado sem instalação do Python na máquina cliente).

Para gerar o exe, rode o comando:

> run-pyinstaller.bat

## Wrapper Delphi

Adicionalmente ao comando, foi desenvolvido um utilitário do tipo wrapper, para uso do mesmo por meio de sistemas Delphi.

Este utilitário está [versionado aqui.](https://github.com/Nasajon/erp-utils/blob/master/mail_sender)

Um exemplo de utilização:

```pascal

  var t_email: TMail;
  var t_listaEmails: TObjectList<TMail>;
  var t_anexo: TMailAnexo;
  var t_mailSender: TMailSenderWrapper;

begin
  t_listaEmails := nil;
  t_mailSender := nil;
  try
    t_listaEmails := TObjectList<TMail>.Create();

    t_email := TMail.Create();
    t_email.assunto := 'Teste Assunto';
    t_email.remetente := 'ana@nasajon.com.br';
    t_email.destinatarios.Add('sergiosilva@nasajon.com.br');
    t_email.msgHtml := 'Corpo do e-mail';

    t_anexo := TMailAnexo.Create();
    t_anexo.nomeArquivo := 'anexo.pdf';
    t_anexo.path := 'C:/Users/Sergio Silva/Downloads/Transformational Leadership.pdf';
    t_email.anexos.Add(t_anexo);

    t_listaEmails.Add(t_email);

    t_mailSender := TMailSenderWrapper.Create(
      'ana@nasajon.com.br',
      '**********',
      'smtp.gmail.com',
      '465',
      'ssl_tls',
      'v1.2'
    );
    t_mailSender.enviar(t_listaEmails);
  finally
    if Assigned(t_listaEmails) then t_listaEmails.Free;
    if Assigned(t_mailSender) then t_mailSender.Free;
  end;
end;
```

**Para correto funcionamento do wrapper, é preciso garantir que o executável "mail_cmd.exe" esteja contido no diretório ```nsbin```. O qual pode ser [encontrado aqui.](https://github.com/Nasajon/mail_sender_util/releases/tag/v0.0.1)**

### Retorno de erros

Caso ocorra um erro no envio, o método "enviar" lança uma exceção do tipo "mail_sender_wrapper.TMailException", e para acessar as informações de erro (conforme apresentadas no JSON de retorno acima), é preciso se utiliza das propriedades "errosGerais" e "errosEmails" do objeto correspondente à exception.

## Logs

O envio de e-mails registra logs, na tabela ```mail_sender_util``` do schema ```logs```.
