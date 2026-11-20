from pathlib import Path
from copy import deepcopy
import json,re
from collections import Counter
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK,WD_TAB_ALIGNMENT,WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
d=Document(ROOT/'Отчет_ИКБО-10-24_БикташевИИ.docx')
# Save the existing bibliography, then append the new section before it.
bib=next(p for p in d.paragraphs if p.text=='СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ')
body=d.element.body; children=list(body); idx=children.index(bib._p)
bibliography=[]
for e in children[idx:]:
 if e.tag!=qn('w:sectPr'):bibliography.append(deepcopy(e));body.remove(e)
# Targeted KT1/KT2 corrections preserve all unrelated content and the title page.
for p in d.paragraphs:
 if p.text.startswith('В качестве используемых технологий выбраны'):
  p.text='В качестве используемых технологий выбраны Python 3.13, Java 21 LTS (дистрибутив Eclipse Temurin от Eclipse Adoptium) и PostgreSQL 17. Temurin выбран как свободно доступная реализация OpenJDK для Windows, Linux и macOS с долгосрочной поддержкой Java 21 [30].'
 if p.text.startswith('Для разработки на Python и Java будет использоваться'):
  p.text='Для разработки на Python и Java выбран Visual Studio Code с расширениями Python и Extension Pack for Java. Одна среда позволяет редактировать обе версии, выполнять отладку, работать с Git и запускать команды javac во встроенном терминале. Это снижает число переключений между инструментами; для учебной консольной программы отдельная тяжёлая IDE не требуется. Поддержка Java описана в документации Microsoft [31]. Для воспроизводимости сборка выполняется из терминала и не зависит от редактора. PostgreSQL 17 выбран для будущего хранения товаров, заявок и резервов с внешними ключами и атомарной проверкой остатков [17].'
 if p.text.startswith('На рисунке 5.1 показан путь'):
  p.text='На рисунке 5.1 показан путь от получения заявки до заказа с резервом либо отказа. В пуле поставщика три дорожки: менеджер, система и склад; покупатель вынесен во внешний пул. Заявка, условия и ответ передаются потоками сообщений. После проверки заявки, проверки доступности и получения решения покупателя стоят исключающие шлюзы; «нет» является ветвью по умолчанию. Задача «Подтвердить условия заказа» означает получение и регистрацию подтверждения менеджером. Конечные события имеют толстый контур. Исходник импортирован в редактор bpmn-js проекта bpmn.io без предупреждений. Нотация соответствует BPMN 2.0.2 [24].'
 if p.text.startswith('Первая нормальная форма соблюдена:'):
  p.text += ' Атрибут agreed_total хранится как исторический факт: сумма, зафиксированная при согласовании конкретной заявки. Он зависит от ключа заявки и не является копией суммы по текущим ценам каталога. После изменения цены автоматический пересчёт этого атрибута исказил бы договорённость; вместо этого программа сравнивает новую сумму с согласованной и требует повторного согласования. Такое хранение не вводит транзитивной зависимости между неключевыми атрибутами заявки.'
 if p.text.startswith('Алгоритм проверки доступности (рисунок 5.3)'):
  p.text += ' Исправленная схема явно обнуляет резерв для каждой строки и вычисляет доступное количество как остаток минус резерв. Возвраты внутреннего и внешнего циклов проложены отдельно; до чтения очередного элемента проверяется его наличие, поэтому пустой список резервов также обрабатывается.'
# Replace image bytes while retaining relationships, and set intentional sizes.
for num,name,width in [(1,'bpmn',17),(3,'algo_1',14.5)]:
 shape=d.inline_shapes[num]; rel=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
 image=ROOT/'models'/f'{name}.png';d.part.related_parts[rel]._blob=image.read_bytes()
 from PIL import Image
 with Image.open(image) as im:w,h=im.size
 shape.width=Cm(width);shape.height=Cm(width*h/w)
