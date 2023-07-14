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
import config
import logging
import pika
from telethon import TelegramClient, events

#Check if logs folder exists and if not create's it
if not os.path.exists('logs'):
    os.makedirs('logs')

# You can create your applciation by finding information about login in Telethon documentation
api_id = config.api_id 
api_hash = config.api_hash
# If rabbitmq supposed to be on remote server, specify ip
rabbitmq_host = 'localhost'
# Creating logging file in the project
logging.basicConfig(level=logging.INFO, filename="logs/StormTrooperLogs.log",filemode="w")

# Getting information about keywords, which should sattisfy
with open('resources/keywords.txt', 'r') as f:
    keywords = f.readlines()

# Getting keywords which pattern should not sattisfy
with open('resources/restricted_keywords.txt', 'r') as f:
    restricted_keywords = f.readlines()

# Creating client for the user. System version is used for avoiding signing out from all devices after exiting from the program.
client = TelegramClient('StormTrooper', api_id, api_hash, system_version="4.16.30-vxCUSTOM")

# Creating rabbit_mq producer channel with the default exchanger and 'message' queue which will send all satisfied message
# to the Supplier service
rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
rabbit_channel = rabbit_connection.channel()
rabbit_channel.queue_declare(queue='messages')

# Checking for the new messages inside the bot
@client.on(events.NewMessage)
async def handler(event):
    # Trying to prevent error if some messages were sended for the user P2P.
    # Main purpose for now to focus on group chats with the keymessages
    if event.is_group:
        # Check if message contains any of the restricted keywords
        if any(re.search(keyword.strip().lower(), event.message.message.lower()) for keyword in restricted_keywords):
            return
        # Check if message contains any of the keywords
        if any(re.search(keyword.strip().lower(), event.message.message.lower()) for keyword in keywords):
            # Create dictionary with user ID and message text
            data = {
                'username': event.message.sender.username,
                'message': event.message.message,
            }
            print(data)
            # Convert dictionary to JSON string and send it to RabbitMQ queue
            rabbit_channel.basic_publish(exchange='', routing_key='messages', body=json.dumps(data))


# Starting the client
client.start()
client.run_until_disconnected()