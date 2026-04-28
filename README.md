# claude-suap-ifrn

Plugin [Claude Code](https://claude.ai/code) para automatizar workflows do SUAP-IFRN — preenchimento de RIT, cadastro de projetos de pesquisa e complemento de equipe/metas.

> **Filosofia:** o plugin nunca assume onde ficam seus dados, nunca submete nada sem confirmação humana explícita, e para em "Salvar rascunho". A submissão final é sempre sua.

---

## Sumário

- [O que faz](#o-que-faz)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Setup inicial (uma vez por máquina)](#setup-inicial-uma-vez-por-máquina)
- [Skills disponíveis](#skills-disponíveis)
- [Estrutura de dados recomendada](#estrutura-de-dados-recomendada)
- [Como funciona por dentro](#como-funciona-por-dentro)
- [Contribuindo](#contribuindo)

---

## O que faz

| Skill | O que automatiza |
|-------|-----------------|
| `/preencher-rit-suap` | Preenche as 9 seções do formulário RIT no SUAP com seus textos aprovados e faz upload dos PDFs de evidência |
| `/suap-cadastrar-projeto-edital` | Lê o PDF do seu Plano de Trabalho e cadastra o projeto num edital PROPI aberto, do formulário ao rascunho salvo |
| `/suap-completar-projeto-equipe-metas` | Preenche a aba Equipe e Objetivos de um projeto já cadastrado |

Cada skill conduz um fluxo guiado: faz perguntas, mostra o que vai fazer antes de agir, e aguarda confirmação nas etapas críticas.

---

## Requisitos

- **Claude Code** — [claude.ai/code](https://claude.ai/code)
- **Python 3.11+** com [`uv`](https://github.com/astral-sh/uv) (`brew install uv` no macOS)
- **Conta ativa no SUAP-IFRN** — `https://suap.ifrn.edu.br`
- macOS (testado), Linux (deve funcionar), Windows (não testado)

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/DemetriosCoutinho/claude-suap-ifrn.git ~/Projects/claude-suap-ifrn
```

### 2. Registre como marketplace local no Claude Code

Dentro do Claude Code (qualquer diretório):

```
/plugin marketplace add ~/Projects/claude-suap-ifrn
/plugin install claude-suap-ifrn@claude-suap-ifrn-local
```

O plugin ficará disponível globalmente (scope `user`) em todas as sessões Claude Code.

---

## Setup inicial (uma vez por máquina)

### Dependências Python e Playwright

```bash
# Opção A — script idempotente (detecta o que falta e instala só isso)
bash ~/Projects/claude-suap-ifrn/scripts/bootstrap_deps.sh

# Opção B — manual
uv pip install -r ~/Projects/claude-suap-ifrn/requirements.txt
uv run playwright install chromium
```

### Credenciais SUAP

As credenciais ficam **apenas no keyring do sistema operacional** (Keychain no macOS). Nunca em arquivo de texto, nunca em variável de ambiente.

```bash
uv run python -m scripts.auth.setup_credentials
```

O script pedirá seu login e senha do SUAP interativamente. Repita somente se trocar a senha.

---

## Skills disponíveis

### `/preencher-rit-suap`

Preenche o Relatório Individual de Trabalho semestral.

**O que você precisa ter pronto:**
- 9 arquivos `.md` com os textos de cada eixo (ensino, pesquisa, gestão, orientações + subseções)
- PDFs de evidência organizados por eixo
- Um `manifesto.json` com metadados do período

**Fluxo:**
1. Skill pergunta a pasta base dos seus dados SUAP
2. Valida os arquivos antes de abrir o browser
3. Preenche seção por seção, fazendo upload dos PDFs
4. Para em "Salvar rascunho" — você revisa e submete

### `/suap-cadastrar-projeto-edital`

Cadastra um projeto de pesquisa num edital PROPI aberto.

**O que você precisa ter pronto:**
- PDF do Plano de Trabalho aprovado
- Número ou nome do edital aberto no SUAP

**Fluxo:**
1. Skill lê o PDF e extrai título, resumo, objetivos e palavras-chave
2. Confirma os dados extraídos com você antes de qualquer ação
3. Preenche o formulário do edital
4. Para antes de submeter

### `/suap-completar-projeto-equipe-metas`

Completa aba Equipe e Objetivos de projeto já cadastrado. Use logo após o cadastro inicial.

---

## Estrutura de dados recomendada

O plugin não exige esta estrutura, mas as skills foram pensadas com ela em mente:

```
~/Documents/meus-dados-suap/
├── periodos/
│   └── 2025.1/
│       └── rit/
│           ├── _meta/
│           │   └── manifesto.json      # { "periodo": "2025.1", "ch_total": 40, ... }
│           ├── _redacao/
│           │   ├── 01_ensino.md
│           │   ├── 02_pesquisa.md
│           │   ├── 03_gestao.md
│           │   └── ...                 # 9 arquivos no total
│           ├── ensino/
│           │   └── evidencia_aula.pdf
│           ├── pesquisa/
│           │   └── artigo_publicado.pdf
│           ├── gestao/
│           └── orientacoes/
└── projetos/
    └── meu-projeto-2025/
        ├── plano_de_trabalho.pdf
        └── edital_propi_ref.txt
```

---

## Como funciona por dentro

```
.claude-plugin/
├── plugin.json          # manifesto do plugin (nome, versão, autor)
└── marketplace.json     # permite instalação local via /plugin marketplace add

skills/
├── preencher-rit-suap/
├── suap-cadastrar-projeto-edital/
└── suap-completar-projeto-equipe-metas/

scripts/
├── auth/
│   ├── credentials.py        # único ponto de acesso ao keyring
│   └── setup_credentials.py  # wizard de configuração inicial
├── suap/
│   ├── .auth/
│   │   └── storage_state.json   # sessão autenticada do Playwright (criado no 1º login; gitignored)
│   └── .discovery/
│       └── rit_form_schema.json # schema do formulário RIT
├── pdf/                      # utilitários de leitura de PDF
└── bootstrap_deps.sh         # instalação idempotente de dependências

docs/
├── GLOSSARIO.md
└── CRITERIOS_VALIDACAO.md

CHECKLISTS/                   # templates de coleta, validação e revisão
```

**Regras invioláveis:**
- Credenciais: nunca em texto — somente `scripts/auth/credentials.py` acessa o keyring
- Dados pessoais: o plugin pergunta onde estão, nunca assume
- Submissão: sempre manual — o plugin para em "Salvar rascunho"
- Períodos: nunca misturados — semestre errado invalida o documento

---

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md).

**Ambiente de desenvolvimento:**

```bash
git clone https://github.com/DemetriosCoutinho/claude-suap-ifrn.git
cd claude-suap-ifrn
uv pip install -r requirements.txt
uv run playwright install chromium
```

Abra um Claude Code neste diretório — o `CLAUDE.md` explica as convenções do projeto.

---

## Licença

MIT © 2026 Demetrios Coutinho