# Helpers: standard report typography and tables.
def para(text='',style=None):
 p=d.add_paragraph(text,style=style);p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 p.paragraph_format.first_line_indent=Cm(1.25);p.paragraph_format.line_spacing=1.5;p.paragraph_format.space_after=Pt(0)
 return p
def heading(text,level=3,page=False):
 p=d.add_paragraph(text,style=f'Heading {level}');p.paragraph_format.keep_with_next=True
 if page and (text.startswith('6.1.') or text.startswith('6.2 ') or text.startswith('6 Реализация')):p.paragraph_format.page_break_before=True
 return p
def caption(text):
 p=para(text);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.keep_with_next=False
 return p
def figure(name,title,width=17,maxheight=20):
 from PIL import Image
 with Image.open(ROOT/'models'/f'{name}.png') as im:w,h=im.size
 width=min(width,maxheight*w/h)
 p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
 p.add_run().add_picture(str(ROOT/'models'/f'{name}.png'),width=Cm(width))
 caption(title)
def table(title,headers,rows,widths):
 p=para(title);p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.keep_with_next=True
 t=d.add_table(rows=1,cols=len(headers));t.style='Table Grid';t.autofit=False
 for col,w in zip(t.columns,widths):col.width=Cm(w)
 for c,text in zip(t.rows[0].cells,headers):c.text=text
 for row in rows:
  for c,text in zip(t.add_row().cells,row):c.text=str(text)
 for i,row in enumerate(t.rows):
  trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
  if i==0:repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  for c,w in zip(row.cells,widths):
   c.width=Cm(w)
   for p in c.paragraphs:
    p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4)
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:r.bold=i==0
 return t
def code(text):
 p=para(text);p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1;p.paragraph_format.keep_together=True
 return p
