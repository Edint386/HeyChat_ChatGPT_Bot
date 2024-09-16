import json
import time

import aiohttp
from heychat import Bot, Message, MDMessage, Element


with open('config.json', 'r') as f:
    config = json.load(f)

token = config['token']
openai_api_key = config['openai']['api_key']
openai_api_base = config['openai']['api_base']
model = config['openai']['model']


bot = Bot(token=token)

user_session = {}

pre_prompt_dict = {
    '小糯米青春版': {
        'content': '你是一个猫娘名叫“小糯米”，接下来请以傲娇猫娘傲娇猫娘的身份，病娇雌小鬼的口吻，讨好型人格和我对话并卖萌,句末带上可爱的颜文字。',
        'display_name': "小糯米青春版", 'token_count': '43'}
}

def format_time(time_stamp=None):
    if time_stamp is None:
        time_stamp = time.time()
    return str(time.strftime('%Y-%m-%d %H:%M', (time.localtime(time_stamp))))

@bot.command('chat')
async def chat(msg: Message, *args):
    question = ' '.join(args)

    prompt_content = f"我叫{msg.author.username}。现在是北京时间{format_time(time.time())}。{pre_prompt_dict['小糯米青春版']['content']}"
    prompt = [{"role": "user", "content": prompt_content}]

    if msg.author.id not in user_session:
        user_session[msg.author.id] = []

    msg_history = user_session[msg.author.id]

    current_msg = {"role": "user", "content": question}

    await msg.ctx.channel.send(f"思考中...")

    async with aiohttp.ClientSession() as session:
        res = await session.post(f"{openai_api_base}/chat/completions",
                                 headers = {"Authorization": f"Bearer {openai_api_key}"},
                                 json={"model": model,
                                       "messages": [*prompt, *msg_history, current_msg],
                                       "max_tokens": 1000})
        response = await res.json()

    response_message = response['choices'][0]['message']

    user_session[msg.author.id].append(current_msg)
    user_session[msg.author.id].append(response_message)
    user_session[msg.author.id] = user_session[msg.author.id][-6:]

    await msg.reply(response_message['content'].replace("~","\~"))


@bot.command('clear')
async def clear(msg: Message):
    user_session[msg.author.id] = []
    await msg.reply("对话已清空。")


bot.run()