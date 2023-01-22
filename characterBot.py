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
    chat_log = character_description
    prompt_text = f'{chat_log}{restart_sequence} {message.text}{start_sequence}'
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt_text,
      temperature=0.8,
      max_tokens=150,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.3,
      stop=["\n"],
    )
    story = response['choices'][0]['text']
    msg = bot.send_message(message.from_user.id, story)
    chat_log = append_interaction_to_chat_log(prompt_text, story, chat_log) 
    bot.register_next_step_handler(msg, handle_message, chat_log)

def handle_message(message, chat_log):
    prompt_text = f'{chat_log}{restart_sequence} {message.text}{start_sequence}'
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt_text,
      temperature=0.8,
      max_tokens=150,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.3,
      stop=["\n"],
    )
    story = response['choices'][0]['text']
    bot.send_message(message.from_user.id, story)
    chat_log = append_interaction_to_chat_log(prompt_text, story, chat_log)

def append_interaction_to_chat_log(question, answer, chat_log):
    if chat_log is None:
        chat_log = character_description
    text = f'{restart_sequence}{question}{start_sequence}{answer}{chat_log}'
    return text[-100:]

if __name__ == '__main__':
    bot.infinity_polling()