heading('6 Реализация на Джаве и организационный раздел',2,True)
para('В разделе представлена объектно-ориентированная версия обработки оптовых заявок на офисную мебель. Она сохраняет входной JSON и результаты процедурной программы КТ2: резервирование заявки R1 на 33 500,00 руб. и отмену с освобождением двух резервов. Модель классов выведена из исправленной модели данных; далее сопоставлены реализации, предложен состав команды внедрения и определены направления профессионального роста по десяти вакансиям.')
heading('6.1 Диаграмма классов UML')
para('Полная диаграмма в models/classes.puml и models/classes.png описывает 13 классов и интерфейсов. Для читаемости в отчёте приведены её предметные и поведенческие представления (рисунки 6.1–6.3). Обозначения UML взяты из спецификации OMG UML 2.5.1 [28]: «+» означает public, «−» private, «#» protected; пустой треугольник показывает наследование, пунктир с треугольником — реализацию интерфейса. Закрашенный ромб обозначает композицию, незакрашенный — агрегацию.')
para('Шесть сущностей КТ2 соответствуют шести предметным классам (таблица 6.1). Связи productId, customerId и requestId реализованы через идентификаторы. Request владеет строками: RequestLine не имеет самостоятельного назначения вне заявки. Каталог, остатки и резервы передаются Warehouse как самостоятельные объекты, что показано агрегацией. У товара допускается 0..1 загруженный остаток: отсутствие записи во входном снимке означает нулевой остаток, а не новую сущность. Резервы других заявок допустимы без загрузки самих заявок; кратности описывают предметную модель, а не полноту снимка JSON.')
table('Таблица 6.1 — Переход от модели данных к классам',['Сущность КТ2','Класс Java','Данные и поведение'],[
['Покупатель','Customer','id, name; чтение идентификатора и имени'],['Заявка','Request','id, customerId, confirmed, agreedTotal, lines, cancelled, cancellationReason; проверка, объединение строк, сумма и отметка отмены'],['Позиция заявки','RequestLine','productId и quantity; принадлежит Request'],['Товар','Product','id, name и price'],['Остаток','Stock','productId и quantity'],['Резерв','Reservation','id, requestId, productId, quantity, active; release() снимает активность']], [3.5,3.4,10.1])
heading('6.1.1 Заявка и её позиции',4,True)
figure('classes_request','Рисунок 6.1 — Покупатель, заявка и композиция позиций',17,21)
heading('6.1.2 Товар и складские данные',4,True)
figure('classes_stock','Рисунок 6.2 — Товар, остаток и резерв',17,16)
para('Поле agreedTotal сохраняет историческую договорённость в строковом формате входного контракта. Для вычислений используется BigDecimal. При изменении каталога согласованная сумма остаётся прежней, а новая сумма рассчитывается отдельно. Это сохраняет смысл атрибута, пояснённый в разделе 5.2.')
heading('6.1.3 Операции и склад',4,True)
figure('classes_hierarchy','Рисунок 6.3 — Интерфейс операций и наследование',17,17)
para('Warehouse содержит Map<String, Customer>, Map<String, Product>, Map<String, Stock>, List<Reservation> и Request. Его методы checkAvailability, reserveAll и cancel управляют доступностью и резервами. На рисунке 6.3 состав Warehouse свёрнут для читаемости; полные поля и методы приведены на общей диаграмме. Main создаёт объекты и выбирает Operation, а Json отвечает за разбор и запись данных. Эти технические классы также присутствуют на полной диаграмме.')
heading('6.2 Объектно ориентированная реализация',3,True)
para('Реализация использует Eclipse Temurin JDK 21 LTS как целевую среду и javac без внешних зависимостей. Проверка выполнена установленным Oracle JDK 26.0.2.1 с параметром --release 21. Полный код находится в src/java; компиляция и запуск не зависят от VS Code. Поля сущностей закрыты, неизменяемые коллекции выдаются наружу через List.copyOf и Map.copyOf. Изменяемое состояние Reservation скрыто за release(), а состояние Request — за cancel().')
table('Таблица 6.2 — Операции BPMN и методы Java',['Операция','Python КТ2','Java КТ3'],[
['Проверить корректность заявки','validate_request','Request.validate'],['Проверить доступность товаров','check_availability','Warehouse.checkAvailability'],['Рассчитать стоимость заказа','calculate_total','Request.calculateTotal'],['Зарезервировать все позиции','reserve_request','Warehouse.reserveAll'],['Отменить заказ и снять резерв','cancel_request','Warehouse.cancel через CancelOperation']], [6.3,4.3,6.4])
para('Operation имеет две конкретные реализации через AbstractOperation: ReserveOperation и CancelOperation. Базовый класс хранит проверенную ненулевую ссылку на Warehouse и предоставляет общий неизменяемый вход apply(); потомки переопределяют execute(). Первый выполняет проверку и создаёт резервы, второй проверяет реквизиты отмены и снимает активность. Это разные поведения, а не формальная иерархия одинаковых классов. Вызывающий код работает через интерфейс [16].')
code('Operation operation;\nif ("cancel".equals(data.get("operation")))\n    operation = new CancelOperation(warehouse, requestId, reason);\nelse operation = new ReserveOperation(warehouse);\nreturn operation.apply();')
para('Проверка доступности повторяет вложенные циклы Python: для каждой объединённой позиции просматриваются все резервы, учитываются только активные резервы того же артикула. Время O(n·m), память O(n) для дефицита. Метод calculateTotal выполняет O(n) арифметических операций; при фиксированной разрядности сумм требуется O(1) дополнительной памяти. Он использует BigDecimal и HALF_EVEN, как Decimal в КТ2 [29]. Разрядность чисел влияет на реальную стоимость арифметики в обеих версиях.')
code('Map<String, BigDecimal> quantities = new LinkedHashMap<>();\nfor (RequestLine line : lines)\n    quantities.merge(line.productId(), line.quantity(), BigDecimal::add);')
para('LinkedHashMap объединяет повторяющиеся товары и сохраняет порядок первого появления, как dict в Python. BigDecimal для количества позволяет сохранить проверку больших целых JSON-чисел без переполнения int. Числа с дробной записью 2.0 и булевы значения отклоняются как количества, как в Python. Парсер Json сохраняет отличие целого JSON-числа от дробного.')
heading('6.2.1 Сборка и результаты проверки',4)
code('cd src/java\nmkdir -p out\njavac --release 21 -encoding UTF-8 -Xlint:all -d out *.java\njava -cp out Main example.json\njava -cp out Main example_cancel.json')
para('Во входе example.json заявка R1 содержит T1 в количестве 2 по цене 12 500,00 и K1 в количестве 1 по цене 8 500,00. Остатки равны 10 и 6; другой заказ уже резервирует 2 единицы T1. Общая сумма: 2 × 12 500,00 + 1 × 8 500,00 = 33 500,00 руб. Обе версии возвращают одинаковые JSON-значения:')
code('{"status":"reserved","request_id":"R1","total":"33500.00"}')
para('Во входе example_cancel.json активны два резерва R1 и один R0. Отменяется R1 с причиной «Покупатель отказался от заказа». Обе версии возвращают:')
code('{"status":"cancelled","request_id":"R1",\n "reason":"Покупатель отказался от заказа",\n "released_reservations":2}')
para('Сравнительная проверка verify.py выполняет 31 сценарий: оба примера, неизвестного покупателя и товар, пустую заявку, нулевое, отрицательное, дробное, строковое, логическое и большое количество, дефицит, ожидание подтверждения, изменение суммы, отменённый и повторный резерв, дубликаты строк, пустые резервы и остатки, округление, ошибки и повтор отмены. Все результаты совпали с Python. StateTest дополнительно проверяет изменения объектов: отсутствие частичного резерва при отказе, защиту коллекций, сохранение чужого резерва, причины отмены и физического остатка. Сборка выполняется без предупреждений -Xlint:all.')
para('Данные живут в памяти одного запуска. Отмена изменяет объекты, но не переписывает исходный JSON. Проверка перед резервированием не защищает от одновременных процессов. На КТ4 понадобится транзакция СУБД и блокировка или иной механизм конкурентного доступа; здесь промышленная атомарность не заявляется.')
heading('6.3 Сопоставление реализаций',3,True)
para('Таблица 6.3 отделяет различия парадигмы от свойств языков. Та же логика могла бы быть объектной в Python или процедурно организованной в Java; наличие классов в синтаксисе само по себе не делает проект объектным.')
table('Таблица 6.3 — Сопоставление Python и Java',['Причина','Python КТ2','Java КТ3','Следствие'],[
['Парадигма','Словарь заявки передаётся функциям','Request хранит данные и методы validate, mergedLines, calculateTotal','Инварианты и поведение заявки собраны в одном объекте'],
['Парадигма','cancel_request меняет словари','Warehouse.cancel и Reservation.release скрывают изменение','Состояние резервов изменяется через предметные операции'],
['Парадигма','Условие в process_request выбирает функцию','Operation и два наследника AbstractOperation','Полиморфный вызов apply для разных операций'],
['Парадигма','Общие списки и словари доступны вызывающему коду','Закрытые поля и неизменяемые представления коллекций','Внешний код не может произвольно очистить список резервов'],
['Язык','Динамические dict/list и проверка type(quantity)','Статические типы, обобщённые List/Map и BigDecimal','Компилятор проверяет типы; JSON всё равно проверяется при вводе'],
['Язык','Decimal и quantize','BigDecimal и setScale(HALF_EVEN)','Разный API десятичной арифметики, одинаковый денежный результат'],
['Язык','Запуск интерпретатором Python','javac создаёт байткод, java запускает JVM','Разные команды сборки и запуска'],
['Язык','json из стандартной библиотеки','Отдельный адаптер Json без сторонних библиотек','В Java SE нет аналогичного встроенного JSON API; предметная логика отделена от формата']], [3.0,4.5,5.3,4.2])
para('Пример изменения: добавить третью операцию предварительного расчёта без резервирования. В процедурной версии добавляется функция и ветвь диспетчеризации process_request. В объектной версии можно добавить наследника AbstractOperation, переопределить execute и зарегистрировать его выбор в Main. Request.calculateTotal и Warehouse.checkAvailability остаются общими. ООП упрощает повторное использование поведения в иерархии, но не избавляет от изменения точки выбора операции. Третья операция в сдаваемой реализации не добавлена, чтобы сохранить контракт КТ2.')
heading('6.4 Состав команды внедрения',3,True)
para('Учебную реализацию выполнил один автор. В таблице 6.4 описана проектируемая команда для промышленного внедрения системы на одном складе. Колонка самооценки опирается на артефакты практики: наличие учебного результата не считается подтверждением опыта промышленной эксплуатации. Интерфейс для внешних посетителей в объём проекта не входит, поэтому отдельная роль UI-дизайнера не выделяется.')
table('Таблица 6.4 — Роли команды и компетенции',['Роль и задачи','Профильные навыки','Личные качества','Самооценка'],[
['Системный аналитик: требования, BPMN, модель данных, правила согласования','BPMN, UML, ER, SQL, REST, интервью, спецификации','Точные вопросы, ясное описание правил','Есть учебные BPMN, ER и ФТ. Требуют развития интервью и проектирование контрактов интеграции'],
['Backend-разработчик: предметная модель, Java, API и слой БД','Java Core, ООП, коллекции, Spring, PostgreSQL, Git, транзакции','Инициатива, обоснование решений, работа с рецензией','Есть проверяемая консольная реализация. Spring и конкурентные транзакции этой работой не подтверждены'],
['QA-инженер: сценарии, автотесты, регрессия, приёмка','Тест-дизайн, SQL, API, JUnit, Postman, CI','Внимание к деталям, ясное описание дефекта','Есть сравнение 31 сценария и тесты состояния. Нужны API-тесты и тестирование конкуренции'],
['DevOps-инженер: сборка, доставка, мониторинг и восстановление','Linux, CI/CD, контейнеры, PostgreSQL, метрики, резервные копии','Аккуратность, спокойная диагностика, документация','Есть инструкция CLI и Git. CI/CD, мониторинг и восстановление пока не подтверждены']], [4.2,4.4,3.8,4.6])
para('Аналитик согласует правила с менеджером и кладовщиком; разработчик переносит их в код и миграции; QA проверяет реализацию на примерах и отказах; DevOps обеспечивает воспроизводимую доставку и наблюдаемость. При малой нагрузке разработчик может совмещать часть DevOps-задач, но ответственность за резервное копирование и восстановление должна быть назначена явно.')
heading('6.5 Анализ рынка труда',3,True)
heading('6.5.1 Выборка вакансий',4)
para('На 21.11.2026 рассмотрены десять карточек девяти компаний на двух площадках: Хабр Карьера и сайт вакансий Яндекса. Выборка охватывает backend, системный анализ, QA и эксплуатацию. Она целевая и малая: частоты характеризуют только эти десять карточек, а не весь рынок. Вакансия № 10 архивная, но её требования доступны; её нельзя считать открытым предложением. Рекламные оценки «похожие специалисты получают» исключены из зарплат. Поля, которых нет в карточке, отмечены как неуказанные.')
jobs=json.loads((ROOT/'tools/market_kt3.json').read_text())
table('Таблица 6.5 — Требования и условия вакансий',['№ и вакансия','Требования','Опыт и условия'],[[str(j['id'])+'. '+j['title']+'\n'+j['company'],j['detail'],j['experience']+'\n'+j['conditions']] for j in jobs],[4.6,6.3,6.1])
para('Ссылки на карточки таблицы 6.5 приведены ниже. Для всех дата просмотра — 21.11.2026. Вакансии используются как данные анализа и не включаются в список научной литературы.')
for j in jobs:
 p=para(str(j['id'])+'. '+j['url']);p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(6)
