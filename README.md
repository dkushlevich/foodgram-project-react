<div align=center>
  
  # [Foodgram](https://foodgram.servehttp.com/) продуктовый помощник
  
  [![Foodgram_CI/CD](https://github.com/dkushlevich/foodgram-project-react/workflows/Foodgram_CI/CD/badge.svg)](https://github.com/dkushlevich/kittygram_final/workflows/CICD-Kittygram/badge.svg)
  
  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
  ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

  ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
  ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
  ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
  
  ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)


</div>

## Описание проекта


Foodgram - онлайн-сервис, представляющий собой продуктового помощника как для начинающих кулинаров, так и для опытных гурманов. В рамках этого сервиса пользователи могут делиться своими рецептами, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список избранного, а также скачивать сводный список продуктов в формате .pdf перед походом в магазин для приготовления выбранных блюд.

## Структура базы данных

![Image](https://github.com/dkushlevich/Dkushlevich/blob/main/images/Foodgram_ER.png?raw=true)


## Подготовка сервера и деплой проекта

1. Создать директорию foodgram/ в домашней директории сервера.

2. В корне папки foodgram поместить файл .env, заполнить его по шаблону

  ```env
    ALLOWED_HOSTS=<Ваш домен>, <IP сервера>
    DEBUG=False

    POSTGRES_USER=...
    POSTGRES_PASSWORD=...
    POSTGRES_DB=...
    
    DB_HOST=...
    DB_PORT=...
```

4. Установить Nginx и настроить конфигурацию так, чтобы все запросы шли в контейнеры на порт 8000.

    ```bash
        sudo apt install nginx -y 
        sudo nano etc/nginx/sites-enabled/default
    ```
    
    Пример конфигурация nginx
    ```bash
        server {
            server_name <Ваш IP> <Домен вашего сайта>;
            server_tokens off;
            client_max_body_size 20M;
        
            location / {
                proxy_set_header Host $http_host;
                proxy_pass http://127.0.0.1:9000;
        }
    ```
    
    > При необходимости настройте SSL-соединение

5. Установить docker и docker-compose
   
``` bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin     
```

4. Добавить в Secrets GitHub Actions данного репозитория на GitHub переменные окружения

``` env
    DOCKER_USERNAME=<имя пользователя DockerHub>
    DOCKER_PASSWORD=<пароль от DockerHub>
    
    USER=<username для подключения к удаленному серверу>
    HOST=<ip сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш приватный SSH-ключ>
    
    TELEGRAM_TO=<id вашего Телеграм-аккаунта>
    TELEGRAM_TOKEN=<токен вашего бота>
```
5. Запустить workflow проекта выполнив команды:

```bash
  git add .
  git commit -m ''
  git push
```
6. После этого выпонятся следующие workflow jobs:

- **tests:** запуск pytest.
- **build_and_push_to_docker_hub:** сборка и размещение образа проекта на DockerHub.
- **deploy:** автоматический деплой на боевой сервер и запуск проекта.
- **send_massage:** отправка уведомления об успешном деплое в Телеграм.

> С примерами запросов можно ознакомиться в [спецификации API](https://foodgram.servehttp.com/redoc/)


<div align=center>

## Контакты

[![Telegram Badge](https://img.shields.io/badge/-dkushlevich-blue?style=social&logo=telegram&link=https://t.me/dkushlevich)](https://t.me/dkushlevich) [![Gmail Badge](https://img.shields.io/badge/-dkushlevich@gmail.com-c14438?style=flat&logo=Gmail&logoColor=white&link=mailto:dkushlevich@gmail.com)](mailto:dkushlevich@gmail.com)

</div>
