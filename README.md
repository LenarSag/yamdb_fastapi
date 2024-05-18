# yamdb_fastapi# Описание:


## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/LenarSag/blogicum_fastapi_async_db

cd blogicum_fastapi_async_db

Cоздать и активировать виртуальное окружение:

python3 -m venv venv

source venv/Scripts/activate

Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip

pip install -r requirements.txt


Подключаем и настраиваем алембик:

$ alembic init migration

В файле alembic.ini указываем адрес базы:

[alembic]
...
sqlalchemy.url = postgresql://romblin@localhost/db


В файле migration/env.py импортируем все модели и указываем target_metadata:

from db import *
target_metadata = Base.metadata

После этого:

alembic revision --autogenerate -m 'initial'
alembic upgrade head

Запуск проекта:

python main.py


## Документация для API запросов:

Подробная документация для API blogicum с примерами доступных запросов и результатов таких запросов доступна после запуска проекта по адресу http://127.0.0.1:8000/docs/