heading('6.5.2 Сводка требований',4)
counts=Counter(skill for j in jobs for skill in set(j['skills']))
para('Для подсчёта объединены SQL и работа с реляционными БД, UML и BPMN, а также REST, SOAP и HTTP API. Spring включает Spring Boot. Технология учитывается один раз на вакансию, только если она названа как требование или часть рабочего стека. Желание изучать UML/BPMN в стажировке № 7 не приравнено к требованию владеть ими; неопределённая «контейнеризация» № 10 не приравнена к Docker. Таблица 6.6 воспроизводится из полей skills в tools/market_kt3.json репозитория.')
table('Таблица 6.6 — Частота требований в выборке',['Навык','Вакансий из 10','Номера'],[[skill,str(count),', '.join(str(j['id']) for j in jobs if skill in j['skills'])] for skill,count in counts.most_common()],[5.5,4,7.5])
para('SQL/БД связывают разработку, аналитику, тестирование и эксплуатацию: целостность данных важна независимо от роли. Java и API особенно значимы для backend и QA. Spring встречается у трёх backend-работодателей, поэтому консольной реализации недостаточно для перехода к их рабочему стеку. Для начального уровня полезны вакансии № 1, 4, 5 и 7; Senior-вакансии используются как ориентир дальнейшего развития, а не как оценка текущей готовности автора.')
heading('6.5.3 Образовательные программы',4,True)
para('В таблице 6.7 сопоставлены три программы Яндекс Практикума по официальным страницам, просмотренным 21.11.2026 [32–34]. Они развивают разные роли одной команды. Указан базовый формат; расширенные тарифы и интенсивы могут иметь другие сроки. Оплата и трудоустройство по итогам курса не оцениваются.')
table('Таблица 6.7 — Сравнение образовательных программ',['Организация и программа','Срок и содержание','Связь с вакансиями и проектом'],[
['Яндекс Практикум\nJava-разработчик [32]','10 месяцев; Java, ООП, Git, тестирование, Spring Boot, базы данных','№ 1–4: переход от Java Core к сервису на Spring и хранилищу PostgreSQL. Повторение базовой части менее приоритетно, чем сервисная разработка'],
['Яндекс Практикум\nСистемный аналитик [33]','9 месяцев; требования, UML/BPMN, SQL, JSON, Postman, проектная практика','№ 5–7: развитие контрактов API и требований. Дополняет уже созданные схемы практикой согласования с заказчиком'],
['Яндекс Практикум\nИнженер по тестированию [34]','Базовый формат 4 месяца; тест-дизайн, проверки приложений и API, тестовая документация','№ 8–9: воспроизводимые сценарии, проверки API. Для требований Java AQA дополнительно нужны JUnit и REST Assured']], [5,5.2,6.8])
para('Для выбранной роли backend-разработчика наиболее прямой путь даёт Java-программа: она закрывает Spring и БД из вакансий № 1–4. Программа аналитика полезна для качества требований и контрактов. Базовая QA-программа укрепляет тест-дизайн, но не заменяет коммерческий опыт автоматизации, требуемый в № 8–9. Последовательное изучение выбранных модулей реалистичнее одновременного прохождения трёх полных программ.')
heading('6.5.4 Приоритеты профессионального роста',4)
priorities=[
('SQL и транзакции', 'SQL/БД', 'реализовать PostgreSQL-хранилище и транзакцию резервирования; проверить две конкурирующие заявки и откат при дефиците. Учебная ER-модель уже есть, промышленная конкурентная работа ещё не подтверждена'),
('Java и сервисный слой', 'Java', 'закрепить Core и коллекции, затем перенести операции в REST-сервис на Spring Boot; критерием станет повторное прохождение тех же 31 сценария через API. Spring явно указан в № 1–3'),
('Контракты и тестирование API', 'API', 'описать OpenAPI и добавить позитивные и негативные API-тесты с JUnit и REST Assured; оформить ошибки и проверить коды ответа. Это развивает backend и QA-компетенции'),
('Автоматизация проверок', 'CI/CD', 'собирать Java и запускать сравнение сценариев в CI на каждом изменении; сохранять отчёт тестов. Следующий шаг — контейнер и контролируемая доставка'),
('Командная проверка и документация', 'UML/BPMN', 'согласовать схемы с исполнителем процесса, провести взаимное рецензирование, исправить замечания отдельными коммитами. Учебные диаграммы не заменяют навыка уточнения требований')]
for i,(title,skill,action) in enumerate(priorities,1):para(f'{i}. {title}. Основание: {skill} встречается в {counts[skill]} из 10 карточек. План: {action}.')
heading('6.6 Рецензирование и учёт исправлений',3,True)
para('Взаимное рецензирование ещё не проведено: пара и код одногруппника не определены, внешние замечания не получены. В review/review.md зафиксированы статус и критерии проверки. Самопроверка программы не подменяет рецензию другого студента. Для завершения этого требования нужно обменяться кодом, указать ФИО, группу, URL и хеш проверенного коммита, записать конкретные замечания и ответы; исправления оформить отдельными коммитами.')
para('История Git содержит три тематических коммита: исправления моделей КТ2, реализация Java и UML, отчёт и материалы КТ3. В метаданных указаны даты 16, 18 и 20 ноября 2026 года. Выгрузка истории приведена в vcs/git_log.txt, ссылка на репозиторий — в vcs/repo_url.txt.')
table('Таблица 6.8 — Исправления по КТ1 и КТ2',['Замечание','Выполненное исправление'],[
['Не указан дистрибутив JDK и выбор VS Code','Раздел 3 уточняет Temurin 21 LTS и причины выбора единой среды для Python и Java'],
['Одинаковые id дорожек, неверные DI-ссылки','Три уникальных Lane_manager, Lane_system, Lane_warehouse; bpmn-js импортирует без предупреждений'],
['Решения без шлюзов и тонкие конечные события','Три exclusiveGateway; «нет» по умолчанию, «да» с условием; конечные события рендерит BPMN-редактор'],
['Покупатель во внутренней дорожке','Отдельный пул Buyer и три потока сообщений'],
['Не обоснован agreed_total в 3НФ','Раздел 5.2 объясняет исторический факт согласованной суммы'],
['Слившиеся циклы и пропущенные вычисления','Схема 5.3 разделяет возвраты; добавлены резерв = 0 и доступно = остаток − резерв'],
['Оформление источников 12 и 13','Указаны корпоративные авторы, вид электронного ресурса, отсутствие даты публикации и актуальная дата обращения']], [6.0,11.0])
# Restore and update bibliography.
for e in bibliography:body.insert(len(body)-1,e)
for p in d.paragraphs:
 if p.text.startswith('1С. Управление продажами'):
  p.text='Фирма «1С». Управление продажами в 1С Управление торговлей 8 : электронный ресурс. — Дата публикации не указана. — URL: https://v8.1c.ru/trade/upravlenie-prodazhami/ (дата обращения: 21.11.2026). — Текст : электронный.'
 if p.text.startswith('МойСклад. Управление торговлей.'):
  p.text='МойСклад. Управление торговлей : электронный ресурс. — Дата публикации не указана. — URL: https://www.moysklad.ru/reshenija/upravlenie-torgovley/ (дата обращения: 21.11.2026). — Текст : электронный.'
