import json

# Загружаем базу сокращений из файла
with open("abbreviations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Функция для поиска сокращений по запросу
def find_abbreviation(query):
    query = query.upper()  # Приводим введённый текст к верхнему регистру
    results = [item for item in data if item["abbr"].upper() == query]
    return results
