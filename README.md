## Сайт для ведения блогов YaTube

![2022-07-31_14-17-29](https://user-images.githubusercontent.com/77703490/182024015-3e64e887-e6b9-4512-aa3f-cd395c333293.png)
Сайт позволяет просматривать записи пользователей.

После регистрации можно добовлять или редактировать свои записи, общаться с другими пользователями в комментариях.

Фильтровать ленту по избранным авторам или по группам, просматривать все записи одного автора.

### Как запустить проект на тестовом сервере:
<details><summary> Linux </summary>

Клонировать репозиторий, перейти в директорию с проектом.

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 yatube/manage.py migrate
```

Запустить проект:

```
python3 yatube/manage.py runserver
```
Сайт будет доступен по адресу:
```
http://127.0.0.1:8000/
```
</details>

<details><summary> Windows </summary>

Клонировать репозиторий, перейти в директорию с проектом.

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python yatube/manage.py migrate
```

Запустить проект:

```
python yatube/manage.py runserver
```
Сайт будет доступен по адресу:
```
http://127.0.0.1:8000/
```
</details>