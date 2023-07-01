from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlalchemy.sql import text
import sqlalchemy.pool as pool
from typing import Any, Optional, Tuple, List
import sqlalchemy
import asyncio

class MySQL_Connect:
	def __init__(self, host: str, port: int, user: str, password: str, db: str, pool_size: Optional[int] = 5, logging: Optional[bool] = True):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.db = db
		self.engine = create_async_engine(self.get_connection_string(), poolclass=pool.QueuePool, pool_size=pool_size, echo=False)
		self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

	def get_connection_string(self) -> str:
		#return f'mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'
		return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'

	async def create_table(self, table_class) -> bool:
		try:
			async with self.engine.begin() as conn:
				await conn.run_sync(table_class.__table__.create)
			return True
		except Exception as e:
			print(e)
			return False

	async def check_table_existence(self, table_name: str) -> bool:
		async with self.engine.connect() as conn:
			tables = await conn.run_sync(
				lambda sync_conn: inspect(sync_conn).get_table_names()
			)

			if table_name in tables:
				return True
			else:
				return False

	async def execute_query(self, query: str, params=None, commit: bool = True):
		query = text(query)
		
		async with self.Session() as session:
			async with session.begin():
				try:
					result = await session.execute(query, params)
				except sqlalchemy.exc.OperationalError:
					result = await session.execute(query, params)

				if commit:
					await session.commit()

				return result

	def generation_query(self, query, params):
		json_params = {}
		for i in range(len(params)):
			query = query.replace('?', f':p{i}', 1)
			json_params.update({f'p{i}' : params[i]})

		return query, json_params

	def get_session(self):
		session = self.Session()

		return session