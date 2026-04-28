# Fase 5 — Pendências pós-salvamento (próxima skill/iteração)

Depois que a skill `suap-cadastrar-projeto-edital` salva o rascunho (final
da Fase 4), o SUAP mostra mensagens do tipo "Aguardando submissão de arquivos"
e lista o que ainda falta antes do projeto poder ser **enviado para avaliação**
pelo humano. **Esta skill atual não cobre nada disso** — cada item aqui é
uma iteração futura.

## Ponto de entrada

URL do projeto salvo na Rodada 1: `https://suap.ifrn.edu.br/pesquisa/projeto/<id-do-projeto>/`
(edital 02/2026). Ao abrir essa URL em modo de edição, o SUAP exibe:

- Abas: Detalhes, Equipe, Metas, Anexos, Plano de Aplicação, Histórico.
- Alertas vermelhos: pendências bloqueantes.
- Botões de ação: "Classificar TRL", "Enviar para Avaliação" (**este é o
  submit final — NUNCA clicar**), "Editar", "Salvar".

## Checklist das 5 pendências

### 1. Equipe (aba "Equipe")

Adicionar:
- **Bolsistas** (alunos): nome, matrícula, vínculo (IC/PIBITI/etc.), carga
  horária, função.
- **Servidores**: coordenador, líder técnico, especialistas. Buscar por CPF
  ou SIAPE.
- **Colaboradores externos** (TRI): nome, CPF, vínculo institucional, função.

Fonte: §11 do Plano de Trabalho (lista nominal de 16 pessoas no caso
edital 02/2026). Formato varia por edital — reler a seção "Equipe" do PDF
a cada rodada.

**Armadilha**: a aba Equipe costuma usar Select2 AJAX para buscar servidores.
Preenchimento por nome parcial → aguardar resultados → clicar. Se o servidor
não aparece, provável que não esteja cadastrado no SUAP (caso comum com
professores substitutos recentes); aí cabe contato administrativo prévio.

### 2. Metas (aba "Metas")

A aba está vazia após a Fase 4. Cadastrar uma linha por meta, com:
- Nome curto (META I, META II, ...).
- Descrição (reaproveitar texto do campo `acompanhamento_e_avaliacao`).
- Data início / data fim (dentro do intervalo do projeto).
- Entregáveis (lista de etapas/marcos).

Fonte: seção "Metas e Etapas" do PDF. Para edital 02/2026 o texto já está
em `21-acompanhamento-avaliacao.md` — formatado como META I a META VI.

**Possível extensão**: criar MDs `metas/01-meta-I.md` ... `metas/06-meta-VI.md`
com o mesmo padrão de revisão humana (`status: pendente|aprovado`).

### 3. Anexos (aba "Anexos")

Subir:
- O próprio PDF do Plano de Trabalho (obrigatório).
- Documentos adicionais exigidos pelo edital (variam a cada ano; ler o
  PDF do edital na Rodada 0).
- Cartas de anuência, declarações de parceria, etc.

**Armadilha**: o SUAP limita tamanho (verificar). Se PDF do Plano tiver >10MB,
pode precisar compactar.

### 4. Anuência da chefia imediata

Campo com seleção de servidor (Select2) + data limite (20/12/YYYY no caso
02/2026). A **assinatura** é feita depois, pelo próprio chefe, via login
separado no SUAP — esta skill só registra quem é.

### 5. Botão "Classificar TRL"

Apesar do campo `classificacao_trl` já ter sido preenchido na Fase 4, o SUAP
expõe um botão dedicado "Classificar TRL" na tela do projeto. Ao clicar, abre
um assistente com questionário guiado (sim/não). Resultado precisa bater com
o valor do campo (TRL 7 para o LMA).

**Atenção**: se a resposta do assistente divergir do campo, o SUAP pode
sobrescrever. Preencher o assistente com respostas que **reforcem** a
classificação escolhida, não que a contradigam.

## Ordem recomendada (quando virar skill)

1. **Classificar TRL** primeiro (rápido, ~2min, elimina alerta visível).
2. **Anuência da chefia** (só precisa nome — a assinatura fica pendente
   assíncrona).
3. **Equipe** (mais demorado por causa da busca Select2).
4. **Metas** (texto narrativo, pode reaproveitar do Plano).
5. **Anexos** por último (upload é o que mais pode falhar/timeouts).

## Regra inviolável (persistente da Fase 4)

**Nunca clicar em "Enviar para Avaliação"**. Esse é o botão de submissão
final — violação direta da CLAUDE.md §Regra 5. O envio é sempre feito pelo
usuário após revisão visual de todas as 5 pendências.

## Sugestão de estrutura para a skill Fase-5

```
.claude/skills/
├── suap-cadastrar-projeto-edital/        # esta skill (Fases 1–4)
└── suap-completar-projeto-edital/        # NOVA — Fase 5
    ├── SKILL.md
    └── references/
        ├── equipe.md
        ├── metas.md
        ├── anexos.md
        ├── anuencia.md
        └── classificar-trl.md
```

A skill Fase-5 receberia como parâmetro o `projeto_id` (p.ex. 9139) em vez do
`edital`, já que trabalha em cima de um projeto **já salvo**.
