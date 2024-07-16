# [![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=FOODGRAM)](https://git.io/typing-svg)

## Социальная сеть для любителей придумывать, готовить и делиться рецептами различных блюд.
### Зарегестрированные пользователи могут так же скачать список продуктов необходимых для приготовления по рецептам.

## Стек:
```
-Python 3.10
-Django
-DRF
-PostgresQL
-Docker
-Nginx
-Git
-GitActions
-Gunicorn


## Как развернуть проект:
Ссылка на проект: [GitHub repo](https://github.com/fluegergehaimer/foodgram)

1.Клонировать репозиторий
```
git clone https://github.com/fluegergehaimer/foodgram
```

2.Перейти в папку с проектом:
```
cd foodgram/backend
```

3.Cоздать и активировать виртуальное окружение:
```
python3 -m venv env

source env/bin/activate
```

4.Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```
5.Выполнить миграции:

```
python3 manage.py migrate
```

6.Для наполнения БД данными из файлов (папка "data") использовать команды:
```
python3 manage.py import_ingredients_json
python3 manage.py import_tags_json
```

7.Запустить проект:

```
python3 manage.py runserver
```



Авторы:
- [команда Yandex-практикума](https://github.com/yandex-praktikum?tab=repositories)
- [Никита Чередниченко](https://github.com/fluegergehaimer)