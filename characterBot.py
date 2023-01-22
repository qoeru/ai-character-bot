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

@bot.message_handler(content_types=['text'])
def handle_welcome(message):
    name = message.from_user.username + ".txt"
    try:
        f = open(name)
        chat_log = f.read()
        f.close()
    except FileNotFoundError:
        chat_log = ""
    prompt_text = f'{chat_log}\n{character_description}\n{message.from_user.username}:{message.text}{start_sequence}'
    if(len(prompt_text) > 5000):
        prompt_text = prompt_text[-5000:]
    print(prompt_text)
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt_text,
      temperature=0.8,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.3,
      stop=["\n"],
    )
    story = response['choices'][0]['text']
    msg = bot.send_message(message.from_user.id, story)
    chat_log = append_interaction_to_chat_log(message.text, story, chat_log, message.from_user.username) 
    bot.register_next_step_handler(msg, handle_message, chat_log)

def handle_message(message, chat_log):
    prompt_text = f'{chat_log}\n{character_description}\n{message.from_user.username}:{message.text}{start_sequence}'
    print(prompt_text)
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
    chat_log = append_interaction_to_chat_log(message.text, story, chat_log, message.from_user.username)
    bot.register_next_step_handler(msg, handle_message, chat_log)

def append_interaction_to_chat_log(question, answer, chat_log, name):
    if(len(chat_log) > 5000):
        chat_log = chat_log[-5000:]
    chat_log = f'{chat_log}\n{name}:{question} {start_sequence}{answer} '
    name = name + ".txt"
    f = open(name, 'w')
    f.write(chat_log)
    f.close()
    return chat_log

if __name__ == '__main__':
    bot.polling()