refs=[
'Object Management Group. Unified Modeling Language. Version 2.5.1. — 2017. — URL: https://www.omg.org/spec/UML/2.5.1 (дата обращения: 21.11.2026). — Text : electronic.',
'Oracle. BigDecimal : Java Platform Standard Edition 21 API Specification. — URL: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/BigDecimal.html (дата обращения: 21.11.2026). — Text : electronic.',
'Eclipse Adoptium. Eclipse Temurin JDK 21 LTS : электронный ресурс. — URL: https://adoptium.net/temurin/releases/?version=21 (дата обращения: 21.11.2026).',
'Microsoft. Getting Started with Java in VS Code : электронный ресурс. — URL: https://code.visualstudio.com/docs/java/java-tutorial (дата обращения: 21.11.2026).',
'Яндекс Практикум. Java-разработчик : образовательная программа. — URL: https://practicum.yandex.ru/courses/java-developer/ (дата обращения: 21.11.2026). — Текст : электронный.',
'Яндекс Практикум. Системный аналитик : образовательная программа. — URL: https://practicum.yandex.ru/systems-analyst/ (дата обращения: 21.11.2026). — Текст : электронный.',
'Яндекс Практикум. Инженер по тестированию : образовательная программа. — URL: https://practicum.yandex.ru/qa-engineer/ (дата обращения: 21.11.2026). — Текст : электронный.']
for i,text in enumerate(refs,28):
 para(f'{i}. {text}')
