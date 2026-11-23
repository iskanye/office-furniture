# Оптовая торговля офисной мебелью со склада

Учебная практика, РТУ МИРЭА, 2026 год.

**Студент:** Бикташев Искандер Ирикович.

**Группа:** ИКБО-10-24.

## Состав репозитория

Обе реализации хранятся в этом репозитории и обрабатывают одинаковые JSON-данные.

| Материалы | Расположение |
| --- | --- |
| Процедурная реализация на Python | [src/main.py](src/main.py) |
| Примеры и инструкция запуска Python | [src/README.md](src/README.md) |
| Объектно-ориентированная реализация на Java | [src/java/](src/java/) |
| Сборка, запуск и проверка Java | [src/java/README.md](src/java/README.md) |
| Тесты Java и контрольные сценарии | [src/java/tests/](src/java/tests/) |
| BPMN, модель данных, алгоритмы и UML | [models/](models/) |
| Статус взаимного рецензирования | [review/review.md](review/review.md) |
| Отчёт КТ1 и КТ2 | [Отчет_ИКБО-10-24_БикташевИИ.docx](Отчет_ИКБО-10-24_БикташевИИ.docx) |
| Полный отчёт с разделом КТ3 | [Отчет_ИКБО-10-24_БикташевИИ_КТ3.docx](Отчет_ИКБО-10-24_БикташевИИ_КТ3.docx) |

## Быстрый запуск

Команды выполняются из корня репозитория. Для Python нужен Python 3.10+,
для Java — JDK 21+; внешние библиотеки не требуются.

Python:

```sh
python3 src/main.py src/example.json
python3 src/main.py src/example_cancel.json
```

Java:

```sh
mkdir -p src/java/out
javac --release 21 -encoding UTF-8 -Xlint:all -d src/java/out src/java/*.java
java -cp src/java/out Main src/java/example.json
java -cp src/java/out Main src/java/example_cancel.json
```

Первый пример резервирует заявку R1 на 33500.00 руб.; второй отменяет заявку
и освобождает два резерва. Проверка совпадения обеих реализаций на 31 сценарии:

```sh
python3 src/java/verify.py
```
