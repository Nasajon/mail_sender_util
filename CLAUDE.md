# CLAUDE.md

## Codificação e transição entre ramos

Neste ramo `v2.2602`, o padrão do ERP é **Windows-1252 (WIN1252 / CP1252)**. Consulte a [política de codificação](ENCODING.md) antes de editar ou transportar alterações. O `master` usa UTF-8; `v2.2601` e `v2.2602`, quando existentes, usam Windows-1252. Em cherry-picks, merges, rebases e backports, adapte ao ramo de destino: não copie cegamente conversões, defaults de conexão ou regras de BOM. Contratos explícitos de protocolos, linguagens e layouts externos continuam válidos.

Leia também [AGENTS.md](AGENTS.md); as demais regras do repositório continuam válidas.
