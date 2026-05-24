# Backend (C++)

Сюда положите исходники C++ сервера. Dockerfile собирает либо через CMake (если есть `CMakeLists.txt`), либо одним файлом `main.cpp`.

## Ожидаемые эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/profile` | Создать/обновить профиль школьника |
| `GET` | `/api/profile?user_id=` | Получить профиль |
| `GET` | `/api/recommendations?user_id=` | Список рекомендованных олимпиад |
| `GET` | `/api/explain?user_id=&olympiad_id=` | LLM-обоснование |
| `POST` | `/api/plan` | Добавить олимпиаду в план |
| `GET` | `/api/plan?user_id=` | Получить план с дедлайнами |
| `DELETE` | `/api/plan?user_id=&olympiad_id=` | Удалить из плана |
| `GET` | `/api/notifications?user_id=` | Ближайшие дедлайны |
| `GET` | `/api/regions` | Список регионов |
| `GET` | `/api/subjects` | Список предметов |

Сервер должен слушать `0.0.0.0:8080`.
