# BlazePay API

## Getting started
To make it easy for you to get started with bitbucket, here's a list of recommended next steps.

### Versions
BlazePay runs on Python 3.10.4.


### Setup Project 
Local Environment Settings

Create local environment settings for the project by overriding settings.py and environment settings.
- Create local.py in the project root and edit it. 
  ```
  touch config/local.py
  nano config/local.py
  ```

### Virtual Environment
Create and activate the virtual environment, and install the required packages.

- Install virtualenv.
  ```
  pip install virtualenv
  python -m venv env
  ```

- Create the virtual environment.
  ``` 
  python -m venv env
  ```

- Activate the virtual environment.
  - For bash (Linux):
    ```
    source env/bin/activate 
    ```
  - For console (Windows):
    ```
    .\env\Scripts\activate
    ```
- Install the required packages.
  ```
  pip install -r requirements.txt
  ```
- Run python
  ```
  python manage.py runserver
  ```


### Initial Setup Scripts 
This are the scripts needed to run.
```
sh migrate.sh
python manage.py populate_role
python manage.py populate_application
python manage.py populate_address

// Create the super admin
python manage.py createsuperuser
```

### Redis caching Setup
Setup redis on windows
https://redis.io/docs/getting-started/installation/install-redis-on-windows/
```
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update
sudo apt-get install redis

sudo service redis-server start
```

### Connect to Redis
```
redis-cli 
127.0.0.1:6379> ping
PONG
```

### Celery run
```
- celery -A config worker --loglevel=INFO --concurrency 1 -P solo
- celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Clean migration file
```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
pip install --upgrade --force-reinstall  Django==5.0.6
sh migrate.sh
```