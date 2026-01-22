from rest_framework.exceptions import PermissionDenied, ErrorDetail

def deny_role(required_role: str) -> None:
    raise PermissionDenied(
        f"Apenas usuários do tipo {required_role} podem acessar este endpoint."
    )

def _stringify_error_detail(value) -> str:
    """
    Converte ErrorDetail/dict/list do DRF em uma mensagem curta e legível.
    Não vaza estrutura interna no campo message.
    """
    if value is None:
        return "Autenticação necessária."

    # ErrorDetail -> texto
    if isinstance(value, ErrorDetail):
        return str(value)

    # dict (SimpleJWT costuma vir assim)
    if isinstance(value, dict):
        # padrão do SimpleJWT: pode ter "messages" com lista de dicts
        msgs = value.get("messages")
        if isinstance(msgs, list) and msgs:
            first = msgs[0]
            if isinstance(first, dict) and "message" in first:
                return str(first["message"])

        # fallback comum: "detail"
        if "detail" in value:
            return _stringify_error_detail(value["detail"])

        return "Token inválido."

    # lista (ex.: lista de erros)
    if isinstance(value, list) and value:
        return _stringify_error_detail(value[0])

    return str(value)
