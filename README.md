# hw05_final

# Проект, который собирает отзывы пользователей на произведения.

## Описание

### Это сайт, на котором можно создать свою страницу и добавлять записи. Если зайти на страницу автора, то можно посмотреть все записи автора.

### Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.

### Автор уже может выбрать имя и уникальный адрес для своей страницы. Дизайн пока что самый простой.

### Возможно нужно будет реализовать возможность модерировать записи и блокировать пользователей, если начнут присылать спам.

### Записи можно отправить в сообщество и посмотреть там записи разных авторов.

## Как установить проект

### Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:AKafer/hw05_final.git
cd hw05_final
```

### Создать и активировать виртуальное окружение:

```
python3 -m venv venv
source venv/bin/activate
```

### Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

### Выполнить миграции:

```
cd yatube
python3 manage.py migrate
```

### Запустить проект:

```
python3 manage.py runserver
```

## Стек технологий

### Python 3, Django 2.2, PostgreSQL, gunicorn, nginx, Яндекс.Облако(Ubuntu 18.04), pytest

## Автор проекта - Сергей Сторожук

