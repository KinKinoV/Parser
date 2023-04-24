# Parser
Парсер с интерфейсом в виде Django сайта
Для запуска сайта и работы самого парсера надо ввести следующие команды:
## Windows
1. `pip install -r "requirments.txt"` -- установить все зависимости
2. `python manage.py runserver` -- для запуска сервера Django
3. Запустить docker контейнер selenium/standalone-firefox (можно использовать команду `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.9.0-20230421`
## Linux
1. `pip install -r "requirments.txt"` -- установить все зависимости
2. `python3 manage.py runserver` -- для запуска сервера Django
3. Запустить docker контейнер selenium/standalone-firefox (можно использовать команду `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.9.0-20230421`
