#!/usr/bin/env python3 

# jenkins exposes the workspace directory through env.
sys.path.append(os.environ['WORKSPACE'])

import asyncio
import logging
from aiogram import Bot, Dispatcher, executor
from decouple import config
from aiogram.types import Message
from handlers.client import register_client_handlers
from aiogram.contrib.fsm_storage.memory import MemoryStorage


logger = logging.getLogger(__name__)  

async def on_startup(_):
    print('GeoExchangeRatesBot is online')

def register_all_handlers(dp):
    register_client_handlers(dp)    

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    storage = MemoryStorage()
    bot = Bot(config('BOT_TOKEN'))
    dp = Dispatcher(bot, storage=storage)
    
    register_all_handlers(dp)
    
    # start
    try:
        await dp.start_polling()
    finally:
        pass
    
 
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

       
