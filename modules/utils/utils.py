from datetime import datetime
from random import randint
import asyncio, re, os, aiohttp

from vkbottle import PhotoMessageUploader

class Utils():
	def __init__(self, BOT_VERSION, bot):
		self.BOT_VERSION = BOT_VERSION
		self.bot = bot

	def CheckDataFromDB(self, data) -> bool:
		if data:
			return True
		else:
			return False

	def DateTimeNow(self) -> str:
		return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

	def DateTimeNow_Millies(self) -> str:
		return str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

	def WorkInProgress(self) -> str:
		emojis = ["😔", "😳", "😓", "😐", "😥"]
		random_index = randint(0, 4)

		answer = """Данная команда находится в разработке и временно недоступна {emoji}"""
		answer = answer.replace('{emoji}', emojis[random_index])

		return answer

	def DayTimeText(self) -> str:
		day_time = ''
		hourse = int(datetime.now().strftime("%H"))

		if 0 <= hourse < 6:
			day_time = 'night'
		elif 6 <= hourse < 12:
			day_time = 'morning'
		elif 12 <= hourse < 18:
			day_time = 'day'
		elif 18 <= hourse < 24:
			day_time = 'evening'

		return day_time

	def on_startup(self, Logger) -> None:
		Logger.ConsoleLog("Bot Started!", 'INFO')

	def on_shutdown(self, Logger, ExceptionsLogger) -> None:
		Logger.ConsoleLog("Bot Shutdown!", 'INFO')

		Logger.CloseLogger()
		ExceptionsLogger.CloseLogger()

	def CheckFloat(self, number) -> bool:
		try:
			float(number)
			return True
		except Exception as e:
			return False

	def GetBotVersion(self):
		return self.BOT_VERSION

	async def DownloadPhoto(self, url, photo_path):
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				if response.status == 200:
					content = await response.read()
					with open(photo_path, "wb") as file:
						file.write(content)
					return True
				else:
					return False

class MessageRender():
	def __init__(self, Utils, Keyboards):
		self.Keyboards = Keyboards
		self.Utils = Utils

	def Menu(self, user_data):
		menu_text = """
			Меню
		"""

		return menu_text

