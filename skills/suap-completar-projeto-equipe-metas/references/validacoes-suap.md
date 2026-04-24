# Validações e erros conhecidos do SUAP

Erros encontrados na execução real do projeto #9139 (2026-04-20). O SUAP retorna HTTP 200 com o form renderizado novamente — não redireciona nem retorna 4xx. Sempre checar o DOM após submit.

## Como detectar erro de validação

```javascript
const err = document.querySelector('.alert, .errorlist');
if (err) {
  return { ok: false, mensagem: err.innerText.trim() };
}
// Sucesso: redireciona ou exibe mensagem de confirmação
```

## Erros encontrados

### Servidor sem grupo de pesquisa

**Mensagem exata**: `"O servidor não está vinculado a nenhum grupo de pesquisa."`

**Causa**: o servidor precisa estar associado a um grupo de pesquisa no SUAP antes de ser cadastrado como participante de qualquer projeto.

**Ação para o humano**: pedir ao servidor que acesse o SUAP → Pesquisa → Grupos de Pesquisa → solicitar inclusão em algum grupo ativo. Após inclusão, re-rodar o cadastro pontualmente para este servidor.

**Comportamento da skill**: capturar erro, registrar no report sob "Rejeitados pelo SUAP — ação humana requerida", continuar com os demais membros. Substituir o servidor rejeitado nas atividades (se for corresponsável) por outro membro já cadastrado — anotar substituição no report.

---

### Aluno sem Lattes no SUAP

**Mensagem exata**: `"Não há currículo lattes registrado no SUAP. Oriente seu aluno a cadastrar seu currículo lattes na área de informações pessoais no SUAP."`

**Causa**: o campo Lattes na área "Informações Pessoais" do perfil do aluno no SUAP está em branco. Não se trata de ter ou não ter um currículo Lattes — é só o URL não estar cadastrado no SUAP.

**Ação para o humano**: pedir ao aluno que acesse o próprio SUAP → Informações Pessoais → adicionar URL do currículo Lattes (`http://lattes.cnpq.br/XXXX`). Após atualização, re-rodar o cadastro deste aluno pontualmente.

**Comportamento da skill**: mesmo que o MD do aluno tenha `lattes: null`, tentar o cadastro — o SUAP é que valida, não a skill. Capturar erro, registrar no report, continuar.

---

## Erros não encontrados mas esperados

| Situação | Comportamento provável |
|----------|----------------------|
| CPF não encontrado no Select2 | `items: []` na resposta AJAX — a skill deve tentar fallback por nome e registrar pendência se também falhar |
| Aluno já cadastrado no projeto | SUAP provavelmente exibe erro de unicidade — capturar e pular |
| Servidor já cadastrado | Idem |
| Meta com `ordem` duplicada | SUAP pode rejeitar — verificar se ele auto-incrementa ou exige unicidade |

## Fluxo de contingência para pessoas rejeitadas

1. Registrar no report: nome, tipo (aluno/servidor), mensagem de erro, ação necessária.
2. Não abortar a execução — continuar com os demais membros.
3. Para atividades onde a pessoa rejeitada era responsável/corresponsável: substituir pelo backup mais adequado (ex.: segundo servidor sênior), anotar substituição no report.
4. Ao final da Fase 3, a seção "Pendências humanas" do report lista cada pessoa rejeitada com a ação exata necessária para re-inclusão posterior.
