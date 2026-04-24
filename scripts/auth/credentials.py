"""
Gerenciamento de credenciais do SUAP via keyring do SO.

Usa o keyring nativo de cada plataforma:
  - macOS: Keychain
  - Windows: Credential Vault
  - Linux: Secret Service (GNOME Keyring / KWallet)

Nunca armazena senha em arquivo. Rodar setup_credentials.py uma vez por máquina.
"""

import keyring

_SERVICE = "suap.ifrn.edu.br"
_USER_KEY = "__current_user__"


def set_suap_credentials(username: str, password: str) -> None:
    """Salva usuário e senha no keyring do SO."""
    keyring.set_password(_SERVICE, _USER_KEY, username)
    keyring.set_password(_SERVICE, username, password)


def get_suap_credentials() -> tuple[str, str]:
    """
    Retorna (username, password) do keyring.

    Raises:
        RuntimeError: se as credenciais ainda não foram configuradas.
    """
    username = keyring.get_password(_SERVICE, _USER_KEY)
    if not username:
        raise RuntimeError(
            "Credenciais do SUAP não encontradas. "
            "Execute: python -m scripts.auth.setup_credentials"
        )
    password = keyring.get_password(_SERVICE, username)
    if not password:
        raise RuntimeError(
            f"Senha para '{username}' não encontrada no keyring. "
            "Execute: python -m scripts.auth.setup_credentials"
        )
    return username, password


def clear_suap_credentials() -> None:
    """Remove as credenciais do keyring."""
    username = keyring.get_password(_SERVICE, _USER_KEY)
    if username:
        keyring.delete_password(_SERVICE, username)
    keyring.delete_password(_SERVICE, _USER_KEY)
    print("Credenciais removidas do keyring.")
