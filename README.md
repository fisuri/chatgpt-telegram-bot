# Чат-бот Telegram ChatGPT
![python-version](https://img.shields.io/badge/python-3.9-blue.svg)
[![openai-version](https://img.shields.io/badge/openai-0.27.4-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-GPL%202.0-brightgreen.svg)](LICENSE)
[![Publish Docker image](https://github.com/n3d1117/chatgpt-telegram-bot/actions/workflows/publish.yaml/badge.svg)](https://github.com/n3d1117/chatgpt-telegram-bot/actions/workflows/publish.yaml)

A [Telegram bot](https://core.telegram.org/bots/api) that integrates with OpenAI's _official_ [ChatGPT](https://openai.com/blog/chatgpt/), [DALL·E](https://openai.com/product/dall-e-2) and [Whisper](https://openai.com/research/whisper) APIs to provide answers. Ready to use with minimal configuration required.

## Скриншоты
![demo](https://user-images.githubusercontent.com/11541888/225114786-0d639854-b3e1-4214-b49a-e51ce8c40387.png)

## Особенности
- [x] Поддержка разметки в ответах
- [x] Сброс разговора с помощью команды `/reset`.
- [x] Индикатор набора текста при генерации ответа
- [x] Доступ можно ограничить, указав список разрешенных пользователей
- [x] Поддержка Docker и прокси
- [x] (NEW!) Создание изображений с помощью DALL-E через команду `/image`
- [x] (NEW!) Расшифровка аудио- и видеосообщений с помощью Whisper (может потребоваться [ffmpeg](https://ffmpeg.org))
- [x] (NEW!) Автоматическое подведение итогов разговора во избежание чрезмерного использования токенов
- [x] (NEW!) Отслеживать использование токенов по каждому пользователю - [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) Получите статистику использования персонального токена и стоимость в день/месяц с помощью команды `/stats` - [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) Бюджеты пользователей и бюджеты гостей - [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) Поддержка потока
- [x] (NEW!) Поддержка GPT-4
  - Если у вас есть доступ к API GPT-4, просто измените параметр `OPENAI_MODEL` на `gpt-4`
- [x] (NEW!) Локализация языка бота
  - Available languages :gb: :de: :ru: :tr: :it: :es: :indonesia: :netherlands: :cn:
- [x] (NEW!) Улучшена поддержка встроенных запросов для групповых и приватных чатов - [@bugfloyd](https://github.com/bugfloyd)
  - Чтобы использовать эту функцию, включите встроенные запросы для вашего бота в BotFather с помощью команды `/setinline` [command](https://core.telegram.org/bots/inline)

## Дополнительные функции - нужна помощь!
Если вы хотите помочь, ознакомьтесь с [issues](https://github.com/n3d1117/chatgpt-telegram-bot/issues) раздел и внести свой вклад!  
Если вы хотите помочь с переводами, загляните в раздел [Translations Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219)

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

#### Additional optional configuration options
| Parameter                          | Description                                                                                                                                                                                          | Default value                      |
|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `ENABLE_QUOTING`                   | Whether to enable message quoting in private chats                                                                                                                                                   | `true`                             |
| `ENABLE_IMAGE_GENERATION`          | Whether to enable image generation via the `/image` command                                                                                                                                          | `true`                             |
| `ENABLE_TRANSCRIPTION`             | Whether to enable transcriptions of audio and video messages                                                                                                                                         | `true`                             |
| `PROXY`                            | Proxy to be used for OpenAI and Telegram bot (e.g. `http://localhost:8080`)                                                                                                                          | -                                  |
| `OPENAI_MODEL`                     | The OpenAI model to use for generating responses                                                                                                                                                     | `gpt-3.5-turbo`                    |
| `ASSISTANT_PROMPT`                 | A system message that sets the tone and controls the behavior of the assistant                                                                                                                       | `You are a helpful assistant.`     |
| `SHOW_USAGE`                       | Whether to show OpenAI token usage information after each response                                                                                                                                   | `false`                            |
| `STREAM`                           | Whether to stream responses. **Note**: incompatible, if enabled, with `N_CHOICES` higher than 1                                                                                                      | `true`                             |
| `MAX_TOKENS`                       | Upper bound on how many tokens the ChatGPT API will return                                                                                                                                           | `1200` for GPT-3, `2400` for GPT-4 |
| `MAX_HISTORY_SIZE`                 | Max number of messages to keep in memory, after which the conversation will be summarised to avoid excessive token usage                                                                             | `15`                               |
| `MAX_CONVERSATION_AGE_MINUTES`     | Maximum number of minutes a conversation should live since the last message, after which the conversation will be reset                                                                              | `180`                              |
| `VOICE_REPLY_WITH_TRANSCRIPT_ONLY` | Whether to answer to voice messages with the transcript only or with a ChatGPT response of the transcript                                                                                            | `true`                             |
| `N_CHOICES`                        | Number of answers to generate for each input message. **Note**: setting this to a number higher than 1 will not work properly if `STREAM` is enabled                                                 | `1`                                |
| `TEMPERATURE`                      | Number between 0 and 2. Higher values will make the output more random                                                                                                                               | `1.0`                              |
| `PRESENCE_PENALTY`                 | Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far                                                                                     | `0.0`                              |
| `FREQUENCY_PENALTY`                | Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far                                                                                | `0.0`                              |
| `IMAGE_SIZE`                       | The DALL·E generated image size. Allowed values: `256x256`, `512x512` or `1024x1024`                                                                                                                 | `512x512`                          |
| `GROUP_TRIGGER_KEYWORD`            | If set, the bot in group chats will only respond to messages that start with this keyword                                                                                                            | -                                  |
| `IGNORE_GROUP_TRANSCRIPTIONS`      | If set to true, the bot will not process transcriptions in group chats                                                                                                                               | `true`                             |
| `BOT_LANGUAGE`                     | Language of general bot messages. Currently available: `en`, `de`, `ru`, `tr`, `it`, `es`, `id`, `nl`, `cn`.  [Contribute with additional translations](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219) | `en`                               |

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
