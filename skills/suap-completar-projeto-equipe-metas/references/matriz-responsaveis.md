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

## Aplicação ao projeto #9139

Derivado de §11 do PDF:

| Pessoa | Papel no plano | Potencial responsabilidade |
|--------|----------------|------------------------------|
| <Coordenador> (coordenador, servidor IFRN) | Coordenação | Metas 1, 2, 3 (gestão/doc) |
| Diego (servidor IFRN) | Líder Técnico | Metas 4, 5, 6 (técnicas) |
| Thiago (servidor IFRN) | Especialista Moodle | Meta 7 |
| Allan (servidor UFRN — **excluído por filtro**) | Especialista IA | — (não entra na Equipe SUAP) |
| Misael, Leão (servidores IFRN) | Back-end Sr. | Corresponsáveis metas 5, 6 |
| Erasmo (servidor IFRN) | Assistente Administrativo | Corresponsável metas 1, 3 |
| Adriyan (aluno IFRN) | Mobile Jr. | Corresponsável meta 4, 6 |
| Valeria (aluna IFRN) | Web Jr. | Corresponsável meta 4, 6 |
| Maria Alessandra (aluna IFRN) | Front-End Moodle | Corresponsável meta 7 |
| Maria Heloísa (aluna IFRN) | Dev Moodle | Corresponsável meta 7 |
| Caio (aluno IFRN) | Dev software | Corresponsável meta 6 |

**Nota sobre Allan**: ele é `Especialista em IA` mas UFRN. Como o filtro IFRN exclui-o da aba Equipe, a meta 4 (que seria ideal para ele) passa a ter Diego como responsável principal. Consequência: o projeto perde o atributo "atividade com especialista IA" no SUAP. Se isso for problema, reconsiderar o filtro ou cadastrar Allan manualmente como colaborador externo.

## Formato no MD de meta

```yaml
responsavel_principal: "Diego Vinicius Cirilo do Nascimento"
corresponsaveis:
  - "Adriyan Eryk de Oliveira Leite"
  - "Misael Barreto de Queiroz"
  - "Valeria Vitória de Queiroz Fraire"
```

O gerador de payload resolve cada nome para o ID do Select2 no dropdown de responsável (encontrado via busca por nome parcial no mapa da aba Objetivos). Se não resolver:

- Se for principal: fallback cascata.
- Se for corresponsável: pula e anota no report.
