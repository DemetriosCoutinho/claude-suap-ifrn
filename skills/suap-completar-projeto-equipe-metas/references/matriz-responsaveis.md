# Matriz papel-no-plano → responsável SUAP

## Princípio

Cada atividade precisa de um **responsável principal** (obrigatório) e pode ter **corresponsáveis** (opcional). A matriz é inferida do papel declarado na tabela §11 do Plano de Trabalho ("Líder Técnico", "Especialista em Moodle", "Dev Mobile", etc.).

Só pode entrar como responsável quem **já foi cadastrado na aba Equipe** (na Fase 3 da skill). Por isso: Fase 3 preenche Equipe primeiro, Metas depois. Se algum responsável escolhido falhar no cadastro de Equipe (ex.: servidor rejeitado como bolsista), há **fallback automático**.

## Mapeamento por tipo de meta

| Tipo de meta | Responsável principal preferido | Corresponsáveis preferidos |
|--------------|----------------------------------|----------------------------|
| Relatórios/gestão administrativa | Coordenador | Assistente Administrativo |
| Relatório final | Coordenador | Líder Técnico |
| Documentação/conformidade (HIPAA, LGPD) | Coordenador | Assistente Administrativo + Líder Técnico |
| Desenvolvimento técnico (back-end, mobile, web) | Líder Técnico | Devs das camadas envolvidas |
| Segurança/infra | Líder Técnico | Devs Back-end |
| IA/ML | Especialista em IA | Líder Técnico + Devs Mobile/Back |
| Capacitação/educação (Moodle) | Especialista em Moodle | Devs Front-End Moodle + Dev Moodle |

## Fallbacks

Ordem de preferência se o principal estiver indisponível (não cadastrado, rejeitado):

```
Coordenador → Líder Técnico → Especialista da área → primeiro corresponsável da lista
```

O gerador de payload registra a substituição como `responsavel_original` vs. `responsavel_aplicado` no report final, para o usuário saber o que mudou.

## Exemplo de aplicação (projeto genérico)

Derivado de §11 do PDF do usuário:

| Pessoa | Papel no plano | Potencial responsabilidade |
|--------|----------------|------------------------------|
| `<coordenador-1>` (coordenador, servidor IFRN) | Coordenação | Metas de gestão/documentação |
| `<servidor-1>` (servidor IFRN) | Líder Técnico | Metas técnicas principais |
| `<servidor-2>` (servidor IFRN) | Especialista na área | Metas da especialidade |
| `<servidor-externo>` (servidor outra instituição — **excluído por filtro**) | Colaborador | — (não entra na Equipe SUAP) |
| `<aluno-1>` (aluno IFRN) | Desenvolvimento | Corresponsável em metas técnicas |
| `<aluno-2>` (aluna IFRN) | Desenvolvimento | Corresponsável em metas técnicas |

**Nota sobre membros de outras instituições**: servidores de fora do IFRN são excluídos pelo filtro da aba Equipe. Se isso for problema, reconsiderar o filtro ou cadastrar como colaborador externo manualmente.

## Formato no MD de meta

```yaml
responsavel_principal: "<nome-completo-do-responsavel>"
corresponsaveis:
  - "<nome-completo-corresponsavel-1>"
  - "<nome-completo-corresponsavel-2>"
```

O gerador de payload resolve cada nome para o ID do Select2 no dropdown de responsável (encontrado via busca por nome parcial no mapa da aba Objetivos). Se não resolver:

- Se for principal: fallback cascata.
- Se for corresponsável: pula e anota no report.
