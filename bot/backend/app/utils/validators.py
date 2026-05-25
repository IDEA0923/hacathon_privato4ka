from email_validator import EmailNotValidError, validate_email


def normalize_email(raw: str) -> str:
    """Проверяет email и возвращает нормализованную форму.

    Бросает ``ValueError`` при невалидном вводе.
    """
    try:
        result = validate_email(raw, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc
    return result.normalized
