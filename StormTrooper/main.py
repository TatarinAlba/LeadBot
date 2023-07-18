'''
MIT License

Copyright (c) Albert Avkhadeev

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."

'''


import json
import re
import os
import time
import logging
import pika
import telethon.tl.functions as functions
from telethon.tl.types import InputPeerUser
from telethon import TelegramClient, events

config_data = dict()  # data with api_id and api_hash


# Check if logs folder exists and if not create's it
if not os.path.exists('logs'):
    os.makedirs('logs')

with open('config.json', 'r') as f:
    config_data = json.load(f)

# You can create your applciation by finding information about login in Telethon documentation
api_id = config_data['api_id']
api_hash = config_data['api_hash']
# If rabbitmq supposed to be on remote server, specify ip
rabbitmq_host = 'rabbitmq'
# Creating logging file in the project
logging.basicConfig(
    level=logging.INFO,
    filename="logs/logs.log",
    filemode="w",
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.Formatter.converter = lambda *args: time.localtime(
    time.time() + 3 * 3600)
# Creating client for the user. System version is used for avoiding signing out from all devices after exiting from the program.
client = TelegramClient('StormTrooper', api_id, api_hash,
                        system_version="4.16.30-vxCUSTOM")

# Creating rabbit_mq producer channel with the default exchanger and 'message' queue which will send all satisfied message
# to the Supplier service
rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, heartbeat=600,
                                                                    blocked_connection_timeout=300))
rabbit_channel = rabbit_connection.channel()
rabbit_channel.queue_declare(queue='messages')
# Checking for the new messages inside the bot


@client.on(events.NewMessage())
async def handler(event):
    # Trying to prevent error if some messages were sended for the user P2P.
    # Main purpose for now to focus on group chats with the keymessages
    if event.is_group and event.message.sender != None and event.message.sender.bot == False:
        # Getting information about keywords, which should sattisfy
        with open('resources/keywords.txt', 'r') as f:
            keywords = f.readlines()

        # Getting keywords which pattern should not sattisfy
        with open('resources/restricted_keywords.txt', 'r') as f:
            restricted_keywords = f.readlines()
        # Check if message contains any of the restricted keywords
        if any(re.search(keyword.strip().lower(), event.message.message.lower()) for keyword in restricted_keywords):
            return
        # Check if message contains any of the keywords
        if any(re.search("^" + keyword.strip().lower(), event.message.message.lower()) for keyword in keywords):
            from_user = await event.get_sender()
            chat_from = event.chat if event.chat else (await event.get_chat())
            if from_user.username != None:
                data = {
                    'username': from_user.username,
                    'message': event.message.message,
                }
                logging.info(f"User has username {data['username']} has been detected. Chat: {chat_from.title}. Sending message to Supplier")
                rabbit_channel.basic_publish(
                    exchange='', routing_key='messages', body=json.dumps(data))
            elif from_user.phone != None:
                data = {
                    
                    'phone': from_user.phone,
                    'message': event.message.message,
                }
                logging.info(f"User has no username, but has number {data['phone']}. It has been detected. Chat: {chat_from.title}. Sending message to Supplier")
                rabbit_channel.basic_publish(
                    exchange='', routing_key='messages', body=json.dumps(data))
            else:
                logging.error(f"Username with message {event.message.message} has no anything.Chat: {chat_from.title}")

# Starting the client
client.start()
client.run_until_disconnected()
