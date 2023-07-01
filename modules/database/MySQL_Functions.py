from datetime import datetime
import sqlalchemy, random
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy import Column, String, Integer, Double, DateTime, ForeignKey, Boolean
from sqlalchemy import select, join, or_, and_, delete, update

Base = declarative_base()

class Users(Base):
	__tablename__ = 'users'
	vk_id = Column(Integer, primary_key=True)
	reg_datetime = Column(DateTime, default=None)
	last_use = Column(DateTime, default=None)
	status_mes = Column(String(255), default=None)
	ban = Column(Integer, default=0)

class Users_Profiles(Base):
	__tablename__ = 'users_profiles'
	vk_id = Column(Integer, ForeignKey('users.vk_id'), primary_key=True)
	name = Column(String(255))
	about = Column(String(255))
	age = Column(Integer)
	city = Column(String(255))
	photo_path = Column(String(255))
	sex = Column(String(255))
	search_sex = Column(String(255))

	proposals = relationship('ProposedConnection', primaryjoin="or_(Users_Profiles.vk_id==ProposedConnection.user_a_vk_id, Users_Profiles.vk_id==ProposedConnection.user_b_vk_id)", backref='user_profile')

class ProposedConnection(Base):
	__tablename__ = 'proposed_connections'
	user_a_vk_id = Column(Integer, ForeignKey('users_profiles.vk_id'), primary_key=True)
	user_b_vk_id = Column(Integer, ForeignKey('users_profiles.vk_id'), primary_key=True)
	proposal_date = Column(DateTime)
	liked = Column(Boolean, default=False)
	disliked = Column(Boolean, default=False)

tables = {
	"users": Users(),
	"users_profiles": Users_Profiles(),
	"proposed_connections": ProposedConnection()
}

