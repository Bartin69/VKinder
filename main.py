import config

from datetime import datetime
import json, requests, asyncio, threading, orjson, re

loop = asyncio.new_event_loop()

# -------------------- Parametrs -------------------- #
BOT_TOKEN = config.bot_token
BOT_VERSION = config.bot_version
LOGGER_STATUS = config.logger_status

DB_HOST = config.db_host # DataBase Host IP
DB_PORT = config.db_port # DataBase Host Port Number
DB_USER = config.db_user # DataBase User
DB_PASSWORD = config.db_password # DataBase User Password
DATABASE_NAME = config.database_name # DataBase Name

# -------------------- VK Bot -------------------- #
from vkbottle.modules import logger
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import PayloadRule, CommandRule

bot = Bot(token=BOT_TOKEN, loop=loop)

from modules.logger import logging
Logger = logging.Logger(write_file=False, log_path = './logs/', rewrite_file=True)
ExceptionsLogger = logging.Logger(write_file=False, log_path = './logs/', log_file='exceptions_log', rewrite_file=True)

if not LOGGER_STATUS:
	from loguru import logger
	logger.disable("vkbottle")

# -------------------- Modules -------------------- #
from modules.utils import utils
from modules.markups import keyboards

Keyboards = keyboards.Keyboards()
Utils = utils.Utils(BOT_VERSION, bot)

# -------------------- Setup DataBase -------------------- #
import modules.database.MySQL_Async as MySQL_Async
import modules.database.MySQL_Functions as MySQL_Functions

DB_connector = MySQL_Async.MySQL_Connect(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DATABASE_NAME, logging=False, pool_size=10)
DB_executor = MySQL_Functions.MySQL_Executor(DB_connector, Utils, Logger, ExceptionsLogger)

CallHandlerExecutor = utils.CallHandlerExecutor(Utils, DB_executor, Keyboards, bot)

# --------------------- Main --------------------- #
@bot.on.private_message(PayloadRule({'command':'start'})) #, func=lambda message: message.text in ['Начать', 'Старт']
async def hi_handler(message: Message):
	await CallHandlerExecutor.StartCommand(message)

@bot.on.private_message(CommandRule('start', ['!'], 0))
async def hi_handler(message: Message):
	await CallHandlerExecutor.GoToStartButton(message)

@bot.on.private_message(CommandRule('menu', ['!'], 0))
async def hi_handler(message: Message):
	await CallHandlerExecutor.OpenMenu(message)

@bot.on.private_message()
async def main_handler(message: Message):
	payload_command = None
	try:
		payload_command = json.loads(message.payload)['command']
	except Exception as e:
		pass
	
	user_id = message.from_id

	user_data = await DB_executor.GetUserData(user_id)

	user_status = user_data['status_mes']#.split('_')

# -------------------------------------- Registration -------------------------------------- #
	if user_status == 'reg_wait_confirm':
		if payload_command == 'yes':
			await CallHandlerExecutor.ChoiceSexSearch(message, user_data)

	if user_status == 'choice_sex_search':
		if payload_command in ['search_woman', 'search_all', 'search_man']:
			await CallHandlerExecutor.AddAboutText(message, user_data, payload_command)

	if user_status == 'add_profile_text':
		if payload_command in ['none_text', None]:
			await CallHandlerExecutor.AddUserSex(message, user_data, payload_command)

	if user_status == 'add_profile_sex':
		if payload_command in ['woman', 'man']:
			await CallHandlerExecutor.AddUserCity(message, user_data, payload_command)
	
	if user_status == 'add_profile_city':
		if payload_command in [None]:
			await CallHandlerExecutor.AddUserAge(message, user_data, payload_command)	

	if user_status == 'add_profile_age':
		if payload_command in [None]:
			await CallHandlerExecutor.CompliteProfile(message, user_data, payload_command)

# -------------------------------------- Menu -------------------------------------- #
	if user_status == 'menu':
		if payload_command == 'profile':
			await CallHandlerExecutor.UserProfile(message, user_data)

		if payload_command == 'start_search':
			await CallHandlerExecutor.GoSearch(message, user_data)

		if payload_command == 'back':
			await CallHandlerExecutor.OpenMenu(message)

# -------------------------------------- Search Users -------------------------------------- #
	if 'in_search' in user_status:
		target_vk_id = int(user_status.split('_')[2])

		if payload_command == 'like_user':
			await CallHandlerExecutor.GiveLike(message, user_data, target_vk_id)
			await CallHandlerExecutor.GoSearch(message, user_data)

		if payload_command == 'dislike_user':
			await CallHandlerExecutor.GiveDislike(message, user_data, target_vk_id)
			await CallHandlerExecutor.GoSearch(message, user_data)

		if payload_command == 'go_sleep':
			await CallHandlerExecutor.GoToSleep(message, target_vk_id)

# -------------------------------------- Start Bot -------------------------------------- #
if __name__ == '__main__':
	try:
		loop.run_until_complete(DB_executor.CheckDataBaseStructure())
		Logger.ConsoleLog('Staring VK Bot...', 'INFO')
		bot.run_forever()
	except Exception as e:
		print(e)
	finally:
		loop.close