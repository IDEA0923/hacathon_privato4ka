import os
import csv
import psycopg2
from datetime import datetime

# Берем те же переменные окружения, что и в проекте
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "db") # Измени на "db", если запускаешь внутри Docker-сети

def get_region_id(region_str):
    r = region_str.lower()
    if "все" in r:
        return 0  # Все регионы / Федеральный
    if "примор" in r or "владивосток" in r or "дальн" in r:
        return 25 # Приморский край (код 25)
    if "сочи" in r or "сириус" in r:
        return 23 # Краснодарский край
    return 0

def parse_and_load():
    conn_str = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASS} port=5432"
    try:
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        print("[+] Успешное подключение к PostgreSQL")
    except Exception as e:
        print(f"[-] Ошибка подключения: {e}")
        return

    csv_file = "olympiads_2026_2027.csv"
    if not os.path.exists(csv_file):
        print(f"[-] Файл {csv_file} не найден!")
        return

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        success_count = 0
        
        for row in reader:
            try:
                name_1 = row["название"].strip()
                date_start = datetime.strptime(row["дата_начала"].strip(), "%Y-%m-%d")
                date_end = datetime.strptime(row["дата_окончания"].strip(), "%Y-%m-%d")
                class_start = int(row["класс_от"])
                class_end = int(row["класс_до"])
                lvl = row["уровень"].strip()
                frm = row["источник"].strip()
                lnk = row["url"].strip()
                subjects = row["предметы"].strip()
                description_1 = row["описание"].strip()
                region = get_region_id(row["регион"].strip())

                query = """
                    INSERT INTO events (name_1, date_start, date_end, class_start, class_end, lvl, frm, lnk, subjects, description_1, region)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name_1, date_start, date_end, class_start, class_end, lvl, frm, lnk, subjects, description_1, region))
                conn.commit()  # <--- ВАЖНО: сохраняем каждую успешную строку сразу
                success_count += 1
                
            except Exception as e:
                conn.rollback()  # <--- ВАЖНО: сбрасываем ошибку транзакции, чтобы не сломать остальные
                print(f"[-] Настоящая ошибка в '{row.get('название')}': {e}")
        conn.commit()
        print(f"[+] Успешно загружено {success_count} олимпиад в таблицу 'events'.")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    parse_and_load()