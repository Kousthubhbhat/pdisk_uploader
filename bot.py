from os import environ
import os
from urllib.parse import urlparse
import aiohttp
from pyrogram import Client, filters
import requests
import re

##########################################################################################################
userDB = environ.get('userDB')
userDB = userDB.replace(' ', '').replace('\n', '').split(',')

apiDB = environ.get('apiDB)
apiDB = apiDB.replace(' ', '').replace('\n', '').split(',')

API_ID = environ.get('API_ID')
API_HASH = environ.get('API_HASH')
BOT_TOKEN = environ.get('BOT_TOKEN')
CHANNEL = environ.get('CHANNEL')
bot = Client('pdisk bot',
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             workers=50,
             sleep_threshold=0)

async def saver(item_id, apikey):
    res = False
    raw_item_id = item_id:
    res = await requests(f'http://linkapi.net/open/clone_item?api_key={apikey}&item_id={item_id}', timeout=7)
    res = res.json()
    print(res)
    res = res['data']['item_id']   
    status = res['status']
    if status == 500:
        if res['msg'] == 'please try later':
            print('waiting')
            await asyncio.sleep(1)
            item_id = await saver(item_id, apikey)
            return item_id
        elif res['msg'] == f'cannot repost from yourself {raw_item_id}':
            res = raw_item_id
            return res
        else:
            print(res)
            res = 'No_Content_Found'
            return res
    if status == -1:
        if res['msg'] == 'please try later':
            print('waiting')
            await asyncio.sleep(1)
            item_id = await saver(item_id, apikey)
            return item_id
        elif res['msg'] == f'cannot repost from yourself {raw_item_id}':
            res = raw_item_id
            return res
        else:
            print(res)
            res = False
            return res
    elif status == 1:
        item_id = res['data']['item_id']
        return item_id
    else:
        print(res)
    await asyncio.sleep(1)

async def ziko_function(caption, user):
    if user in userDB:
        user = userDB.index(user)
        apikey = apiDB[user][0]
    else:
        return False
    urlDB = re.findall("(?P<url>https?://[^\s]+)", caption)
    for i in range(len(urlDB)):
        url = urlDB[i]
        if re.search('t\.me|telegram', url):
            caption = caption.replace(url,f'{apiDB[user][1]}')
            continue
        r = requests.get(url)
        url = r.url
        if re.search('yout', url):
            continue
        dottest = re.findall('\.', url)
        if len(dottest) >= 3:
            continue
        if re.search('share-video\?', url):
            titem_id = url.lower().split('=')[-1]
        item_id = await saver(titem_id, apikey)
        if item_id == titem_id:
            caption = caption.replace(url, f'https://pdisks.com/share-video?videoid={item_id}')
        elif item_id == 'No_Content_Found':
            caption = caption.replace(url, '')
        elif item_id == False:
            return
    caption = re.sub('@[^\s]+', apiDB[user][2], caption)
    return caption


@bot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    await message.reply(
        f"**Hey {message.chat.first_name}!**\n\n"
        "𝐈'𝐦 𝐚 𝐏𝐝𝐢𝐬𝐤 𝐜𝐨𝐧𝐯𝐞𝐫𝐭𝐞𝐫 𝐛𝐨𝐭. 𝐉𝐮𝐬𝐭 𝐬𝐞𝐧𝐝 𝐦𝐞 𝐚𝐧𝐲 𝐩𝐝𝐢𝐬𝐤 𝐥𝐢𝐧𝐤 𝐢 𝐰𝐢𝐥𝐥 𝐜𝐨𝐧𝐯𝐞𝐫𝐭 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐥𝐢𝐧𝐤 𝐓𝐡𝐢𝐬 𝐛𝐨𝐭 𝐢𝐬 𝐞𝐝𝐢𝐭𝐞𝐝 𝐛𝐲\n\n✅ @jack_sparow119\n\n𝐢𝐟 𝐲𝐨𝐮 𝐧𝐞𝐞𝐝 𝐥𝐢𝐤𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 @jack_sparow119")


@bot.on_message(filters.text & filters.private)
async def pdisk_uploader(bot, message):
    new_string = str(message.text)
    caption = await ziko_function(new_string,user = message.chat.id)
    await message.reply(f'<b>{caption}</b>', quote=True)

@bot.on_message(filters.photo & filters.private)
async def pdisk_uploader(bot, message):
    new_string = str(message.caption)
    caption = ziko_function(new_string)
    await bot.send_photo(message.chat.id, message.photo.file_id, caption=f'<b>{caption}</b>')

async def addFooter(str):
    footer = """


⭐️JOIN CHANNEL ➡️ t.me/""" + CHANNEL
    return str + footer

bot.run()
