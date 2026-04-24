# Distribuição das atividades entre as metas

## Regra

A skill gera **`total_atividades` atividades** (default `12`), cada uma com `duracao_atividade_dias` dias (default `30`), distribuídas entre as metas extraídas do PDF.

Critérios:

1. **Cadência temporal**: aproximadamente 1 atividade por mês ao longo do projeto. Se o projeto dura 12 meses, 12 atividades é o default natural.
2. **Fidelidade à natureza da meta**: distribuir o número de atividades por meta de acordo com o que o plano pede.
3. **Atividades concentradas quando necessário**: metas "pontuais" (ex.: "relatório final") ganham 1 atividade no mês certo. Metas contínuas ("entregas regulares de código") podem ganhar 1 sprint consolidada.

## Heurística de distribuição

Dado `total_atividades=12` e `N_metas` metas extraídas do PDF:

1. **Etapa A — categorização**: para cada meta, classificar em:
   - `periodica-trimestral` (ex.: relatórios trimestrais) → 1 atividade por trimestre do período da meta.
   - `pontual-final` (ex.: relatório final) → 1 atividade no último mês do período.
   - `pontual-inicio` (ex.: kickoff, documentação inicial) → 1 atividade no primeiro mês.
   - `contínua-bifásica` (ex.: expansão de cobertura em duas fases) → 2 atividades, uma no início e outra no meio.
   - `contínua-consolidada` (ex.: segurança, entregas de código) → 1 atividade no meio do período.
   - `composta` (ex.: documentação HIPAA que precisa iniciar e consolidar) → 2 atividades.

2. **Etapa B — orçamento de atividades**: soma das atividades por categoria. Se exceder `total_atividades`, priorizar `periodica-trimestral` (que tem lógica mais rígida), depois `composta`, depois demais.

3. **Etapa C — datas**: para cada atividade, fixar `inicio = dia 1 do mês escolhido` e `fim = inicio + 30 dias corridos`. Se o mês não comporta 30 dias úteis, tudo bem — são dias corridos.

## Exemplo aplicado ao projeto #9139

7 metas, projeto 12 meses (Nov/2025–Out/2026):

| Meta | Categoria | Qtd | Datas |
|------|-----------|-----|-------|
| 1. Relatórios trimestrais | periodica-trimestral | 4 | Jan, Abr, Jul, Out/26 |
| 2. Relatório final | pontual-final | 1 | Out/26 |
| 3. Documentação HIPAA | composta | 2 | Fev/26 e Ago/26 |
| 4. Cobertura expandida LMA | contínua-bifásica | 2 | Dez/25 e Mai/26 |
| 5. Segurança e eficiência | contínua-consolidada | 1 | Mar/26 |
| 6. Entregas regulares de código | contínua-consolidada | 1 | Jun/26 |
| 7. Trilha Moodle | contínua-consolidada | 1 | Set/26 |
| **Total** | | **12** | |

## Override manual

A matriz proposta fica em `00-matriz-atividades.md` com `status: pendente`. Se o usuário ajustar datas/quantidade/responsáveis lá, a Fase 3 respeita a matriz editada — **não recalcula**. Isso permite ajustes finos sem re-rodar Fase 2.

Condição para a skill prosseguir:
- `status: aprovado` no `00-matriz-atividades.md` **e** nos 7 `NN-meta-*.md`.
- Soma das atividades nas 7 metas = `total_atividades` (12 por default).

Se a soma divergir (usuário mudou quantidade sem atualizar matriz, ou vice-versa), a skill aborta com erro indicando qual meta descasou.

## Nota de execução — projeto #9139

A matriz 4+1+2+2+1+1+1 = 12 foi confirmada na execução real sem ajustes. Um ponto prático: quando pessoas são aprovadas depois (rodada extra pós-Fase 3), é possível adicioná-las como integrantes de atividades já criadas via `/pesquisa/editar_etapa/{etapa_id}/` — marcar os checkboxes de `integrantes` e re-submeter. Ver `references/submit-e-navegacao.md` para o snippet.

## Observação sobre sobreposições

Atividades de metas distintas podem cair no mesmo mês (ex.: Relatório trimestral Q4 + Relatório final, ambos em Out/26). Não é conflito — são entregas independentes. O SUAP aceita sem problemas.

## Título das atividades

O gerador produz títulos humanos claros:
- Para periódicas: `"Relatório trimestral Q{n} ({janela_meses})"`.
- Para pontuais: título da meta + sufixo (`"Relatório final do projeto"`, `"Auditoria de segurança + atualizações"`).
- Para bifásicas: sufixo `"(fase 1)"`, `"(fase 2)"`.
- Para compostas: prefixo `"Elaboração inicial de"` e `"Consolidação de"`.

Títulos não devem repetir exatamente o título da meta — o SUAP distingue meta (continer) da atividade (entrega).
