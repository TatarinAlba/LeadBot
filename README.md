# LeadTelegramBot
The purpose of the project was to create bot for giving need infomration about some work in thematic chats. This is only __alpha__ version of the project. We need to add possibility for working with multiple users. By now i have used next libraries
* SqlAlchemy - ORM.
* Asyncio - During working with bots, i need to make tasks asynchronously.
* Telethon - For wokring from the backend side (**Stormtrooper**)
* Aiogram - Working from the frontend side (**Supplier**)
* RabbitMQ (pika, aio_pika) - For communication between devices.

Everything were packed into 3 docker containers (__RabbitMQ, Supplier, Stormtrooper__)

For beginning, you should write in the **_StormTrooper's_** config file _api_id_ and _api_hash_. Information about how to get it you can find in official Telethon documentation page. In the **_Suplier's_** config file you should past _TOKEN_, which could be taken from the @BotFather.

For starting the project just pull the repository and write next command.

`docker-compose up --build`

If docker-compose utility is not installed on your machine. Try to download it by using package manager.

I am free to any contributions here. Thank you.