class MySQL_Executor:
	def __init__(self, db_connector, Utils, Logger, ExceptionsLogger):
		self.db = db_connector
		self.Utils = Utils
		self.Logger = Logger
		self.ExceptionsLogger = ExceptionsLogger

	def DateTimeNow(self) -> str:
		return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

	async def CheckDataBaseStructure(self):
		global tables

		for table_name in tables.keys():
			result = await self.db.check_table_existence(table_name)

			if not result:
				status = await self.db.create_table(tables[table_name])
				if status:
					self.ExceptionsLogger.ConsoleLog(f'Table {table_name} not found, the new table has been created successfully.', 'WARNING')
				else:
					self.ExceptionsLogger.ConsoleLog(f'Table {table_name} not found, the new table not created.', 'ERROR')
			else:
				self.ExceptionsLogger.ConsoleLog(f'Table {table_name} found.', 'SUCCESS')

	async def DataBaseExecute(self, query, params=(), update_last_use=False, user_id=None, _fetchall=True):
		if type(params) != tuple:
			params = [params]
		params=list(params)

		if update_last_use:
			query += '; UPDATE users SET last_use = ? WHERE vk_id = ?;'
			params.append(self.DateTimeNow())
			params.append(user_id)

		query, params = self.db.generation_query(query, params)
		data = await self.db.execute_query(query, params)

		if _fetchall:
			try:
				data = data.fetchall()
			except sqlalchemy.exc.ResourceClosedError:
				self.ExceptionsLogger.ConsoleLog(f"DataBase Fetchall: This result object does not return rows.", 'WARNING')
				data = ()
			except Exception as e:
				self.ExceptionsLogger.ConsoleLog(f"Unknown error: {e}", 'ERROR')
				data = ()

		return data

	async def CheckUserInDB(self, user_id):
		data = await self.DataBaseExecute('SELECT * FROM users WHERE vk_id = ?', (user_id))
		return self.Utils.CheckDataFromDB(data)

	async def RegUserInDB(self, user_id) -> None:
		await self.DataBaseExecute(
			'INSERT INTO users (vk_id, reg_datetime, status_mes, last_use, ban) VALUES (?, ?, ?, ?, ?)',  \
			params=(user_id, self.DateTimeNow(), 'reg_wait_confirm', self.DateTimeNow(), 0)
		)

	async def GetUserData(self, user_id) -> dict:
		user_data = await self.DataBaseExecute('SELECT * FROM users WHERE vk_id = ?', (user_id), update_last_use=True, user_id=user_id, _fetchall=False)

		coloumns_names = user_data.keys()
		data = user_data.fetchall()[0]

		user_data_json = {}
		for x, coloumn_name in enumerate(coloumns_names):
			user_data_json.update({coloumn_name : data[x]})

		return user_data_json

	async def ChangeUserStatus(self, user_id, new_status):
		await self.DataBaseExecute('UPDATE users SET status_mes = ? WHERE vk_id = ?', (new_status, user_id))

	async def CreateUserProfile(self, user_id):
		await self.DataBaseExecute(
			'INSERT INTO users_profiles (vk_id) VALUES (?)',  \
			params=(user_id)
		)

	async def GetUserProfileData(self, user_id) -> dict:
		user_data = await self.DataBaseExecute('SELECT * FROM users_profiles WHERE vk_id = ?', (user_id), update_last_use=False, user_id=user_id, _fetchall=False)

		coloumns_names = user_data.keys()
		data = user_data.fetchall()[0]

		user_data_json = {}
		for x, coloumn_name in enumerate(coloumns_names):
			user_data_json.update({coloumn_name : data[x]})

		return user_data_json

	async def UpdateUserProfile(self, user_id, name=None, about=None, age=None, city=None, photo_path=None, sex=None, search_sex=None):
		user_data = await self.GetUserProfileData(user_id)

		name = name or user_data['name']
		about = about or user_data['about']
		age = age or user_data['age']
		city = city or user_data['city']
		photo_path = photo_path or user_data['photo_path']
		sex = sex or user_data['sex']
		search_sex = search_sex or user_data['search_sex']

		await self.DataBaseExecute(
			'UPDATE users_profiles SET name = ?, about = ?, age = ?, city = ?, photo_path = ?, sex = ?, search_sex = ? WHERE vk_id = ?',
			(name, about, age, city, photo_path, sex, search_sex, user_id)
		)

	async def get_new_connection(self, user_id):
		session = self.db.get_session()

		user_profile = await self.GetUserProfileData(user_id)

		search_city = user_profile['city']
		search_age = user_profile['age']
		search_sex = user_profile['search_sex']

		min_age = search_age - 2
		max_age = search_age + 2

		available_users = None
		if search_sex == 'all':
			available_users = await session.execute(
				select(Users_Profiles)
				.join(
					ProposedConnection,
					or_(
						Users_Profiles.vk_id != ProposedConnection.user_a_vk_id,
						Users_Profiles.vk_id == ProposedConnection.user_b_vk_id
					),
					isouter=True
				)
				.filter(ProposedConnection.user_a_vk_id == None)
				.filter(ProposedConnection.user_b_vk_id == None)
				.filter(Users_Profiles.city == search_city)
				.filter(and_(
					Users_Profiles.age >= min_age,
					Users_Profiles.age <= max_age
				))
				.filter(or_(
					Users_Profiles.sex == 'man',
					Users_Profiles.sex == 'woman'
				))
			)
		else:
			available_users = await session.execute(
				select(Users_Profiles)
				.join(
					ProposedConnection,
					or_(
						Users_Profiles.vk_id != ProposedConnection.user_a_vk_id,
						Users_Profiles.vk_id == ProposedConnection.user_b_vk_id
					),
					isouter=True
				)
				.filter(ProposedConnection.user_a_vk_id == None)
				.filter(ProposedConnection.user_b_vk_id == None)
				.filter(Users_Profiles.city == search_city)
				.filter(and_(
					Users_Profiles.age >= min_age,
					Users_Profiles.age <= max_age
				))
				.filter(Users_Profiles.sex == search_sex)
			)

		available_users = [row[0].__dict__ for row in available_users.fetchall()]

		if not available_users:
			await session.close()
			return None

		filtered_users = []
		for user in available_users:
			connection = await session.execute(
				select(ProposedConnection)
				.where(or_(
					ProposedConnection.user_a_vk_id == user_id,
					ProposedConnection.user_b_vk_id == user_id
				))
				.where(or_(
					ProposedConnection.user_a_vk_id == user['vk_id'],
					ProposedConnection.user_b_vk_id == user['vk_id']
				))
			)

			result = connection.fetchone()

			if result:
				if result[0].liked:
					filtered_users.append(user)
			else:
				filtered_users.append(user)

		if not filtered_users:
			await session.close()
			return None

		chosen_user = random.choice(filtered_users)
		proposal_date = self.Utils.DateTimeNow()

		proposal = ProposedConnection(user_a_vk_id=user_id, user_b_vk_id=chosen_user['vk_id'], proposal_date=proposal_date)
		session.add(proposal)
		await session.commit()

		await session.close()

		return chosen_user

	async def set_like(self, user_vk_id: int, liked_user_vk_id: int):
		session = self.db.get_session()

		user_profile = await self.GetUserProfileData(user_vk_id)
		liked_user_profile = await self.GetUserProfileData(liked_user_vk_id)

		connection = await session.execute(
			select(ProposedConnection)
			.where(or_(
				ProposedConnection.user_a_vk_id == user_profile['vk_id'],
				ProposedConnection.user_b_vk_id == user_profile['vk_id']
			))
			.where(or_(
				ProposedConnection.user_a_vk_id == liked_user_profile['vk_id'],
				ProposedConnection.user_b_vk_id == liked_user_profile['vk_id']
			))
			.limit(1)
		)

		result = connection.fetchone()

		if result:
			await session.execute(
				update(ProposedConnection)
				.where(or_(
					ProposedConnection.user_a_vk_id == user_profile['vk_id'],
					ProposedConnection.user_b_vk_id == user_profile['vk_id']
				))
				.where(or_(
					ProposedConnection.user_a_vk_id == liked_user_profile['vk_id'],
					ProposedConnection.user_b_vk_id == liked_user_profile['vk_id']
				))
				.values(liked=True)
			)

			await session.commit()

			mutual_like = await session.execute(
				select(ProposedConnection)
				.where(ProposedConnection.user_a_vk_id == liked_user_profile['vk_id'])
				.where(ProposedConnection.user_b_vk_id == user_profile['vk_id'])
				.where(ProposedConnection.liked == True)
				.limit(1)
			)

			await session.close()

			mutual_like_result = mutual_like.fetchone()
			if mutual_like_result:
				return True

		return False

	async def set_dislike(self, user_vk_id: int, disliked_user_vk_id: int):
		session = self.db.get_session()

		user_profile = await self.GetUserProfileData(user_vk_id)
		disliked_user_profile = await self.GetUserProfileData(disliked_user_vk_id)

		await session.execute(
			update(ProposedConnection)
			.where(or_(
				ProposedConnection.user_a_vk_id == user_profile['vk_id'],
				ProposedConnection.user_b_vk_id == user_profile['vk_id']
			))
			.where(or_(
				ProposedConnection.user_a_vk_id == disliked_user_profile['vk_id'],
				ProposedConnection.user_b_vk_id == disliked_user_profile['vk_id']
			))
			.values(disliked=True)
		)

		await session.commit()

		await session.close()

	async def delete_proposed_connection(self, user_a_vk_id, user_b_vk_id):
		session = self.db.get_session()

		await session.execute(
			delete(ProposedConnection)
			.where(
				or_(
					and_(
						ProposedConnection.user_a_vk_id == user_a_vk_id,
						ProposedConnection.user_b_vk_id == user_b_vk_id
					),
					and_(
						ProposedConnection.user_a_vk_id == user_b_vk_id,
						ProposedConnection.user_b_vk_id == user_a_vk_id
					)
				)
			)
		)

		await session.commit()

		await session.close()