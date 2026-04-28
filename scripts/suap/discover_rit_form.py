"""
Descobre a estrutura do formulário RIT no SUAP e gera um contrato de seletores.

Roda UMA ÚNICA VEZ (por layout de formulário). Depois de gerado, o
rit_form_schema.json é usado por preencher_rit.py indefinidamente.

Uso:
    python -m scripts.suap.discover_rit_form \\
        --url https://suap.ifrn.edu.br/pit_rit_v2/preencher_relatorio_individual_trabalho/<id-do-rit>/

O script:
1. Abre o navegador em modo headful (visível).
2. Faz login com as credenciais do keyring (usuário digita 2FA/captcha se necessário).
3. Navega à URL do formulário.
4. Mapeia os campos do formulário via JavaScript.
5. Salva:
   - scripts/suap/.discovery/rit_form_schema.json  (commitável — sem dados pessoais)
   - scripts/suap/.discovery/rit_form_raw.html      (gitignored — pode conter info pessoal)
   - scripts/suap/.discovery/screenshot.png         (para inspeção visual)
6. Salva a sessão em scripts/suap/.auth/storage_state.json (gitignored — reutilizada por preencher_rit.py).
"""

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from scripts.auth.credentials import get_suap_credentials

RAIZ = Path(__file__).resolve().parents[2]
AUTH_DIR = RAIZ / "scripts" / "suap" / ".auth"
DISCOVERY_DIR = RAIZ / "scripts" / "suap" / ".discovery"
SUAP_BASE = "https://suap.ifrn.edu.br"
LOGIN_URL = f"{SUAP_BASE}/accounts/login/"

# Mapeamento canônico: nome da seção → slug do arquivo de redação
SECOES_CONHECIDAS = [
    "aulas",
    "preparacao_ensino",
    "apoio_ensino",
    "projetos_ensino",
    "atendimento_orientacao",
    "reunioes",
    "pesquisa",
    "extensao",
    "gestao",
]

# Palavras-chave para identificar cada campo de texto no formulário do SUAP
KEYWORDS_SECAO = {
    "aulas": ["aulas", "relatos de aulas", "relato aulas"],
    "preparacao_ensino": ["preparação", "manutenção do ensino", "preparacao"],
    "apoio_ensino": ["apoio ao ensino"],
    "projetos_ensino": ["programas ou projetos", "projetos de ensino"],
    "atendimento_orientacao": ["atendimento", "orientação de alunos", "orientacao"],
    "reunioes": ["reuniões pedagógicas", "reunioes pedagogicas"],
    "pesquisa": ["pesquisa e inovação", "pesquisa e inovacao"],
    "extensao": ["extensão", "extensao"],
    "gestao": ["gestão e representação", "gestao"],
}


def login(page, username: str, password: str) -> None:
    """Faz login no SUAP. Aguarda resolução manual de 2FA/captcha se necessário."""
    print(f"Navegando para login: {LOGIN_URL}")
    page.goto(LOGIN_URL, wait_until="networkidle")

    # Preencher credenciais
    page.fill("#id_username", username)
    page.fill("#id_password", password)
    page.click('[type="submit"]')

    # Aguardar até 60s para o usuário resolver 2FA ou captcha
    print("Aguardando login... (resolva 2FA/captcha no navegador se necessário)")
    try:
        page.wait_for_url(f"{SUAP_BASE}/**", timeout=60_000)
        print("Login bem-sucedido.")
    except PlaywrightTimeoutError:
        print("ERRO: Login não completado em 60 segundos. Verifique credenciais ou captcha.")
        sys.exit(1)


def discover_fields(page) -> list[dict]:
    """
    Mapeia campos de texto (textarea/input) no formulário da página atual.
    Retorna lista de dicts com { label, selector, type, tab }.
    """
    campos = page.evaluate("""() => {
        const results = [];
        // Busca todos os textareas e inputs text no formulário
        const elements = document.querySelectorAll('textarea, input[type="text"]');
        elements.forEach((el, idx) => {
            const id = el.id || el.name || `__campo_${idx}`;
            const selector = el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : null);
            if (!selector) return;

            // Buscar label associado
            let labelText = '';
            const label = document.querySelector(`label[for="${el.id}"]`);
            if (label) {
                labelText = label.textContent.trim();
            } else {
                // Tenta label pai/irmão
                const parent = el.closest('.form-group, .field, fieldset, .form-row, .form-section');
                if (parent) {
                    const parentLabel = parent.querySelector('label, legend, h3, h4');
                    if (parentLabel) labelText = parentLabel.textContent.trim();
                }
            }

            // Detectar tab/accordion ativo
            let tabLabel = '';
            const tab = el.closest('.tab-pane, [role="tabpanel"], .accordion-collapse');
            if (tab) {
                const tabId = tab.id || tab.getAttribute('aria-labelledby');
                if (tabId) {
                    const tabBtn = document.querySelector(`[href="#${tabId}"], [data-bs-target="#${tabId}"], [aria-controls="${tabId}"]`);
                    if (tabBtn) tabLabel = tabBtn.textContent.trim();
                }
            }

            results.push({
                label: labelText,
                selector: selector,
                type: el.tagName.toLowerCase(),
                tab: tabLabel,
                id: id,
                value_preview: (el.value || el.textContent || '').substring(0, 80)
            });
        });
        return results;
    }""")
    return campos


