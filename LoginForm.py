from tkinter import *
from tkinter import messagebox
import sqlite3 as db
from MainForm import Main
from datetime import datetime


class Login(object):
	#tao 2 bien cuc bo de chua username va password
	user_name = ""
	pass_word = ""	

	#tao form dang nhap
	def __init__(self):
		self.TB_Sign = 'sign'
		self.TB_Account= 'Account'
		self.TB_Account_Info = 'Account_Info'

		self.LoginForm = Tk()
		self.LoginForm.geometry("250x170")
		windownWidth = self.LoginForm.winfo_reqwidth()
		windownHeight = self.LoginForm.winfo_reqheight()

		posRight = int(self.LoginForm.winfo_screenwidth()/2 - windownWidth/2) 
		posDown = int(self.LoginForm.winfo_screenheight()/2 - windownHeight/2) 

		self.LoginForm.geometry("+{}+{}".format(posRight,posDown))
		self.LoginForm.title("Đăng nhập")
	
		
		Label(self.LoginForm,text = "",).pack()
		Label(self.LoginForm,text = "Tên đăng nhập: ").pack()
		self.txtuser_name = Entry(self.LoginForm,width=30)
		self.txtuser_name.pack()

		Label(self.LoginForm,text = "Mật khẩu: ").pack()
		self.txtpass_word = Entry(self.LoginForm,width=30,show="*")
		self.txtpass_word.pack()

		frame_For_Button = Frame(self.LoginForm)
		frame_For_Button.pack()
		Label(frame_For_Button,text = " ").pack()

		self.btnSubmit = Button(frame_For_Button,text="Đăng nhập",command=self.check_Account,width=10)
		self.btnSubmit.pack(side=LEFT,padx=2,pady=2)

		self.btnEXit = Button(frame_For_Button,text="Thoát",command=self.exit,width=10)
		self.btnEXit.pack(side=LEFT,padx=2,pady=2)

		mainloop()

	#ham samloz cua t. khong can quan tam den
	def changeTextForFilIntoQuery(self,ValueCondition):
		return '"'+ValueCondition+'"'

	#ham thuc thi cau lenh
	def execute_Query(self,Query):
		conn = db.connect(DBName)
		cur = conn.cursor()
		cur.execute(Query)
		conn.commit()
		data = cur.fetchall()
		cur.close()
		conn.close()
		return data


	def exit(self):
		msgBox = messagebox.askquestion("Thông báo","Bạn có muốn thoát không!")
		if(msgBox == 'yes'):
			self.LoginForm.destroy()

	#ham lay user_name va password do nguoi dung nhap vao va gan len 2 bien cuc bo
	def getValue(self):
		self.user_name = self.txtuser_name.get()
		self.pass_word = self.txtpass_word.get()


	# check account
	def check_Account(self):
		self.getValue()

		#2 dong nay khong can quan tam
		user_name = self.changeTextForFilIntoQuery(self.user_name)
		pass_word = self.changeTextForFilIntoQuery(self.pass_word)

		Query = ' SELECT * FROM Account WHERE user_name = '+user_name+' AND pass_word = '+pass_word 
		data = self.execute_Query(Query)
		if(len(data) > 0):
			self.LoginForm.destroy()
			self.log_Time_In()
			Main(self.user_name)
		else:
			messagebox.showinfo("Thông báo","Sai thông tin tài khoản hoặc mật khẩu")


	def insertNULL(self,TableName, ArrayValue):
		stri = self.arrToString(ArrayValue)
		stri = "NULL,"+stri
		Query = "INSERT INTO "+TableName+" VALUES ( "+stri+" )"
		self.execute_Query(Query)
		return True	

	def arrToString(self,array):
		stri = ""
		for x in array:
			stri += '"'+x+'"'
			stri = stri.replace("\"\"","\",\"")
		return stri	

	def log_Time_In(self):
		now = datetime.now()
		time = now.strftime("%H:%M:%S %d/%m/%Y")

		ArrayValue = [self.user_name,"IN",time]
		self.insertNULL(self.TB_Sign,ArrayValue)


if __name__ == '__main__':
	DBName = "DB/Account.db"
	Login()











