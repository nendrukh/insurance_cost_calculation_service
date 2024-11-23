## Insurance cost calculation service

### Что делает сервис?
REST API сервис по расчёту стоимости страхования в зависимости от типа груза и объявленной стоимости (ОС).

### Стек технологий
* FastAPI
* SQLAlchemy
* asyncpg (для асинхронной работы с базой)
* PostgreSQL
* Adminer
* Pydantic
* Docker
* Docker-compose
* Kafka

### Запуск сервиса

* Запустить docker compose
```commandline
docker-compose up --build
```

* Затем нужно добавить тариф и можно получить расчёт стоимости страхования по тарифу

### Методы сервиса

* Добавление тарифа

Тариф(ы) можно добавить через следующий POST запрос:
```shell
curl -H 'Content-Type: application/json' -d '{
	"2019-12-26": [
        {
            "cargo_type": "Glass",
            "rate": "0.04"
        },
        {
            "cargo_type": "Other",
            "rate": "0.01"
        }
    ],
    "2019-11-26": [
        {
            "cargo_type": "Glass",
            "rate": "0.04"
        },
        {
            "cargo_type": "Other",
            "rate": "0.01"
        }
    ]
}' http://localhost:8001/tariff
```

Ответ от сервера:
```json
{
  "status": "OK", 
  "msg": "Tariffs added to the database"
}
```

* Расчет стоимости страхования

Для расчета нужно отправить GET запрос, указывая тариф (тип груза и дата), и объявленную стоимость:
```shell
curl 'http://localhost:8001/calculate_insurance?cargo_type=Glass&date=2019-11-26&cost=120.5'
```

Ответ от сервера:
```json
{
  "status": "OK",
  "result": 4.82
}
```

* Изменение тарифа

Для изменения ставки по тарифу нужно отправить PUT запрос, указывая тариф и новую ставку:
```shell
curl -X 'PUT' 'http://localhost:8001/tariff?cargo_type=Glass&date=2019-11-26&new_rate=0.05'
```

Ответ от сервера:
```json
{
  "msg": "Tariff updated"
}
```

* Удаление тарифа

Для удаления тарифа нужно отправить DELETE запрос, указывая тариф (дата и тип груза):
```shell
curl -X 'DELETE' 'http://localhost:8001/tariff?cargo_type=Glass&date=2019-11-26'
```

Ответ от сервера:
```json
{
  "msg": "Tariff deleted"
}
```

### Логирование

Также добавлено логирование изменений через батчи в kafka.
Логи отправляются в kafka когда размер батча достигает 3, то есть 3 раза писали лог, или при остановке сервера на FastAPI.
Логи пишутся при каждом успешном ответе от сервера или при ошибке (только если сервер смог обработать её)

* Посмотреть все логи в kafka:
```shell
docker exec -it kafka kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic logs-topic --from-beginning
```

### Мониторинг
* Также добавлен мониторинг за базой через сервис adminer:
```
http://localhost:8002/
```
Движок: PostgreSQL

Сервер: postgres

Имя пользователя: root_user

Пароль: hard_pass

База данных: some_db