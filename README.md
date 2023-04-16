# Чат-бот Telegram ChatGPT
![python-version](https://img.shields.io/badge/python-3.9-blue.svg)
[![openai-version](https://img.shields.io/badge/openai-0.27.4-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-GPL%202.0-brightgreen.svg)](LICENSE)
[![Publish Docker image](https://github.com/n3d1117/chatgpt-telegram-bot/actions/workflows/publish.yaml/badge.svg)](https://github.com/n3d1117/chatgpt-telegram-bot/actions/workflows/publish.yaml)

[Telegram-бот](https://core.telegram.org/bots/api), который интегрируется с API [ChatGPT](https://openai.com/blog/chatgpt/) от OpenAI для предоставления ответов. Готов к использованию с минимальной настройкой.

## Скриншоты
![demo](https://user-images.githubusercontent.com/11541888/225114786-0d639854-b3e1-4214-b49a-e51ce8c40387.png)

## Features
- [x] Support markdown in answers
- [x] Reset conversation with the `/reset` command
- [x] Typing indicator while generating a response
- [x] Access can be restricted by specifying a list of allowed users
- [x] Docker and Proxy support
- [x] (NEW!) Image generation using DALL·E via the `/image` command
- [x] (NEW!) Transcribe audio and video messages using Whisper (may require [ffmpeg](https://ffmpeg.org))
- [x] (NEW!) Automatic conversation summary to avoid excessive token usage
- [x] (NEW!) Track token usage per user - by [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) Get personal token usage statistics and cost per day/month via the `/stats` command - by [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) User budgets and guest budgets - by [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) Stream support
- [x] (NEW!) GPT-4 support
  - If you have access to the GPT-4 API, simply change the `OPENAI_MODEL` parameter to `gpt-4`
- [x] (NEW!) Localized bot language
  - Available languages :gb: :de: :ru: :tr: :it: :es: :indonesia:
- [x] (NEW!) Improved inline queries support for group and private chats - by [@bugfloyd](https://github.com/bugfloyd)
  - To use this feature, enable inline queries for your bot in BotFather via the `/setinline` [command](https://core.telegram.org/bots/inline)

## Additional features - help needed!
If you'd like to help, check out the [issues](https://github.com/n3d1117/chatgpt-telegram-bot/issues) section and contribute!  
If you want to help with translations, check out the [Translations Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219)

PR всегда приветствуются!

## Предварительные требования
- Python 3.9+
- [Telegram bot](https://core.telegram.org/bots#6-botfather) и его токен (см. [руководство](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))
- Учетная запись [OpenAI](https://openai.com) (см. раздел [конфигурации](#configuration))

## Начало работы

### Конфигурация
Скопируйте `accounts.json.example` и переименуйте его в `accounts.json`.

Настройте конфигурацию, скопировав файл `.env.example` и переименовав его в `.env` а затем отредактируйте необходимые параметры по желанию:

| Параметр                   | Описание                                                                                                                                                                                                                   |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `OPENAI_API_KEY`            | Ваш API-ключ OpenAI, который можно получить [здесь](https://platform.openai.com/account/api-keys)                                                                                                                                 |
| `TELEGRAM_BOT_TOKEN`        | Токен вашего Telegram-бота, полученный с помощью [BotFather](http://t.me/botfather) (см. [руководство](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))                                                                  |
| `ADMIN_USER_IDS`            | Идентификаторы пользователей Telegram администраторов. У этих пользователей есть доступ к особым командам администратора, информации и безоговорочных ограничений бюджета. ID администратора не нужно добавлять в `ALLOWED_TELEGRAM_USER_IDS`. **Обратите внимание**: по умолчанию отсутствуют админы ('-'). |
| `ALLOWED_TELEGRAM_USER_IDS` | Список идентификаторов пользователей Telegram через запятую, которые могут взаимодействовать с ботом (используйте [getidsbot](https://t.me/getidsbot), чтобы найти идентификатор вашего пользователя). **Внимание**: по умолчанию для всех разрешено (`*`).                       |

### Дополнительная конфигурация
Следующие параметры являются необязательными и могут быть заданы в файле `.env`:

#### Бюджеты
| Параметр                          | Описание                                                                                                                                                                                                                                                                                                                                                                               | Значение по умолчанию             |
|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------|
| `BUDGET_PERIOD`                    | Определяет временной интервал, к которому применяются все бюджеты. Доступные периоды: `daily` *(сбрасывает бюджет каждый день)*, `monthly` *(сбрасывает бюджеты первого числа каждого месяца)*, `all-time` *(никогда не сбрасывает бюджет)*. Дополнительную информацию см. в [Руководстве по бюджету](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184).                                                                  | `monthly`                 |
| `USER_BUDGETS`                     | Список $-сумм для каждого пользователя из списка `ALLOWED_TELEGRAM_USER_IDS`, разделенный запятыми, для установки пользовательского лимита использования расходов OpenAI API для каждого. Для `*`- списков пользователей первое значение `USER_BUDGETS` присваивается каждому пользователю. **Примечание**: по умолчанию, *нет лимитов* для любого пользователя (`*`). Дополнительную информацию см. в [Руководстве по бюджету](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184). | `*`                       |
| `GUEST_BUDGET`                     | $-amount в качестве лимита использования для всех гостевых пользователей. Гостевые пользователи - это пользователи в групповых чатах, которых нет в списке `ALLOWED_TELEGRAM_USER_IDS`. Значение игнорируется, если в бюджетах пользователей не установлены лимиты использования (`USER_BUDGETS`="*"). Дополнительную информацию см. в [Руководстве по бюджету](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184).                                                   | `100.0`                   |
| `TOKEN_PRICE`                      | $-цена за 1000 жетонов, используемая для расчета информации о стоимости в статистике использования (https://openai.com/pricing)                                                                                                                                                                                                                                                                                 | `0.002`                   |
| `IMAGE_PRICES`                     | Список, разделенный запятыми, состоящий из 3 элементов цен для различных размеров изображений: `256x256`, `512x512` и `1024x1024`.                                                                                                                                                                                                                                                                      | `0.016,0.018,0.02`        |
| `TRANSCRIPTION_PRICE`              | USD-цена за одну минуту расшифровки аудиозаписи                                                                                                                                                                                                                                                                                                                                           | `0.006`                   |

Просмотрите [Руководство по бюджету](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184) для возможных конфигураций бюджета.

#### Дополнительные опции конфигурации
| Параметр                          | Описание                                                                                                                                                                                                                                                                                                                                                                            | Значение по умолчанию                  |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| `ENABLE_QUOTING`                   | Включать ли цитирование сообщений в личных чатах                                                                                                                                                                                                                                                                                                                                     | `true`                         |
| `ENABLE_IMAGE_GENERATION`          | Включать ли генерацию изображений с помощью команды `/image`.                                                                                                                                                                                                                                                                                                                            | `true`                         |
| `ENABLE_TRANSCRIPTION`             | Разрешить ли расшифровку аудио- и видеосообщений                                                                                                                                                                                                                                                                                                                           | `true`                         |
| `PROXY`                            | Прокси, который будет использоваться для бота OpenAI и Telegram (например, `http://localhost:8080`)                                                                                                                                                                                                                                                                                                            | -                              |
| `OPENAI_MODEL`                     | Модель OpenAI, которую следует использовать для генерации ответов                                                                                                                                                                                                                                                                                                                                       | `gpt-3.5-turbo`                |
| `ASSISTANT_PROMPT`                 | Системное сообщение, которое задает тон и управляет поведением помощника                                                                                                                                                                                                                                                                                                         | `You are a helpful assistant.` |
| `SHOW_USAGE`                       | Показывать ли информацию об использовании токена OpenAI после каждого ответа                                                                                                                                                                                                                                                                                                                     | `false`                        |
| `STREAM`                           | Передавать ли ответы в потоковом режиме. **Примечание**: несовместимо, если включено, с `N_CHOICES` больше 1                                                                                                                                                                                                                                                                                        | `true`                         |
| `MAX_TOKENS`                       | Верхняя граница того, сколько токенов вернет API ChatGPT                                                                                                                                                                                                                                                                                                                             | `1200`                         |
| `MAX_HISTORY_SIZE`                 | Максимальное количество сообщений для хранения в памяти, после чего разговор будет обобщен, чтобы избежать чрезмерного использования токенов                                                                                                                                                                                                                                                               | `15`                           |
| `MAX_CONVERSATION_AGE_MINUTES`     | Максимальное количество минут, которое разговор должен прожить с момента последнего сообщения, после чего разговор будет сброшен                                                                                                                                                                                                                                                                | `180`                          |
| `VOICE_REPLY_WITH_TRANSCRIPT_ONLY` | Отвечать ли на голосовые сообщения только стенограммой или отвечать на стенограмму в формате ChatGPT                                                                                                                                                                                                                                                                              | `true`                         |
| `N_CHOICES`                        | Количество ответов для каждого входного сообщения. **Примечание**: установка значения больше 1 не будет работать правильно, если включен `STREAM`.                                                                                                                                                                                                                                   | `1`                            |
| `TEMPERATURE`                      | Число от 0 до 2. Более высокие значения сделают вывод более случайным                                                                                                                                                                                                                                                                                                                 | `1.0`                          |
| `PRESENCE_PENALTY`                 | Число между -2,0 и 2,0. Положительные значения наказывают новые лексемы в зависимости от того, появляются ли они в тексте до сих пор.                                                                                                                                                                                                                                                                       | `0.0`                          |
| `FREQUENCY_PENALTY`                | Число между -2,0 и 2,0. Положительные значения штрафуют новые лексемы на основе их существующей на данный момент частоты в тексте                                                                                                                                                                                                                                                                  | `0.0`                          |
| `IMAGE_SIZE`                       | Размер генерируемого DALL-E изображения. Допустимые значения: `256x256`, `512x512` или `1024x1024`.                                                                                                                                                                                                                                                                                                   | `512x512`                      |
| `GROUP_TRIGGER_KEYWORD`            | Если установлено, бот в групповых чатах будет отвечать только на сообщения, начинающиеся с этого ключевого слова                                                                                                                                                                                                                                                                                              | ""                             |
| `IGNORE_GROUP_TRANSCRIPTIONS`      | Если установлено значение true, бот не будет обрабатывать транскрипции в групповых чатах.                                                                                                                                                                                                                                                                                                                 | `true`                         |
| `BOT_LANGUAGE`                     | Language of general bot messages. Currently available: `en`, `de`, `ru`, `tr`, `it`, `es`, `id`.  **Note** [Contribute additional translations](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219) | `en`                               |

Более подробную информацию можно найти в [официальном справочнике API](https://platform.openai.com/docs/api-reference/chat).

### Установка
Клонируйте репозиторий и перейдите в каталог проекта:

```shell
git clone https://github.com/fisuri/chatgpt-telegram-bot.git -b main
cd chatgpt-telegram-bot
```

#### Из исходного кода
1. Создайте виртуальное окружение:
```shell
python -m venv venv
```

2. Активируйте виртуальное окружение:
```shell
# Для Linux или macOS:
source venv/bin/activate

# Для Windows:
venv\Scripts\activate
```

3. Установите зависимости, используя файл `requirements.txt`:
```shell
pip install -r requirements.txt
```

4. Используйте следующую команду для запуска бота:
```
python bot/main.py
```

#### Используя Docker Compose Запустите следующую команду для сборки и запуска Docker image:
```shell
docker compose up
```

#### Готовые Docker-образы
Вы также можете использовать Docker-образ из [Docker Hub](https://hub.docker.com/r/n3d1117/chatgpt-telegram-bot):
```shell
docker pull n3d1117/chatgpt-telegram-bot:latest
```

или из [GitHub Container Registry](https://github.com/n3d1117/chatgpt-telegram-bot/pkgs/container/chatgpt-telegram-bot/):

```shell
docker pull ghcr.io/n3d1117/chatgpt-telegram-bot:latest
```

## Благодарности

- [ChatGPT](https://chat.openai.com/chat) от [OpenAI](https://openai.com)
- [python-telegram-bot](https://python-telegram-bot.org)
- [jiaaro/pydub](https://github.com/jiaaro/pydub)

## Ограничения ответственности

Это личный проект и не связан с OpenAI.

## Лицензия

Этот проект выпущен в соответствии с условиями лицензии GPL 2.0. Более подробную информацию можно найти в файле [LICENSE](LICENSE), включенном в репозиторий.
