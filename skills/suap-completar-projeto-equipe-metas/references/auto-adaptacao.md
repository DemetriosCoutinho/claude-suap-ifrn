# Auto-adaptação da skill — Fase 4

Ao final de cada execução real (Fase 3 concluída), a skill executa uma fase de auto-aprendizagem para não repetir descobertas na próxima invocação.

## Como executar

1. Comparar o que aconteceu na Fase 3 com o fluxo documentado no `SKILL.md`.
2. Preencher o template abaixo.
3. Apresentar ao usuário e aguardar: **"Aplico estas mudanças à skill? (sim/ajustes/não)"**.
4. Só após "sim": editar os arquivos listados.

## Template do plano de ajustes

```
## Aprendizados da execução {projeto_id} — {data}

### Divergências vs. fluxo documentado
- URL/campo X documentado como Y, mas o SUAP usou Z.
- Ordem de operação: esperava A antes de B, mas o SUAP exigiu B antes de A.
- Mapa `adicionar-aluno.json` não tinha o campo `...` — encontrado no DOM real.

### Descobertas novas (Playwright / SUAP)
- Mensagem de erro nova: "..." → causa: ... → ação: ...
- Endpoint AJAX alternativo encontrado: ...
- Campo opcional que o SUAP agora exige como obrigatório: ...

### Edições propostas

#### SKILL.md
- Seção "Armadilhas conhecidas": adicionar "..."
- Fase 3, passo N: substituir "X" por "Y" — motivo: ...

#### references/mapas/adicionar-aluno.json
- Adicionar campo `{"name": "...", "id": "...", "type": "..."}` — encontrado no DOM real.

#### references/validacoes-suap.md
- Nova linha na tabela: mensagem "..." / causa: ... / ação: ...

#### references/select2-ajax-suap.md
- Atualizar snippet `buscarPessoa` — parâmetro X mudou de comportamento.

**Aplicar? (sim/ajustes/não)**
```

## O que NÃO incluir no plano de ajustes

- Dados específicos do projeto (nomes, IDs de participação, CPFs) — esses ficam no report `_snapshot/fase-5-report-*.md`, não na skill.
- Regras de negócio do edital específico — ficam nos MDs do edital.
- Tudo que já estava documentado e funcionou conforme esperado.

## Princípio

A skill cresce com cada execução real. O usuário é o guardião do que entra — a skill propõe, o humano decide. Isso evita tanto o desperdício de redescobertas quanto a poluição da skill com casos de borda que não generalizam.
