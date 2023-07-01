from vkbottle import Keyboard, KeyboardButtonColor, Text

class Keyboards():
	def menu(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("👤Моя анкета", payload={"command": "profile"}), color=KeyboardButtonColor.POSITIVE)
				.add(Text("🔍Начать поиск", payload={"command": "start_search"}), color=KeyboardButtonColor.NEGATIVE)
		)

		return keyboard.get_json()

	def profile(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("Заполнить анкету заново", payload={"command": "rework_profile"}), color=KeyboardButtonColor.SECONDARY)
				.row()
				.add(Text("Изменить фото", payload={"command": "change_profile_photo"}), color=KeyboardButtonColor.SECONDARY)
				.row()
				.add(Text("Изменить текст анкеты", payload={"command": "change_profile_text"}), color=KeyboardButtonColor.SECONDARY)
				.row()
				.add(Text("Выйти", payload={"command": "back"}), color=KeyboardButtonColor.NEGATIVE)
		)

		return keyboard.get_json()

	def work_panel(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("❤", payload={"command": "like_user"}), color=KeyboardButtonColor.POSITIVE)
				.add(Text("👎", payload={"command": "dislike_user"}), color=KeyboardButtonColor.NEGATIVE)
				.row()
				.add(Text("Отдохнуть", payload={"command": "go_sleep"}), color=KeyboardButtonColor.SECONDARY)
		)

		return keyboard.get_json()

	def sex_choice(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("Девушки", payload={"command": "search_woman"}), color=KeyboardButtonColor.SECONDARY)
				.add(Text("Всё равно", payload={"command": "search_all"}), color=KeyboardButtonColor.SECONDARY)
				.add(Text("Парни", payload={"command": "search_man"}), color=KeyboardButtonColor.SECONDARY)
		)

		return keyboard.get_json()

	def sex(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("Я девушка", payload={"command": "woman"}), color=KeyboardButtonColor.SECONDARY)
				.add(Text("Я парень", payload={"command": "man"}), color=KeyboardButtonColor.SECONDARY)
		)

		return keyboard.get_json()

	def yes(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("Да!", payload={"command": "yes"}), color=KeyboardButtonColor.POSITIVE)
		)

		return keyboard.get_json()

	def none_text(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("Без текста", payload={"command": "none_text"}), color=KeyboardButtonColor.SECONDARY)
		)

		return keyboard.get_json()

	def start(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
				.add(Text("Начать", payload={"command": "start"}), color=KeyboardButtonColor.SECONDARY)
		)

		return keyboard.get_json()

	def none(self):
		keyboard = (
			Keyboard(one_time=False, inline=False)
		)

		return keyboard.get_json()

	def settings(self):
		pass