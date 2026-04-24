# Submit e navegação — lições práticas do Playwright

Descobertos na execução real do projeto #9139 (2026-04-20).

## Submit: usar JS, nunca `browser_click` com `ref`

Após qualquer `browser_evaluate` que muta o DOM, os `ref` do snapshot ficam desatualizados. Tentar `browser_click(ref=...)` após uma avaliação JS gera "element not found" ou clica no elemento errado.

**Padrão correto:**

```javascript
// Dentro do browser_evaluate — submit via JS direto
document.querySelector('input[type="submit"][name="participacaoaluno_form"]').click();
```

O `name=` do submit é sempre igual ao `formId` — ver `references/mapas/README.md` para a tabela completa.

**Por que funciona:** o `.click()` do JS não depende de ref do snapshot — opera diretamente no elemento do DOM corrente.

## Aguardar navegação após submit

Após `.click()`, o form faz POST e redireciona. Usar `browser_wait_for` para aguardar a URL mudar antes de continuar:

```
browser_wait_for: url diferente de /pesquisa/adicionar_participante_aluno/ por até 5000ms
```

Se a URL não mudar em 5s, houve erro de validação (200 + form renderizado novamente) — checar `.alert`/`.errorlist`.

## Descobrir IDs de meta após criação

Após criar cada meta via `/pesquisa/adicionar_meta/{projeto_id}/`, o SUAP redireciona para `/pesquisa/projeto/{projeto_id}/` (ou similar). Para obter o ID da meta criada, raspar os links da lista:

```javascript
const ids = Array.from(
  document.querySelectorAll('a[href*="adicionar_etapa"]')
).map(a => {
  const m = a.href.match(/adicionar_etapa\/(\d+)\//);
  return m ? m[1] : null;
}).filter(Boolean);
// ids = ["41878", "41879", "41880", ...] na ordem em que aparecem na página
```

Importante: os IDs aparecem na ordem de listagem da página — garantir que a ordem bate com a ordem de criação das metas (que segue o campo `ordem` preenchido).

## Descobrir ID de etapa (atividade) após criação

Similar ao acima, mas usando `a[href*="editar_etapa"]`:

```javascript
const ids = Array.from(
  document.querySelectorAll('a[href*="editar_etapa"]')
).map(a => {
  const m = a.href.match(/editar_etapa\/(\d+)\//);
  return m ? m[1] : null;
}).filter(Boolean);
```

Útil para re-editar etapas (adicionar integrantes que foram aprovados em rodada posterior).

## Editar etapa existente para adicionar integrantes

URL: `/pesquisa/editar_etapa/{etapa_id}/` — mesmo form `etapa_form`. Apenas marcar os checkboxes adicionais e re-submeter. Os checkboxes de integrantes têm `name="integrantes"` e `value="{ID_participacao}"` — o ID de participação (não o ID do usuário) é o que o SUAP usa internamente.

```javascript
// Marcar checkbox de integrante pelo valor do ID de participação
const cb = document.querySelector(`input[name="integrantes"][value="${idParticipacao}"]`);
if (cb && !cb.checked) cb.click();
```
