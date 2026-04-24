# claude-suap-ifrn

Plugin Claude Code para automatizar workflows do SUAP no IFRN.

## O que é

Um conjunto de skills e scripts que ajudam docentes do IFRN a automatizar tarefas repetitivas no SUAP:

- Preenchimento do **RIT** (Relatório Individual de Trabalho) via Playwright
- Cadastro de **projetos de pesquisa** em editais PROPI
- Complemento de **equipe e metas** de projetos já cadastrados

O plugin é **stateless quanto a dados pessoais**: cada skill pergunta onde ficam seus arquivos antes de qualquer operação.

## Requisitos

- [Claude Code](https://claude.ai/code)
- Python 3.11+ com [`uv`](https://github.com/astral-sh/uv)
- Conta ativa no SUAP-IFRN (`https://suap.ifrn.edu.br`)

## Instalação

```bash
# Via Claude Code (quando disponível no marketplace)
/plugin install demetriosamc/claude-suap-ifrn

# Local (desenvolvimento)
/plugin install ~/Projects/claude-suap-ifrn
```

Após instalar, configure as dependências:

```bash
uv pip install -r requirements.txt
uv run playwright install chromium
uv run python -m scripts.auth.setup_credentials  # uma vez por máquina
```

## Skills disponíveis

| Skill | Descrição |
|-------|-----------|
| `preencher-rit-suap` | Preenche o formulário RIT no SUAP com seus textos aprovados e PDFs de evidência |
| `suap-cadastrar-projeto-edital` | Cadastra projeto de pesquisa num edital aberto, do PDF ao rascunho salvo |
| `suap-completar-projeto-equipe-metas` | Preenche aba Equipe e Objetivos de projeto já cadastrado |

## Como usar

1. Abra o Claude Code em qualquer diretório.
2. Invoque uma skill (ex.: `/preencher-rit-suap`).
3. A skill perguntará onde ficam seus dados (ex.: `~/Documents/meus-dados-suap/`).
4. Siga o fluxo guiado — nenhuma ação irreversível acontece sem sua confirmação.

## Estrutura sugerida para seus dados

```
~/Documents/meus-dados-suap/
├── periodos/
│   └── AAAA.S/
│       └── rit/
│           ├── _redacao/    # 9 arquivos .md com seus textos aprovados
│           ├── _meta/       # manifesto.json
│           └── ensino/ pesquisa/ gestao/ orientacoes/
└── projeto_pesquisa/        # PDFs do Plano de Trabalho e edital
```

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

MIT © 2026 Demetrios Coutinho
