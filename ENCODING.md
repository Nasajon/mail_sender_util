# Codificação por ramo e transição UTF-8

## Regra vigente

O ramo `v2.2601` deste repositório usa **Windows-1252 (WIN1252 / CP1252)** como padrão do ERP.

| Ramo oficial | Padrão do ERP |
| --- | --- |
| `master` | UTF-8 |
| `v2.2601`, quando existente | Windows-1252 (WIN1252 / CP1252) |
| `v2.2602`, quando existente | Windows-1252 (WIN1252 / CP1252) |

A transição para UTF-8 pertence ao master. Não migre as versões v2.2601/v2.2602 para UTF-8 por consequência de um cherry-pick ou merge. Windows-1252 não é sinônimo de ISO-8859-1 (Latin-1).

## Fontes, dados e fronteiras

- A regra orienta os fontes próprios Delphi, scripts SQL, textos do ERP e a codificação das conexões PostgreSQL (`client_encoding=UTF8` no master; `WIN1252` nas linhas legadas). Não confunda `client_encoding` com a codificação física do banco: mudar a sessão não converte dados já gravados nem repara texto corrompido.
- No master, novos fontes e scripts próprios devem seguir UTF-8; SQL deve ser UTF-8 **sem BOM**, inclusive quando concatenado pelos geradores. Em Delphi, respeite a sinalização UTF-8/BOM exigida pelo compilador e o formato de cada tipo de arquivo. Nas linhas legadas, mantenha fontes Delphi e SQL próprios em Windows-1252, sem introduzir BOM incompatível.
- Antes de editar, confira os bytes, o BOM e a leitura de acentos. ASCII puro não distingue as duas codificações; UTF-8 inválido, sozinho, não prova que um arquivo seja Windows-1252. Preserve arquivos legados/exceções identificadas até uma migração explícita e validada; não faça conversão em massa como efeito colateral de uma correção funcional.
- Nunca leia bytes com uma codificação e os regrave com outra por acidente. Não use substituição silenciosa por `?` ou `U+FFFD` nem faça round-trip UTF-8/1252 para "consertar depois". Verifique o diff e os caracteres após salvar.
- Fontes Python, Markdown e formatos com contrato próprio (por exemplo JSON/XML UTF-8, CNAB, SPED e arquivos de terceiros) **não devem ser convertidos indiscriminadamente para o padrão do ERP**. Preserve a especificação da linguagem, do protocolo ou do layout. Em interfaces legadas, explicite a codificação na fronteira e valide produtor e consumidor.
- Use ferramentas que permitam controlar a codificação sem destruir o original. Esta política não declara que todos os arquivos históricos já foram convertidos nem autoriza alterar layouts externos, dependências de terceiros ou dados reais sem relação com a tarefa.

## Cherry-picks, merges, rebases e backports

Antes de transportar uma alteração, identifique origem e destino. Um merge sem conflito não comprova compatibilidade de codificação.

1. **Master → versão legada:** adapte textos, leitura/escrita de arquivos, serialização, conversões e parâmetros de conexão a Windows-1252. Não leve guardas que exijam UTF-8 nem defaults UTF-8 para uma fronteira que continua legada. Caracteres não representáveis exigem decisão explícita; nunca os substitua silenciosamente.
2. **Versão legada → master:** mantenha UTF-8. Não reintroduza defaults ANSI/1252, conversões com perda ou a retirada de validações UTF-8. Reveja arquivos novos e trechos novos, não só os conflitos indicados pelo Git.
3. Revise manualmente conflitos e a documentação do destino; não resolva tudo com "ours"/"theirs". Preserve regras funcionais novas de ambos os lados, adaptadas ao contrato do ramo.
4. Toda alteração publicada em v2.2601 deve ter o conteúdo correspondente publicado também em v2.2602. Isso não autoriza criar ramos inexistentes nem exige retroportar alterações exclusivas de v2.2602.
5. Confira o diff final, codificação/BOM, dependências e conexões; compile e teste os fluxos atingidos quando houver alteração executável. Valide acentos e caracteres multibyte no master e dados representáveis nas versões legadas, inclusive no banco e nos arquivos quando aplicável.

A entrega precisa manter instalador, bibliotecas compartilhadas, executáveis e banco compatíveis. Não trate a simples mudança desta documentação como uma conversão de fontes, dados ou configurações já realizada.
