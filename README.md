
# slackbot
## данный бот предназначен для работы с API от OpenAI

- Прежде чем начать необходимо создать приложение в пространстве Slack
и сохранить все токены, далее мы будем их экспортировать в переменное окружение.

- Установка зависимостей

```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip
pip install -r requirements.txt
```

- Установка переменного окружения

```
export SLACK_BOT_TOKEN=" "
export SLACK_APP_TOKEN=" "
export OPENAI_API_KEY=" "
export OPENAI_MODEL="gpt-4"
```