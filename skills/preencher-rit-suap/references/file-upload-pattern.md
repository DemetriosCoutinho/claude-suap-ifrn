# Upload de PDF — padrão para inputs escondidos (SUAP RIT)

## Por que o upload precisa de tratamento especial

Os inputs de arquivo `#id_arquivo_<secao>` no formulário RIT têm `display: none` — não são visíveis na página. Clicar normalmente via seletor CSS ou `browser_click` falha (elemento não interativo). A sequência correta usa `browser_evaluate` para disparar o click via JavaScript e depois `browser_file_upload` intercepta o diálogo do sistema.

## Mapeamento seção → input id

| Seção | Input ID | Arquivo consolidado |
|-------|---------|---------------------|
| aulas | `id_arquivo_aulas` | `_consolidados/aulas.pdf` (cópia de `_ref/disciplinas.pdf`) |
| apoio_ensino | `id_arquivo_apoio_ensino` | `_consolidados/apoio_ensino.pdf` |
| atendimento_orientacao | `id_arquivo_orientacao_alunos` | `_consolidados/atendimento_orientacao.pdf` |
| pesquisa | `id_arquivo_pesquisa` | `_consolidados/pesquisa.pdf` |
| gestao | `id_arquivo_gestao` | `_consolidados/gestao.pdf` |
| preparacao_ensino | `id_arquivo_preparacao_manutencao_ensino` | *(sem PDF — pular)* |
| projetos_ensino | `id_arquivo_programas_projetos_ensino` | *(sem PDF — pular)* |
| reunioes | `id_arquivo_reunioes` | *(sem PDF — pular)* |
| extensao | `id_arquivo_extensao` | *(sem PDF — pular)* |

(Fonte: `scripts/suap/.discovery/rit_form_schema.json` campo `mapeamento_secao_arquivo`)

## Sequência obrigatória

**Passo 1** — disparar o click via `browser_evaluate` (não via `browser_click`):

```javascript
// exemplo para apoio_ensino
const el = document.getElementById('id_arquivo_apoio_ensino');
el.scrollIntoView();
el.click();
```

**Passo 2** — imediatamente após o evaluate, chamar `browser_file_upload`:

```
browser_file_upload(paths=["<pasta_dados>/periodos/<periodo>/rit/_consolidados/apoio_ensino.pdf"])
```

O path deve ser **absoluto** (não relativo). O Playwright MCP intercepta o diálogo do sistema operacional que o `el.click()` abriu.

## Por que não funciona de outra forma

- `browser_click` em seletor CSS de elemento oculto: Playwright recusa — elemento não está visível.
- Setar `.value` do input diretamente via JS: bloqueado por segurança do browser (não é possível definir o path de um file input programaticamente por razões de sandbox).
- `browser_evaluate` com `el.click()` dispara o file chooser nativo do OS — aí sim o `browser_file_upload` pode interceptar.

## Verificar upload bem-sucedido

Após o `browser_file_upload`, checar que o nome do arquivo apareceu ao lado do input:

```javascript
// Se o SUAP mostra o nome do arquivo num label vizinho:
document.querySelector('[for="id_arquivo_apoio_ensino"]')?.nextElementSibling?.textContent
// ou verificar via snapshot que o nome do PDF aparece na tela
```

Alternativamente: `browser_snapshot` e verificar visualmente que o nome do arquivo aparece.