# Rebuild the static table of contents with a page map from the rendered PDF.
headings=[p for p in d.paragraphs if p.style.name.startswith('Heading')]
page_map_path=ROOT/'tools/report_pages_kt3.json';pages=json.loads(page_map_path.read_text()) if page_map_path.exists() else {}
sdt=body.xpath('.//w:sdt')[0];content=sdt.find(qn('w:sdtContent'))
for node in list(content):content.remove(node)
title=d.add_paragraph('СОДЕРЖАНИЕ');title.alignment=WD_ALIGN_PARAGRAPH.CENTER;title.runs[0].bold=True;content.append(title._p)
for p in headings:
 if p.text=='ОСНОВНАЯ ЧАСТЬ':continue
 level=int(p.style.name[-1]);toc=d.add_paragraph();toc.paragraph_format.first_line_indent=Cm(0);toc.paragraph_format.left_indent=Cm(max(0,level-2)*0.4)
 toc.paragraph_format.line_spacing=1.0;toc.paragraph_format.space_after=Pt(3)
 toc.paragraph_format.tab_stops.add_tab_stop(Cm(16.7),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
 toc.add_run(p.text+'\t'+str(pages.get(p.text,'')))
 content.append(toc._p)
# Replace an isolated page break with a heading break to prevent an empty page.
for p in list(d.paragraphs):
 if p.text=='5 Аналитический раздел':
  prev=p._p.getprevious()
  if prev is not None and prev.tag==qn('w:p') and prev.xpath('.//w:br[@w:type="page"]'):
   body.remove(prev)
  p.paragraph_format.page_break_before=True
# Uniform black 14 pt text, preserve title page font/structure as in KT1.
for style in d.styles:
 if style.type==1:
  style.font.name='Times New Roman';style.font.size=Pt(14);style.font.color.rgb=RGBColor(0,0,0)
for s in d.sections:
 s.left_margin=Cm(3);s.right_margin=Cm(1);s.top_margin=Cm(2);s.bottom_margin=Cm(2)
# Explicit fonts and removal of blue inherited hyperlink text throughout body.
title_done=False
for e in body:
 if 'Москва 2026 г.' in ''.join(e.itertext()):title_done=True;continue
 if not title_done:continue
 for run in e.iter(qn('w:r')):
  pr=run.find(qn('w:rPr'))
  if pr is None:pr=OxmlElement('w:rPr');run.insert(0,pr)
  for tag,val in [('sz','28'),('szCs','28'),('color','000000')]:
   child=pr.find(qn('w:'+tag))
   if child is None:child=OxmlElement('w:'+tag);pr.append(child)
   child.attrib.clear();child.set(qn('w:val'),val)
  fonts=pr.find(qn('w:rFonts'))
  if fonts is None:fonts=OxmlElement('w:rFonts');pr.insert(0,fonts)
  for a in ('ascii','hAnsi','eastAsia','cs'):fonts.set(qn('w:'+a),'Times New Roman')
# Existing report body spacing preserved; new body paragraphs already have 1.5.
OUT=ROOT/'Отчет_ИКБО-10-24_БикташевИИ_КТ3.docx';d.save(OUT);print(OUT)
