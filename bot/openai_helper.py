import datetime
import logging

import tiktoken

import openai

import requests
import json
from datetime import date
from calendar import monthrange

# Models can be found here: https://platform.openai.com/docs/models/overview
GPT_3_MODELS = ("gpt-3.5-turbo", "gpt-3.5-turbo-0301")
GPT_4_MODELS = ("gpt-4", "gpt-4-0314")
GPT_4_32K_MODELS = ("gpt-4-32k", "gpt-4-32k-0314")
GPT_ALL_MODELS = GPT_3_MODELS + GPT_4_MODELS + GPT_4_32K_MODELS


def default_max_tokens(model: str) -> int:
    """
    Gets the default number of max tokens for the given model.
    :param model: The model name
    :return: The default number of max tokens
    """
    return 1200 if model in GPT_3_MODELS else 2400


class OpenAIHelper:
    """
    ChatGPT helper class.
    """

    def __init__(self, config: dict):
        """
        Initializes the OpenAI helper class with the given configuration.
        :param config: A dictionary containing the GPT configuration
        """
        openai.api_key = config['api_key']
        openai.proxy = config['proxy']
        self.config = config
        self.conversations: dict[int: list] = {}  # {chat_id: history}
        self.last_updated: dict[int: datetime] = {}  # {chat_id: last_update_timestamp}

    def get_conversation_stats(self, chat_id: int) -> tuple[int, int]:
        """
        Gets the number of messages and tokens used in the conversation.
        :param chat_id: The chat ID
        :return: A tuple containing the number of messages and tokens used
        """
        if chat_id not in self.conversations:
            self.reset_chat_history(chat_id)
        return len(self.conversations[chat_id]), self.__count_tokens(self.conversations[chat_id])

    async def get_chat_response(self, chat_id: int, query: str) -> tuple[str, str]:
        """
        Gets a full response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """
        response = await self.__common_get_chat_response(chat_id, query)
        answer = ''

        if len(response.choices) > 1 and self.config['n_choices'] > 1:
            for index, choice in enumerate(response.choices):
                content = choice['message']['content'].strip()
                if index == 0:
                    self.__add_to_history(chat_id, role="assistant", content=content)
                answer += f'{index + 1}\u20e3\n'
                answer += content
                answer += '\n\n'
        else:
            answer = response.choices[0]['message']['content'].strip()
            self.__add_to_history(chat_id, role="assistant", content=answer)

        if self.config['show_usage']:
            answer += "\n\n---\n" \
                      f"💰 Tokens used: {str(response.usage['total_tokens'])}" \
                      f" ({str(response.usage['prompt_tokens'])} prompt," \
                      f" {str(response.usage['completion_tokens'])} completion)"

        return answer, response.usage['total_tokens']

    async def get_chat_response_stream(self, chat_id: int, query: str):
        """
        Stream response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used, or 'not_finished'
        """
        response = await self.__common_get_chat_response(chat_id, query, stream=True)

        answer = ''
        async for item in response:
            if 'choices' not in item or len(item.choices) == 0:
                continue
            delta = item.choices[0].delta
            if 'content' in delta:
                answer += delta.content
                yield answer, 'not_finished'
        answer = answer.strip()
        self.__add_to_history(chat_id, role="assistant", content=answer)
        tokens_used = str(self.__count_tokens(self.conversations[chat_id]))

        if self.config['show_usage']:
            answer += f"\n\n---\n💰 Используемые токены: {tokens_used}"

        yield answer, tokens_used

    async def __common_get_chat_response(self, chat_id: int, query: str, stream=False):
        """
        Request a response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """
        try:
            if chat_id not in self.conversations or self.__max_age_reached(chat_id):
                self.reset_chat_history(chat_id)

            self.last_updated[chat_id] = datetime.datetime.now()

            self.__add_to_history(chat_id, role="user", content=query)

            # Summarize the chat history if it's too long to avoid excessive token usage
            token_count = self.__count_tokens(self.conversations[chat_id])
            exceeded_max_tokens = token_count + self.config['max_tokens'] > self.__max_model_tokens()
            exceeded_max_history_size = len(self.conversations[chat_id]) > self.config['max_history_size']

            if exceeded_max_tokens or exceeded_max_history_size:
                logging.info(f'История чатов для ID чата {chat_id} слишком длинный. Подведение итогов...')
                try:
                    summary = await self.__summarise(self.conversations[chat_id][:-1])
                    logging.debug(f'Резюме: {summary}')
                    self.reset_chat_history(chat_id)
                    self.__add_to_history(chat_id, role="assistant", content=summary)
                    self.__add_to_history(chat_id, role="user", content=query)
                except Exception as e:
                    logging.warning(f'Ошибка при подведении итогов истории чатов: {str(e)}. Выскакивающие элементы вместо...')
                    self.conversations[chat_id] = self.conversations[chat_id][-self.config['max_history_size']:]

            return await openai.ChatCompletion.acreate(
                model=self.config['model'],
                messages=self.conversations[chat_id],
                temperature=self.config['temperature'],
                n=self.config['n_choices'],
                max_tokens=self.config['max_tokens'],
                presence_penalty=self.config['presence_penalty'],
                frequency_penalty=self.config['frequency_penalty'],
                stream=stream
            )

        except openai.error.RateLimitError as e:
            raise Exception(f'⚠️ Превышен предел скорости _OpenAI Rate Limit. ⚠️\n{str(e)}') from e

        except openai.error.InvalidRequestError as e:
            raise Exception(f'⚠️ OpenAI Неверный запрос ⚠️\n{str(e)}') from e

        except Exception as e:
            raise Exception(f'⚠️ Произошла ошибка ⚠️\n{str(e)}') from e

    async def generate_image(self, prompt: str) -> tuple[str, str]:
        """
        Generates an image from the given prompt using DALL·E model.
        :param prompt: The prompt to send to the model
        :return: The image URL and the image size
        """
        try:
            response = await openai.Image.acreate(
                prompt=prompt,
                n=1,
                size=self.config['image_size']
            )

            if 'data' not in response or len(response['data']) == 0:
                logging.error(f'Нет ответа от GPT: {str(response)}')
                raise Exception('⚠️ Произошла ошибка ⚠️\nПожалуйста, повторите попытку через некоторое время.')

            return response['data'][0]['url'], self.config['image_size']
        except Exception as e:
            raise Exception(f'⚠️ Произошла ошибка ⚠️\n{str(e)}') from e

    async def transcribe(self, filename):
        """
        Transcribes the audio file using the Whisper model.
        """
        try:
            with open(filename, "rb") as audio:
                result = await openai.Audio.atranscribe("whisper-1", audio)
                return result.text
        except Exception as e:
            logging.exception(e)
            raise Exception(f'⚠️ Произошла ошибка ⚠️\n{str(e)}') from e

    def reset_chat_history(self, chat_id, content=''):
        """
        Resets the conversation history.
        """
        if content == '':
            content = self.config['assistant_prompt']
        self.conversations[chat_id] = [{"role": "system", "content": content}]

    def __max_age_reached(self, chat_id) -> bool:
        """
        Checks if the maximum conversation age has been reached.
        :param chat_id: The chat ID
        :return: A boolean indicating whether the maximum conversation age has been reached
        """
        if chat_id not in self.last_updated:
            return False
        last_updated = self.last_updated[chat_id]
        now = datetime.datetime.now()
        max_age_minutes = self.config['max_conversation_age_minutes']
        return last_updated < now - datetime.timedelta(minutes=max_age_minutes)

    def __add_to_history(self, chat_id, role, content):
        """
        Adds a message to the conversation history.
        :param chat_id: The chat ID
        :param role: The role of the message sender
        :param content: The message content
        """
        self.conversations[chat_id].append({"role": role, "content": content})

    async def __summarise(self, conversation) -> str:
        """
        Summarises the conversation history.
        :param conversation: The conversation history
        :return: The summary
        """
        messages = [
            { "role": "assistant", "content": "Резюмируйте этот разговор в 700 символах или меньше" },
            { "role": "user", "content": str(conversation) }
        ]
        response = await openai.ChatCompletion.acreate(
            model=self.config['model'],
            messages=messages,
            temperature=0.4
        )
        return response.choices[0]['message']['content']

    def __max_model_tokens(self):
        if self.config['model'] in GPT_3_MODELS:
            return 4096
        if self.config['model'] in GPT_4_MODELS:
            return 8192
        if self.config['model'] in GPT_4_32K_MODELS:
            return 32768
        raise NotImplementedError(
            f"Максимальное количество токенов для модели {self.config['model']} пока не реализовано."
        )

    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    def __count_tokens(self, messages) -> int:
        """
        Counts the number of tokens required to send the given messages.
        :param messages: the messages to send
        :return: the number of tokens required
        """
        try:
            model = self.config['model']
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("gpt-3.5-turbo")

        if model in GPT_3_MODELS:
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif model in GPT_4_MODELS + GPT_4_32K_MODELS:
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}.""")
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def get_grant_balance(self):
        """Gets remaining grant balance for new users from OpenAI API.

        :return: remaining grant balance
        """
        headers = {
            "Authorization": f"Bearer {openai.api_key}"
        }
        response = requests.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
        billing_data = json.loads(response.text)
        balance = billing_data["total_available"]
        return balance
    
    def get_billing_current_month(self):
        """Gets billed usage for current month from OpenAI API.

        :return: dollar amount of usage this month
        """
        headers = {
            "Authorization": f"Bearer {openai.api_key}"
        }
        # calculate first and last day of current month
        today = date.today()
        first_day = date(today.year, today.month, 1)
        _, last_day_of_month = monthrange(today.year, today.month)
        last_day = date(today.year, today.month, last_day_of_month)
        params = {
            "start_date": first_day,
            "end_date": last_day
        }
        response = requests.get("https://api.openai.com/dashboard/billing/usage", headers=headers, params=params)
        billing_data = json.loads(response.text)
        usage_month = billing_data["total_usage"] / 100 # convert cent amount to dollars
        return usage_month