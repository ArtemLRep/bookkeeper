# Простая программа для управления личными финансами
#### (учебный проект для курса по практике программирования на Python)

# Программа позволяет:
  1. Записывать, удалять, редактировать расходы.
  2. Устанавливать бюджет на текущий день, неделю и месяц, а также следить за его выполнением.
  3. Смотреть расходы по категориям за день и текущий месяц

# Как пользоваться

1. Для старта программы скачать к себе в папку. Затем запустить файл main_file.py
Откроется вот такое окно(Интерфейс Ubuntu 22.0):

![Image-alt](/images/app1.png)


2. Список категорий заполняется во вкладке "Category list"
  * Записываем категории в каждой строке, затем нажимаем кнопку "commit change".
  * При записи проверяется, что в списке нет категорий с одиноковым названием.(Незначащие пробелы и табы не учитываются). Если будут, вылезет меню с ошибкой.
  * Также можно выделять подкатегории пробелом или табом. Практически это не используется, но информация о подкатегориях записывается в репозиторий. В следующих версиях программы добалю аналитику по подкатегориям)

![Image-alt](/images/app2.png)

3. Для добаления расхода необходимо заполнить соответствующие поля данными в нужном формате и нажать кнопку "Add expense".
Формат полей:
  * edit date -> день - месяц - год час:минута
  * edit amount -> Число >=0
  * edit category -> Выбрать из выпадающего список из категорий (список категорий записывается в листе "Category list")
  * edit comment -> строка. Требований нет пользователь сам знаем решает. Если запишет что-то невнятно сможет поправить
  при неправильном заполнении полей вылезут меню с ошибкой
  
![Image-alt](/images/app3.png)

4. Для установки бюджета необходимо во вкладке Budget заполнить соответствущие поля положительными числами, затем нажать кнопку "change budget"

![Image-alt](/images/app4.png)


5. Для редактирования расходов необходимо щелкнуть по ячейке ввести новые данные, нажать правой кнопкой мыши и выбрать "update cell"

![Image-alt](/images/app5.png)

6. Также можно обновить несколько ячеек сразу. Ввести в них данные, выделить их, нажать правой кнопкой мыши и выбрать "update cell"
  Выбрать ячейки из разных колонок можно через клавишу Alt. Если просто ввести новые данные и не нажать "update cell", то данные не обновятся!
  Разумеется новые данные должны быть корректными и при неправильном формате вылезет меню с ошибкой.
  
![Image-alt](/images/app6.png)

7. При обновлении категорий, если старых названий нет в новых, то им присваивается название 'Not stated'. Я решил это сделать, так как не одобряю удаление расходов. Пусть пользователь сам поменяет вс как он хочет. Хотя это тоже наверное не самое лучшее решение)

![Image-alt](/images/app7.1.png)  ![Image-alt](/images/app7.2.png)

8. Для удалении строки необходимо выделить любую ячейку строки(можно сразу несколько строк и ячеек), затем нажать правой кнопком мыши и выбрать "delete row"

![Image-alt](/images/app8.png)

9. Таблица расходов по категориям на период во вкладке Budget.
   * Период выбирается кнопками "day","month". Под периодом "month" текущий календарный месяц!
   * При любом действии: добавлении, удалении,обновлении расхода, изменении списка категорий таблица расходов по категоям меняется автоматически, а периодом выбирается день
  
![Image-alt](/images/app9.png)
