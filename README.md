# Parser
Парсер с интерфейсом в виде Django сайта
Для запуска сайта и работы самого парсера надо ввести следующие команды:
## Windows
1. `pip install -r "requirments.txt"` -- установить все зависимости
2. `python manage.py runserver` -- для запуска сервера Django
3. Запустить docker контейнер selenium/standalone-firefox на портах 4444 и 7900(как в команде ниже) (можно использовать команду `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.9.0-20230421`
## Linux
1. `pip install -r "requirments.txt"` -- установить все зависимости
2. `python3 manage.py runserver` -- для запуска сервера Django
3. Запустить docker контейнер selenium/standalone-firefox на портах 4444 и 7900(как в команде ниже) (можно использовать команду `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.9.0-20230421`

После запуска сайта и selenium сайт доступен локально по порту 8000:

[http://localhost:8000/](http://localhost:8000/)

Виртуальная машина по ссылке:

[http://localhost:7900/?autoconnect=1&resize=scale&password=secret](http://localhost:7900/?autoconnect=1&resize=scale&password=secret)

Для получения `keys.py` нужного для запуска сайта, писать в телеграм [@KinKinoV](https://t.me/KinkinoV).
