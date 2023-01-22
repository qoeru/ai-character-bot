import os
import telebot
import openai

with open('tg_key.txt') as f:
    tg_api = f.read()
f.close

with open('character_name.txt') as f:
    character_name = f.read()
f.close()

with open('character_description.txt') as f:
    character_description = f.read()
f.close

completion = openai.Completion()
openai.api_key_path = "openai_key.txt"
bot = telebot.TeleBot(tg_api)

start_sequence = "\n" + character_name + ":"
restart_sequence = "\n\nPerson:"

@bot.message_handler(content_types=['text'])
def handle_welcome(message):
    prompt_text = f'{character_description}{restart_sequence}{message.text}{start_sequence}'
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt_text,
      temperature=0.8,
      max_tokens=200,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.3,
      stop=["\n"],
    )
    story = response['choices'][0]['text']
    msg = bot.send_message(message.from_user.id, story)
    chat_log = append_interaction_to_chat_log(message.text, story, "") 
    bot.register_next_step_handler(msg, handle_message, chat_log)

def handle_message(message, chat_log):
    prompt_text = f'{chat_log}{restart_sequence} {message.text}{start_sequence}'
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt_text,
      temperature=0.8,
      max_tokens=1000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.3,
      stop=["\n"],
    )
    story = response['choices'][0]['text']
    msg = bot.send_message(message.from_user.id, story)
    chat_log = append_interaction_to_chat_log(message.text, story, chat_log)
    bot.register_next_step_handler(msg, handle_message, chat_log)

def append_interaction_to_chat_log(question, answer, chat_log):
    if(len(chat_log) > 9000):
        chat_log = chat_log[-9000:]
    context = f'{character_description} "\n" {chat_log} {restart_sequence}{question} {start_sequence}{answer} '
    print(context)
    return context


if __name__ == '__main__':
    bot.polling()