# Welcome to SUAP-IFRN Automation

## How We Use Claude

Based on Demetrios Coutinho's usage over the last 30 days:

Work Type Breakdown:
  Build Feature  ████████████████░░░░  80%
  Plan Design    ████░░░░░░░░░░░░░░░░  20%

Top Skills & Commands:
  `/preencher-rit-suap` · `/suap-cadastrar-projeto-edital` · `/suap-completar-projeto-equipe-metas`

Top MCP Servers:
  Playwright — automação de formulários SUAP via browser headless.

## Your Setup Checklist

### Codebases
- [ ] claude-suap-ifrn — https://github.com/DemetriosCoutinho/claude-suap-ifrn

### MCP Servers to Activate
- [ ] Playwright — browser automation para preencher formulários SUAP. Instalado via `uv run playwright install chromium` dentro do repo.

### Skills to Know About
- `/preencher-rit-suap` — preenche o formulário RIT no SUAP via Playwright (9 seções + PDFs). Use no início de cada semestre ao fechar o relatório.
- `/suap-cadastrar-projeto-edital` — cadastra projeto de pesquisa num edital PROPI aberto. Use quando um edital novo for publicado.
- `/suap-completar-projeto-equipe-metas` — completa a aba Equipe e Objetivos de um projeto já cadastrado. Use logo após o cadastro inicial.

## Team Tips

**Antes da primeira skill, faça estes passos uma única vez por máquina:**

1. **Instale as dependências Python**
   ```bash
   uv pip install -r requirements.txt
   uv run playwright install chromium
   ```
   Ou use o script idempotente do repo:
   ```bash
   bash scripts/bootstrap_deps.sh
   ```

2. **Grave suas credenciais SUAP no keyring do sistema** (nunca em arquivo de texto):
   ```bash
   uv run python -m scripts.auth.setup_credentials
   ```
   O script pedirá seu login e senha do SUAP e guardará no Keychain (macOS) ou equivalente. Só é necessário repetir se você trocar a senha.

3. **Instale o plugin em nível de usuário** (disponível em qualquer diretório):
   ```
   /plugin marketplace add /caminho/para/claude-suap-ifrn
   /plugin install claude-suap-ifrn@claude-suap-ifrn-local
   ```

**Durante o uso:**

- As skills **sempre perguntam** onde ficam seus dados — nenhum caminho fica hardcoded.
- O plugin **para em "Salvar rascunho"** — a submissão final é sempre manual no SUAP.
- Nunca misture períodos: o semestre errado invalida o documento inteiro.
- Sessões autenticadas ficam em `scripts/suap/.auth/storage_state.json` (gitignored) — delete o arquivo se quiser forçar novo login.

## Get Started

Clone o repo, siga os 3 passos de setup acima e invoque sua primeira skill:

```
/suap-cadastrar-projeto-edital
```

A skill guiará você pelo fluxo completo de cadastro em um edital PROPI — é um bom ponto de entrada por ser bem guiada e não modificar nada sem confirmação explícita.

