"""
Preenche o formulário RIT no SUAP usando os textos redigidos em _redacao/
e salva o rascunho (clica "Salvar", NÃO em "Enviar").

Requer:
- rit_form_schema.json gerado por discover_rit_form.py
- periodos/<periodo>/rit/_redacao/<NN>_<secao>.md com status: aprovado

Uso:
    # Com URL explícita:
    python -m scripts.suap.preencher_rit --periodo 2025.2 \\
        --url https://suap.ifrn.edu.br/pit_rit_v2/preencher_relatorio_individual_trabalho/<id-do-rit>/

    # Sem URL (descobre via listing_url do schema):
    python -m scripts.suap.preencher_rit --periodo 2025.2

Fluxo:
1. Verifica que todos os _redacao/*.md com status != "n/a" têm status = "aprovado".
2. Abre o navegador (headful por padrão).
3. Faz login se necessário.
4. Navega ao formulário.
5. Preenche cada campo.
6. Pausa — o usuário revisa visualmente no navegador.
7. Após ENTER: clica Salvar.
8. Salva PDF e texto dos campos em _submissao/.
9. Atualiza manifesto.json com status de submissão.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from scripts.auth.credentials import get_suap_credentials

PLUGIN_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = PLUGIN_DIR / "scripts" / "suap" / ".auth"
DISCOVERY_DIR = PLUGIN_DIR / "scripts" / "suap" / ".discovery"
SUAP_BASE = "https://suap.ifrn.edu.br"
LOGIN_URL = f"{SUAP_BASE}/accounts/login/"

# Ordem canônica de seções e arquivos correspondentes
SECOES = [
    ("aulas",                 "01_aulas.md"),
    ("preparacao_ensino",     "02_preparacao_ensino.md"),
    ("apoio_ensino",          "03_apoio_ensino.md"),
    ("projetos_ensino",       "04_projetos_ensino.md"),
    ("atendimento_orientacao","05_atendimento_orientacao.md"),
    ("reunioes",              "06_reunioes.md"),
    ("pesquisa",              "07_pesquisa.md"),
    ("extensao",              "08_extensao.md"),
    ("gestao",                "09_gestao.md"),
]


def parse_md(path: Path) -> dict:
    """Extrai frontmatter YAML e corpo de um arquivo markdown."""
    content = path.read_text(encoding="utf-8")
    meta = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import re as _re
            for line in parts[1].strip().splitlines():
                m = _re.match(r'^(\w+):\s*"?([^"]+)"?\s*$', line.strip())
                if m:
                    meta[m.group(1)] = m.group(2).strip()
            body = parts[2].strip()

    return {"meta": meta, "body": body}


def extrair_texto_corpo(md_path: Path) -> str:
    """Extrai apenas o texto do corpo do MD, sem as seções de análise."""
    parsed = parse_md(md_path)
    body = parsed["body"]
    # Remove seções de análise (## Referência, ## Comparação, ## Discrepâncias)
    lines = body.splitlines()
    resultado = []
    dentro_analise = False
    for line in lines:
        if line.startswith("## Referência") or line.startswith("## Comparação") or line.startswith("## Discrepâncias"):
            dentro_analise = True
        elif line.startswith("## ") and dentro_analise:
            dentro_analise = False  # Outra seção H2 que não seja análise
        if not dentro_analise:
            resultado.append(line)
    # Remove título H1 inicial (o SUAP já tem o label)
    texto = "\n".join(resultado).strip()
    # Remove primeira linha se for H1
    if texto.startswith("# "):
        texto = "\n".join(texto.splitlines()[1:]).strip()
    return texto


def verificar_aprovacao(periodo: str, data_dir: Path) -> list[dict]:
    """
    Verifica que todas as seções obrigatórias têm status 'aprovado'.
    Retorna lista de seções com texto para preencher.
    Aborta se alguma estiver pendente.
    """
    base = data_dir / "periodos" / periodo / "rit" / "_redacao"
    secoes_para_preencher = []
    problemas = []

    for secao, filename in SECOES:
        path = base / filename
        if not path.exists():
            problemas.append(f"  Arquivo não encontrado: {path}")
            continue

        parsed = parse_md(path)
        status = parsed["meta"].get("status", "").lower()
        tipo = parsed["meta"].get("tipo", "").lower()

        if tipo in ("nao_se_aplica", "n/a") or status == "n/a":
            # Seção não aplicável — usar texto mínimo
            texto = extrair_texto_corpo(path)
            secoes_para_preencher.append({
                "secao": secao,
                "filename": filename,
                "texto": texto,
                "status": "n/a",
            })
        elif status == "aprovado":
            texto = extrair_texto_corpo(path)
            secoes_para_preencher.append({
                "secao": secao,
                "filename": filename,
                "texto": texto,
                "status": "aprovado",
            })
        elif status == "rascunho":
            problemas.append(
                f"  [{secao}] Status '{status}' em {filename}. "
                "Altere para 'aprovado' no YAML após revisar."
            )
        else:
            problemas.append(f"  [{secao}] Status desconhecido: '{status}' em {filename}.")

    if problemas:
        print("\nERRO: Seções não aprovadas encontradas:")
        for p in problemas:
            print(p)
        print(
            "\nRevisão necessária: abra cada arquivo _redacao/*.md e altere "
            "o campo 'status: rascunho' para 'status: aprovado' no frontmatter YAML."
        )
        sys.exit(1)

    return secoes_para_preencher


def carregar_schema() -> dict:
    schema_path = DISCOVERY_DIR / "rit_form_schema.json"
    if not schema_path.exists():
        print(
            f"ERRO: Schema não encontrado em {schema_path}. "
            "Execute discover_rit_form.py primeiro."
        )
        sys.exit(1)
    return json.loads(schema_path.read_text(encoding="utf-8"))


def login(page, username: str, password: str) -> None:
    print(f"Navegando para login: {LOGIN_URL}")
    page.goto(LOGIN_URL, wait_until="networkidle")
    page.fill("#id_username", username)
    page.fill("#id_password", password)
    page.click('[type="submit"]')
    print("Aguardando login... (resolva 2FA/captcha se necessário)")
    try:
        page.wait_for_url(f"{SUAP_BASE}/**", timeout=60_000)
        print("Login bem-sucedido.")
    except PlaywrightTimeoutError:
        print("ERRO: Login não completado em 60 segundos.")
        sys.exit(1)


def descobrir_url_formulario(page, schema: dict, periodo: str) -> str:
    """
    Navega à listing_url do schema e tenta encontrar o link do formulário do período.
    Retorna a URL completa do formulário.
    """
    listing_url = schema.get("listing_url", "")
    if not listing_url:
        print("ERRO: listing_url não encontrada no schema. Use --url explicitamente.")
        sys.exit(1)

    listing_full = f"{SUAP_BASE}{listing_url}" if listing_url.startswith("/") else listing_url
    print(f"Buscando formulário do período {periodo} em: {listing_full}")
    page.goto(listing_full, wait_until="networkidle")

    # Tentar encontrar link com o período ou com "preencher"
    ano, sem = periodo.split(".")
    link = page.evaluate(f"""() => {{
        const links = document.querySelectorAll('a');
        for (const a of links) {{
            const href = a.href || '';
            const text = a.textContent.toLowerCase();
            if ((href.includes('preencher') || text.includes('preencher') || text.includes('editar')) &&
                (text.includes('{ano}') || text.includes('{periodo}') || href.includes('{periodo}'))) {{
                return a.href;
            }}
        }}
        return null;
    }}""")

    if not link:
        print(
            f"ERRO: Não foi possível encontrar o formulário do período {periodo} na listagem. "
            "Use --url com a URL completa do formulário."
        )
        sys.exit(1)

    print(f"Formulário encontrado: {link}")
    return link


def salvar_evidencias(page, periodo: str, form_url: str, secoes: list[dict], data_dir: Path) -> dict:
    """Salva PDF e texto dos campos preenchidos em _submissao/."""
    submissao_dir = data_dir / "periodos" / periodo / "rit" / "_submissao"
    submissao_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = submissao_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # PDF
    pdf_path = submissao_dir / f"form_salvo_{ts}.pdf"
    page.pdf(path=str(pdf_path), format="A4")
    print(f"\nPDF salvo: {pdf_path.relative_to(data_dir)}")

    # Screenshot final
    ss_path = screenshots_dir / f"pos_salvamento_{ts}.png"
    page.screenshot(path=str(ss_path), full_page=True)

    # Texto dos campos
    texto_path = submissao_dir / f"texto_salvo_{ts}.txt"
    linhas = [f"RIT {periodo} — salvo em {ts}\nURL: {form_url}\n\n"]
    for s in secoes:
        linhas.append(f"=== {s['secao'].upper()} ===\n{s['texto']}\n\n")
    texto_path.write_text("".join(linhas), encoding="utf-8")
    print(f"Texto salvo: {texto_path.relative_to(data_dir)}")

    return {
        "pdf": str(pdf_path.relative_to(RAIZ)),
        "texto": str(texto_path.relative_to(RAIZ)),
        "screenshot": str(ss_path.relative_to(RAIZ)),
        "timestamp": ts,
    }


def atualizar_manifesto(periodo: str, form_url: str, evidencias: dict, data_dir: Path) -> None:
    manifesto_path = data_dir / "periodos" / periodo / "rit" / "_meta" / "manifesto.json"
    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    manifesto["submissao"] = {
        "status": "salvo_como_rascunho",
        "data": evidencias["timestamp"],
        "url": form_url,
        "pdf": evidencias["pdf"],
        "texto": evidencias["texto"],
        "screenshot": evidencias["screenshot"],
        "observacoes": "Salvo via preencher_rit.py. NÃO enviado ao diretor.",
    }
    manifesto_path.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Manifesto atualizado: {manifesto_path.relative_to(data_dir)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preenche o formulário RIT no SUAP e salva rascunho."
    )
    parser.add_argument(
        "--periodo",
        required=True,
        help="Semestre no formato AAAA.S (ex.: 2025.2)",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="URL completa do formulário (opcional — descoberta automática via schema se omitido).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("."),
        help="Pasta raiz dos dados SUAP (onde fica periodos/). Default: diretório atual.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Rodar sem abrir janela (não recomendado — perde revisão visual).",
    )
    args = parser.parse_args()

    # 1. Verificar aprovação de todas as seções
    print(f"Verificando aprovação dos arquivos _redacao/ para o período {args.periodo}...")
    data_dir = args.data_dir.expanduser().resolve()
    secoes = verificar_aprovacao(args.periodo, data_dir)
    print(f"Todas as {len(secoes)} seções verificadas.\n")

    # 2. Carregar schema
    schema = carregar_schema()
    mapeamento = schema.get("mapeamento_secao_selector", {})
    salvar_btn = schema.get("salvar_button", {})

    if not mapeamento:
        print(
            "ERRO: Mapeamento de seletores vazio no schema. "
            "Execute discover_rit_form.py e revise manualmente."
        )
        sys.exit(1)

    # 3. Credenciais
    try:
        username, password = get_suap_credentials()
    except RuntimeError as e:
        print(f"ERRO: {e}")
        sys.exit(1)

    storage_state_path = AUTH_DIR / "storage_state.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context_kwargs: dict = {}
        if storage_state_path.exists():
            context_kwargs["storage_state"] = str(storage_state_path)
        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        # 4. Login se necessário
        page.goto(SUAP_BASE, wait_until="networkidle")
        if "login" in page.url or "accounts" in page.url:
            login(page, username, password)
            context.storage_state(path=str(storage_state_path))

        # 5. Navegar ao formulário
        form_url = args.url
        if not form_url:
            form_url = descobrir_url_formulario(page, schema, args.periodo)

        print(f"Navegando ao formulário: {form_url}")
        page.goto(form_url, wait_until="networkidle")

        if "login" in page.url:
            login(page, username, password)
            context.storage_state(path=str(storage_state_path))
            page.goto(form_url, wait_until="networkidle")

        # 6. Preencher campos
        print("\n=== PREENCHIMENTO DOS CAMPOS ===")
        secoes_preenchidas = []
        for item in secoes:
            secao = item["secao"]
            selector = mapeamento.get(secao)
            if not selector:
                print(f"  [{secao}] AVISO: seletor não mapeado — campo ignorado.")
                continue
            try:
                page.wait_for_selector(selector, timeout=5_000)
                page.fill(selector, item["texto"])
                print(f"  [{secao}] ✓ preenchido ({len(item['texto'])} chars)")
                secoes_preenchidas.append(item)
            except PlaywrightTimeoutError:
                print(f"  [{secao}] AVISO: seletor '{selector}' não encontrado na página. Pulando.")

        # 7. Pausa para revisão humana
        print(
            "\n" + "=" * 60 +
            "\nRevise os campos preenchidos no navegador." +
            "\nQuando estiver satisfeito, pressione ENTER para Salvar." +
            "\nPressione Ctrl+C para cancelar sem salvar." +
            "\n" + "=" * 60
        )
        try:
            input("\n[ENTER para Salvar / Ctrl+C para cancelar]: ")
        except KeyboardInterrupt:
            print("\nOperação cancelada. Nenhuma alteração foi salva no SUAP.")
            context.close()
            browser.close()
            sys.exit(0)

        # 8. Clicar em Salvar
        btn_selector = salvar_btn.get("selector") if salvar_btn else 'button:has-text("Salvar")'
        print(f"\nClicando em Salvar ({btn_selector})...")
        try:
            page.click(btn_selector, timeout=10_000)
            page.wait_for_load_state("networkidle", timeout=30_000)
            print("Formulário salvo com sucesso.")
        except PlaywrightTimeoutError:
            print(
                "AVISO: Timeout ao aguardar resposta do Salvar. "
                "Verifique manualmente se o formulário foi salvo."
            )

        # 9. Salvar evidências
        evidencias = salvar_evidencias(page, args.periodo, form_url, secoes_preenchidas, data_dir)
        atualizar_manifesto(args.periodo, form_url, evidencias, data_dir)

        context.close()
        browser.close()

    print(
        "\nPreenchimento concluído."
        "\nCheckpoint E: abra o PDF em _submissao/ e recarregue a página do SUAP para confirmar."
    )


if __name__ == "__main__":
    main()