def detect_save_button(page) -> dict | None:
    """Detecta o botão de Salvar no formulário."""
    btn_info = page.evaluate("""() => {
        const candidates = document.querySelectorAll('button, input[type="submit"], a.btn');
        for (const el of candidates) {
            const text = (el.textContent || el.value || '').toLowerCase().trim();
            if (text.includes('salvar') || text.includes('save') || text.includes('gravar')) {
                const selector = el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : null);
                return {
                    text: el.textContent.trim() || el.value,
                    selector: selector || 'button:has-text("Salvar")',
                    type: el.tagName.toLowerCase()
                };
            }
        }
        return null;
    }""")
    return btn_info


def detect_listing_url(form_url: str) -> str:
    """Deriva a URL de listagem a partir da URL do formulário."""
    # Ex.: /pit_rit_v2/preencher_relatorio_individual_trabalho/<id-do-rit>/ → /pit_rit_v2/
    parts = form_url.rstrip("/").split("/")
    # Remove ID numérico final e ação
    while parts and (parts[-1].isdigit() or not parts[-1]):
        parts.pop()
    if parts and parts[-1] in ("preencher_relatorio_individual_trabalho", "editar", "fill"):
        parts.pop()
    return "/".join(parts) + "/"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descobre a estrutura do formulário RIT no SUAP (rodar 1× por layout)."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL completa do formulário RIT (ex.: https://suap.ifrn.edu.br/pit_rit_v2/preencher_relatorio_individual_trabalho/<id-do-rit>/)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Rodar sem abrir janela do navegador (não recomendado para descoberta inicial).",
    )
    args = parser.parse_args()

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)

    storage_state_path = AUTH_DIR / "storage_state.json"

    try:
        username, password = get_suap_credentials()
    except RuntimeError as e:
        print(f"ERRO: {e}")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context_kwargs: dict = {}
        if storage_state_path.exists():
            print(f"Usando sessão salva em {storage_state_path}")
            context_kwargs["storage_state"] = str(storage_state_path)

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        # Verificar se a sessão está ativa
        page.goto(SUAP_BASE, wait_until="networkidle")
        if "login" in page.url or "accounts" in page.url:
            print("Sessão expirada ou inexistente. Fazendo login...")
            login(page, username, password)
            context.storage_state(path=str(storage_state_path))
            print(f"Sessão salva em {storage_state_path}")
        else:
            print("Sessão ativa reutilizada.")

        # Navegar ao formulário
        print(f"\nNavegando ao formulário: {args.url}")
        page.goto(args.url, wait_until="networkidle")

        if "login" in page.url:
            print("Redirecionado ao login novamente. Refazendo autenticação...")
            login(page, username, password)
            context.storage_state(path=str(storage_state_path))
            page.goto(args.url, wait_until="networkidle")

        # Capturar HTML e screenshot
        html_path = DISCOVERY_DIR / "rit_form_raw.html"
        html_path.write_text(page.content(), encoding="utf-8")
        print(f"HTML salvo em {html_path} (gitignored)")

        screenshot_path = DISCOVERY_DIR / "screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"Screenshot salvo em {screenshot_path}")

        # Mapear campos
        print("\nMapeando campos do formulário...")
        campos = discover_fields(page)
        salvar_btn = detect_save_button(page)
        listing_url = detect_listing_url(args.url)

        schema = {
            "form_url_base": args.url,
            "listing_url": listing_url,
            "salvar_button": salvar_btn,
            "total_campos_detectados": len(campos),
            "campos": campos,
            "mapeamento_secao_selector": {},
            "notas": (
                "Arquivo gerado automaticamente por discover_rit_form.py. "
                "Revisar 'mapeamento_secao_selector' manualmente antes de usar preencher_rit.py."
            ),
        }

        # Tentar mapear automaticamente cada seção por palavras-chave
        for secao, keywords in KEYWORDS_SECAO.items():
            for campo in campos:
                label_lower = campo["label"].lower()
                tab_lower = campo["tab"].lower()
                for kw in keywords:
                    if kw in label_lower or kw in tab_lower:
                        schema["mapeamento_secao_selector"][secao] = campo["selector"]
                        break
                if secao in schema["mapeamento_secao_selector"]:
                    break

        schema_path = DISCOVERY_DIR / "rit_form_schema.json"
        schema_path.write_text(
            json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nSchema salvo em {schema_path}")

        # Relatório
        print("\n=== RELATÓRIO DE DESCOBERTA ===")
        print(f"Campos detectados: {len(campos)}")
        print(f"Botão Salvar: {salvar_btn}")
        print(f"URL de listagem detectada: {listing_url}")
        print(f"\nMapeamento automático de seções:")
        for secao in SECOES_CONHECIDAS:
            selector = schema["mapeamento_secao_selector"].get(secao, "NÃO ENCONTRADO")
            print(f"  {secao:30s} → {selector}")

        mapeados = len(schema["mapeamento_secao_selector"])
        print(f"\n{mapeados}/{len(SECOES_CONHECIDAS)} seções mapeadas automaticamente.")
        if mapeados < len(SECOES_CONHECIDAS):
            print(
                "ATENÇÃO: Seções não mapeadas precisam de ajuste manual em "
                f"{schema_path}. Inspecione rit_form_raw.html e screenshot.png."
            )

        context.close()
        browser.close()

    print("\nDescoberta concluída.")
    print(f"Próximo passo: revisar {schema_path} e rodar preencher_rit.py")


if __name__ == "__main__":
    main()
