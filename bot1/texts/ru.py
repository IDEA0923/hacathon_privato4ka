WELCOME = (
    "Привет, {name}! 👋\n\n"
    "Я бот сервиса. Чтобы продолжить, мне нужно ваше согласие "
    "на использование базовых данных профиля Telegram "
    "(идентификатор, имя, username).\n\n"
    "Это нужно, чтобы создать вашу учётную запись."
)

CONSENT_BUTTON_AGREE = "✅ Согласен"
CONSENT_BUTTON_DECLINE = "❌ Отказаться"

CONSENT_ACCEPTED = (
    "Спасибо! Согласие зафиксировано.\n\n"
    "Если хотите, укажите email для связи — отправьте его сообщением. "
    "Или нажмите «Пропустить»."
)
CONSENT_DECLINED = (
    "Хорошо, без согласия мы не сможем продолжить. "
    "Если передумаете — отправьте /start."
)

EMAIL_SKIP_BUTTON = "Пропустить"
EMAIL_INVALID = "Это не похоже на корректный email. Попробуйте ещё раз или нажмите «Пропустить»."
EMAIL_SAVED = "Email сохранён: {email}\n\nГотово! Можно открыть веб-приложение."
EMAIL_SKIPPED = "Хорошо, пропускаем email.\n\nГотово! Можно открыть веб-приложение."

OPEN_WEBAPP_BUTTON = "🌐 Открыть веб-приложение"
WEBAPP_PLACEHOLDER_URL = "https://example.com"
ADD_SUBJECT_BUTTON = "➕ Добавить доп. предмет"

SUBJECT_MATH = "Математика"
SUBJECT_INFORMATICS = "Информатика"
SUBJECT_PHYSICS = "Физика"

PROFILE_SUBJECTS_PROMPT = (
    "Выберите предмет кнопкой или напишите его текстом.\n"
    "Например: math, physics или математика."
)
PROFILE_SUBJECTS_INVALID = (
    "Не получилось сохранить предметы. Отправьте хотя бы один предмет текстом."
)
PROFILE_CLASS_PROMPT = "Укажите класс числом, например: 10."
PROFILE_CLASS_INVALID = "Класс должен быть целым числом. Например: 10."
PROFILE_REGION_PROMPT = "Укажите регион: Moscow или Primorsky."
PROFILE_REGION_INVALID = "Регион должен быть одним из вариантов: Moscow или Primorsky."
PROFILE_SAVED = "Профиль сохранён."
EMAIL_PROMPT = (
    "Если хотите, укажите email для связи — отправьте его сообщением. "
    "Или нажмите «Пропустить»."
)
MAIN_MENU_READY = "Готово. В меню можно добавить ещё один предмет."
ADD_SUBJECT_PROMPT = "Выберите дополнительный предмет."
ADD_SUBJECT_ADDED = (
    "Предмет «{subject}» добавлен. Теперь я буду подбирать олимпиады "
    "по вашим предметам: {subjects}."
)
ADD_SUBJECT_EXISTS = "Предмет «{subject}» уже есть в вашем списке."
PROFILE_REQUIRED = "Сначала заполните профиль через /start."

UNKNOWN_COMMAND = "Не понимаю команду. Отправьте /start, чтобы начать."
