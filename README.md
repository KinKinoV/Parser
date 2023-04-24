# Parser
Парсер с интерфейсом в виде Django сайта
Для запуска сайта и работы самого парсера надо ввести следующие команды:
## Windows
1. `python manage.py runserver` -- для запуска сервера Django
2. Запустить docker контейнер selenium/standalone-firefox (можно использовать команду `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.9.0-20230421`
## Linux
1. `python3 manage.py runserver` -- для запуска сервера Django
2. Запустить docker контейнер selenium/standalone-firefox (можно использовать команду `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.9.0-20230421`
