import re
from typing import Any, Dict

from core.exceptions import domain as domain_exceptions

BRAZILIAN_STATES = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}


def sanitize_digits(value: str) -> str:
    return re.sub(r"\D+", "", value)


def normalize_state(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        return normalized

    if normalized not in BRAZILIAN_STATES:
        raise domain_exceptions.ValidationError(
            "State must be a valid Brazilian UF abbreviation.",
            code="invalid_state",
            details={"state": "Informe uma sigla de estado brasileira válida (UF)."},
        )

    return normalized


def normalize_user_contact_address(data: Dict[str, Any], partial: bool) -> Dict[str, str]:
    normalized: Dict[str, str] = {}

    if partial:
        if "phone" in data:
            normalized["phone"] = sanitize_digits(data.get("phone", "") or "")
        if "zip_code" in data:
            normalized["zip_code"] = sanitize_digits(data.get("zip_code", "") or "")
        if "state" in data:
            normalized["state"] = normalize_state(data.get("state", "") or "")
        return normalized

    normalized["phone"] = sanitize_digits(data.get("phone", "") or "")
    normalized["zip_code"] = sanitize_digits(data.get("zip_code", "") or "")
    normalized["state"] = normalize_state(data.get("state", "") or "")
    return normalized