class CallHandlerExecutor():
	def __init__(self, Utils, DB_executor, Keyboards, bot):
		self.db = DB_executor
		self.Keyboards = Keyboards
		self.bot = bot
		self.Utils = Utils

		self.MessageRender = MessageRender(Utils, Keyboards)

	async def GoToStartButton(self, message):
		text = "Начало открыто"
		await message.answer(text, keyboard=self.Keyboards.start())

	async def StartCommand(self, message):
		user_id = message.from_id

		if await self.db.CheckUserInDB(user_id):
			query = 'UPDATE users SET status_mes = "menu" WHERE vk_id = ?;'
			await self.db.DataBaseExecute(query, params=(user_id))
		else:
			await self.db.RegUserInDB(user_id)

		user_data = await self.db.GetUserData(user_id)

		if 'reg' not in user_data['status_mes']:
			text = "Открыто главное меню."

			await message.answer(text, keyboard=self.Keyboards.menu())
		else:
			text = "Я помогу найти тебе пару или просто друзей. Можно я задам тебе пару вопросов?"

			await message.answer(text, keyboard=self.Keyboards.yes())

	async def ChoiceSexSearch(self, message, user_data):
		user_id = message.from_id

		text = "Кто тебе интересен?"

		await self.db.CreateUserProfile(user_id)
		await message.answer(text, keyboard=self.Keyboards.sex_choice())

		await self.db.ChangeUserStatus(user_id, 'choice_sex_search')

	async def AddAboutText(self, message, user_data, payload_command):
		user_id = message.from_id

		search_users = payload_command.split('_')[1]

		await self.db.UpdateUserProfile(user_id, search_sex=search_users)

		text = "Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию."

		await message.answer(text, keyboard=self.Keyboards.none_text())

		await self.db.ChangeUserStatus(user_id, 'add_profile_text')

	async def AddUserSex(self, message, user_data, payload_command):
		user_id = message.from_id

		user_text = None
		if payload_command != 'none_text':
			user_text = message.text

		await self.db.UpdateUserProfile(user_id, about=user_text)

		text = "Укажи свой пол."

		await message.answer(text, keyboard=self.Keyboards.sex())

		await self.db.ChangeUserStatus(user_id, 'add_profile_sex')

	async def AddUserCity(self, message, user_data, payload_command):
		user_id = message.from_id

		await self.db.UpdateUserProfile(user_id, sex=payload_command)

		text = "Введите свой город или населенный пункт."

		await message.answer(text, keyboard=self.Keyboards.none())

		await self.db.ChangeUserStatus(user_id, 'add_profile_city')

	async def AddUserAge(self, message, user_data, payload_command):
		user_id = message.from_id

		await self.db.UpdateUserProfile(user_id, city=message.text)

		text = "Введите свой возраст."

		await message.answer(text, keyboard=self.Keyboards.none())

		await self.db.ChangeUserStatus(user_id, 'add_profile_age')

	async def CompliteProfile(self, message, user_data, payload_command):
		user_id = message.from_id
		user_age = None
		try:
			user_age = int(message.text)
		except Exception as e:
			pass

		print(user_age)

		if isinstance(user_age, int) and 0 < user_age < 100:
			users_info = await self.bot.api.users.get(user_id)
			first_name = users_info[0].first_name

			response = await self.bot.api.users.get(user_ids=user_id, fields="photo_max")
			print(response)
			user = response[0]
			photo_url = user.photo_max

			photo_path = f"./users_photos/photo_{user_id}.jpg"

			await self.Utils.DownloadPhoto(photo_url, photo_path)

			await self.db.UpdateUserProfile(user_id, age=user_age, name=first_name, photo_path=photo_path)

			text = "Открыто меню."
	
			await message.answer(text, keyboard=self.Keyboards.menu())
	
			await self.db.ChangeUserStatus(user_id, 'menu')
		else:
			text = "Ошибка повторите ввод!"

			await message.answer(text)

	async def UserProfile(self, message, user_data):
		user_id = message.from_id
		user_profile_data = await self.db.GetUserProfileData(user_id)

		text = f"{user_profile_data['name']}, {user_profile_data['age']}, {user_profile_data['city']}\n\n{user_profile_data['about']}"

		photo_uploader = PhotoMessageUploader(self.bot.api)

		photo = await photo_uploader.upload(
			file_source=user_profile_data['photo_path']
		)

		await message.answer(text, attachment=photo, keyboard=self.Keyboards.profile())

	async def GoSearch(self, message, user_data):
		user_id = message.from_id

		text, photo, new_target_data = await self.NewSearch(message, user_data)

		if text:
			await self.db.ChangeUserStatus(user_id, f'in_search_{new_target_data["vk_id"]}')

			await message.answer(text, attachment=photo, keyboard=self.Keyboards.work_panel())
		else:
			text = "Пока анкеты закончились, приходи позже ;)"
			await self.db.ChangeUserStatus(user_id, 'menu')
			await message.answer(text, keyboard=self.Keyboards.menu())

	async def NewSearch(self, message, user_data):
		user_id = message.from_id

		search_result = await self.db.get_new_connection(user_id)

		if search_result:
			text = f"{search_result['name']}, {search_result['age']}, {search_result['city']}\n\n{search_result['about']}"

			photo_uploader = PhotoMessageUploader(self.bot.api)

			photo = await photo_uploader.upload(
				file_source=search_result['photo_path']
			)

			return text, photo, search_result
		else:
			return None, None, None

	async def GiveLike(self, message, user_data, target_vk_id):
		user_id = message.from_id

		result = await self.db.set_like(user_id, target_vk_id)

		if result:
			text = f"Вау, взаимный лайк, самое время пообщаться ;)\n\nhttps://vk.com/id{target_vk_id}"

			await message.answer(text)

	async def GiveDislike(self, message, user_data, target_vk_id):
		user_id = message.from_id

		await self.db.set_dislike(user_id, target_vk_id)

	async def GoToSleep(self, message, target_vk_id):
		user_id = message.from_id

		await self.db.delete_proposed_connection(user_id, target_vk_id)

		await self.OpenMenu(message)

	async def OpenMenu(self, message):
		user_id = message.from_id

		text = "Вы вернулись в меню."

		await self.db.ChangeUserStatus(user_id, 'menu')

		await message.answer(text, keyboard=self.Keyboards.menu())