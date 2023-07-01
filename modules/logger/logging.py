from datetime import datetime
import os

class Logger():
	def __init__(self, log_path = './', log_file = 'log', log_file_type = 'txt', write_file = False, write_time = True, rewrite_file = False):
		os.system("")

		self.write_file = write_file
		self.write_time = write_time

		log_path_and_file = os.path.abspath(log_path+log_file+'.'+log_file_type)

		if write_file:
			if os.path.isfile(log_path_and_file):
				if rewrite_file:
					file = open(log_path_and_file, 'w')
					file.write(str(datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + "\n")
					self.file = file
				else:
					file = open(log_path_and_file, 'r')
					old_datatime = file.readline().split('\n')[0]
					file.close()
					old_file = log_path_and_file
					new_file = os.path.join(os.path.abspath(log_path+log_file+' - '+old_datatime+'.'+log_file_type))
					os.rename(old_file, new_file)
					file = open(log_path_and_file, 'w')
					file.write(str(datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + "\n")
					self.file = file
			else:
				file = open(log_path_and_file, 'w')
				file.write(str(datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + "\n")
				self.file = file

			self.log_file = log_file+'.'+log_file_type

	def ConsoleLog(self, message, msg_type = 'INFO'):
		console_mes = ""
	
		if self.write_time:
			console_mes = "[" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		else:
			console_mes = "["

		if msg_type == 'INFO':
			console_mes += "]\033[94m INFO\033[0m - "
		elif msg_type == 'WARNING':
			console_mes += "]\033[93m WARNING\033[0m - "
		elif msg_type == 'ERROR':
			console_mes += "]\033[91m ERROR\033[0m - "
		elif msg_type == 'SUCCESS':
			console_mes += "]\033[92m SUCCESS\033[0m - "
		elif msg_type == 'MESSAGE':
			console_mes += "] - "
	
		console_mes += str(message)

		if self.write_file:
			self.FileLog(message, msg_type=msg_type)
		print(console_mes)

	def FileLog(self, message, msg_type = 'INFO'):
		file_msg = ""
	
		if self.write_time:
			file_msg = "[" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		else:
			file_msg = "["

		if msg_type == 'INFO':
			file_msg += "] INFO - "
		elif msg_type == 'WARNING':
			file_msg += "] WARNING - "
		elif msg_type == 'ERROR':
			file_msg += "] ERROR - "
		elif msg_type == 'SUCCESS':
			file_msg += "] SUCCESS - "
		elif msg_type == 'MESSAGE':
			file_msg += "] - "
	
		file_msg += str(message)		

		try:
			self.file.write(file_msg + "\n")
			return True
		except Exception as e:
			return e

	def CloseLogger(self):
		self.file.close()