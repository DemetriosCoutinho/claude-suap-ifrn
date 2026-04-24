"""
Configura as credenciais do SUAP no keyring do SO.

Roda uma vez por máquina:
    python -m scripts.auth.setup_credentials

A senha nunca é escrita em disco; fica no keyring nativo do sistema operacional.
"""

import getpass
import sys

from scripts.auth.credentials import set_suap_credentials, get_suap_credentials


def main() -> None:
    print("=== Configuração de credenciais SUAP ===")
    print("Serviço: suap.ifrn.edu.br")
    print("As credenciais serão salvas no keyring do SO (nunca em arquivo).\n")

    # Verificar se já existe configuração
    try:
        existing_user, _ = get_suap_credentials()
        resposta = input(
            f"Credenciais já configuradas para '{existing_user}'. Sobrescrever? [s/N] "
        ).strip().lower()
        if resposta not in ("s", "sim", "y", "yes"):
            print("Operação cancelada.")
            sys.exit(0)
    except RuntimeError:
        pass  # Nenhuma configuração anterior — seguir normalmente

    username = input("Usuário SUAP (matrícula ou login): ").strip()
    if not username:
        print("Erro: usuário não pode ser vazio.")
        sys.exit(1)

    password = getpass.getpass("Senha SUAP: ")
    if not password:
        print("Erro: senha não pode ser vazia.")
        sys.exit(1)

    set_suap_credentials(username, password)

    # Verificação imediata
    saved_user, _ = get_suap_credentials()
    print(f"\nCredenciais salvas com sucesso para '{saved_user}'.")
    print("Para verificar: python -c \"from scripts.auth.credentials import get_suap_credentials; u,_ = get_suap_credentials(); print('OK:', u)\"")


if __name__ == "__main__":
    main()
