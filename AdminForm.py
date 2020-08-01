from tkinter import *
from tkinter import messagebox
import sqlite3 as db
from tkinter import ttk
import datetime




class Admin(object):
	__user_name = ""
	def getUser_Name(self):
		return self.__user_name
	def __init__(self,user_name):
		self.__user_name = user_name
		self.DBName = "DB/Account.db"
		self.TB_Sign = 'sign'
		self.TB_Account= 'Account'
		self.TB_Account_Info = 'Account_Info'

		self.AdminForm = Tk()
		user_name_login = self.getUser_Name()
		self.AdminForm.title("Admin ("+user_name_login+")")
		self.x = 1200
		self.y = 500
		self.AdminForm.geometry(str(self.x)+"x"+str(self.y))
		self.AdminForm.geometry("+100+100")


		toolbar = self.create_Toolbar_Edit_Delete(self.AdminForm,self.exit)


		Tabcontrol_Main = ttk.Notebook()

		#Tab Sign
#====================================================================================
		Tab_Manage = ttk.Frame(Tabcontrol_Main)
		Tabcontrol_Main.add(Tab_Manage,text='Sign')


		#create Toolbar

		toolbar_Sign_Btn = Frame(Tab_Manage,bg="gray")
		toolbar_Sign_Btn.pack(side=TOP,fill=X)

		toolbar_Sign_Btn1 = Frame(toolbar_Sign_Btn,bg='gray',width=self.x/3)
		toolbar_Sign_Btn1.pack()

		
		btnShow_Sign = Button(toolbar_Sign_Btn1,text="Refesh",width=30,command=self.show_Data_For_Sign)
		btnShow_Sign.pack(side=LEFT,padx=2,pady=2)

		btn_Find_All_Sign = Button(toolbar_Sign_Btn1,text="Tìm kiếm",width=30,command=self.finding_All_For_Sign)
		btn_Find_All_Sign.pack(side=LEFT, padx=4,pady=4)



		toolbar_Time_IO_Edit_Text = Frame(Tab_Manage,bg="gray")
		toolbar_Time_IO_Edit_Text.pack(side=TOP,fill=X)

		toolbar_Time_IO_Edit_Text1 = Frame(toolbar_Time_IO_Edit_Text,bg='gray',width=self.x/3)
		toolbar_Time_IO_Edit_Text1.pack()


		Label(toolbar_Time_IO_Edit_Text1,text="USER NAME: ",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtUser_Name_For_Find_Sign = Entry(toolbar_Time_IO_Edit_Text1)
		self.txtUser_Name_For_Find_Sign.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="SIGN: ",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtSign_For_Find_Sign = Entry(toolbar_Time_IO_Edit_Text1)
		self.txtSign_For_Find_Sign.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Ngày",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtDay_For_Find_Sign = Entry(toolbar_Time_IO_Edit_Text1,width=7)
		self.txtDay_For_Find_Sign.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Tháng",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtMonth_For_Find_Sign = Entry(toolbar_Time_IO_Edit_Text1,width=7)
		self.txtMonth_For_Find_Sign.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Năm",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtYear_For_Find_Sign = Entry(toolbar_Time_IO_Edit_Text1,width=7)
		self.txtYear_For_Find_Sign.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)


		frame_For_Data_Manage = Frame(Tab_Manage,bg="gray")
		frame_For_Data_Manage.pack(fill='both')

		self.Treeview_For_Sign = ttk.Treeview(Tab_Manage,show='headings', column=(1,2,3,4,5),height=self.y)
		self.Treeview_For_Sign.heading(1,text='USER NAME')
		self.Treeview_For_Sign.heading(2,text='NAME')
		self.Treeview_For_Sign.heading(3,text='PERMISSION')
		self.Treeview_For_Sign.heading(4,text='Sign')
		self.Treeview_For_Sign.heading(5,text='TIME')
		self.Treeview_For_Sign.pack(fill='both',padx=6,pady=6)
		
#==================================================================================== END Tab Sign
		

		#Tab Account
#====================================================================================
		Tab_Accoun_Manage = ttk.Frame(Tabcontrol_Main)
		Tabcontrol_Main.add(Tab_Accoun_Manage,text="Account")

		Tab_Account = ttk.Notebook(Tab_Accoun_Manage)


		#Tab Account
		#==============================
		Tab_Account_Account = ttk.Frame(Tab_Account)
		Tab_Account.add(Tab_Account_Account,text="Account")


		self.frame_Data = Frame(Tab_Account_Account,height=self.y,width=self.x*6/10)
		self.frame_Data.pack(padx=6,pady=6,side=LEFT)

		self.frame_Edit = Frame(Tab_Account_Account,height=self.y,width=self.x*4/10)
		self.frame_Edit.pack(padx=6,pady=6,side=LEFT)

		#create Treeview de hien thi data 
		self.Treeview = ttk.Treeview(self.frame_Data,column=(1,2,3), show="headings", height=self.y)
		self.Treeview.heading(1,text="USER NAME")
		self.Treeview.heading(2,text="PASS WORD")
		self.Treeview.heading(3,text="PERMISSION")
		self.Treeview.pack()
		#-------END Tree View


		toolbar1 = Frame(self.frame_Edit,bg="gray")
		btnShow = Button(toolbar1,text="Show All",width=40,command=self.show_Data_For_Account)
		btnShow.pack(padx=2,pady=2)
		toolbar1.pack(side=TOP,fill=X)

		toolbar2 = Frame(self.frame_Edit,bg="gray")
		btnFinding = Button(toolbar2,text="Tìm kiếm",width=40,command=self.finding_For_Account)
		btnFinding.pack(side=LEFT,padx=2,pady=2)
		btnAdd = Button(toolbar2,text="Thêm",width=self.x,command=self.add_For_Account)
		btnAdd.pack(side=LEFT,padx=2,pady=2)
		toolbar2.pack(side=TOP,fill=X)

		toolbar3 = Frame(self.frame_Edit,bg="gray")
		btnEdit = Button(toolbar3,text="Sửa",width=40,command=self.edit_For_Account)
		btnEdit.pack(side=LEFT,padx=2,pady=2)
		btnDelete = Button(toolbar3,text="Xóa",width=self.x,command=self.delete_For_Account)
		btnDelete.pack(side=LEFT,padx=2,pady=2)
		toolbar3.pack(side=TOP,fill=X)


		#create Form edit 
		Label(self.frame_Edit,text="User Name:",width=self.x).pack()
		self.txtUser_Name = Entry(self.frame_Edit,width=self.x)
		self.txtUser_Name.pack(padx=4,pady=2,side=TOP)

		Label(self.frame_Edit,text="Pass Word:",width=self.x).pack()
		self.txtPass_Word = Entry(self.frame_Edit,width=self.x)
		self.txtPass_Word.pack(padx=4,pady=2,side=TOP)

		Label(self.frame_Edit,text="Quyền:",width=self.x).pack()
		self.txtPermission = Entry(self.frame_Edit,width=self.x)
		self.txtPermission.pack(padx=4,pady=2,side=TOP)

		#------end Form edit 
		#create Frame for note
		Label(self.frame_Edit,text="(*) Để tìm kiếm, xóa \nvui lòng nhâp User Name của User vào ô User Name!\n").pack()
		Label(self.frame_Edit,text="(*) Vui lòng điền đầy đủ thông tin \nvào các ô để có thể chỉnh sửa!\n").pack()
		Label(self.frame_Edit,text="(*) Quyền vui lòng điền 1 (admin) hoặc 0 (nhân viên) !\n").pack()
		#--------end Frame for note

		#====================================================End Tab Account



		#tab Info
		#====================================================
		Tab_Account_Info = ttk.Frame(Tab_Account)
		Tab_Account.add(Tab_Account_Info,text="Info")

		Frame_For_Data_Account_Info = Frame(Tab_Account_Info,width=int(self.x*6/10))
		Frame_For_Data_Account_Info.pack(side=LEFT)

		self.Treeview_For_Account_Info = ttk.Treeview(Frame_For_Data_Account_Info,show='headings',column=(1,2,3,4),height=self.y)

		self.Treeview_For_Account_Info.heading(1,text='USER NAME')
		self.Treeview_For_Account_Info.heading(2,text='NAME')
		self.Treeview_For_Account_Info.heading(3,text='SEX')
		self.Treeview_For_Account_Info.heading(4,text='BIRTH DAY')

		self.Treeview_For_Account_Info.pack(fill='both',padx=6,pady=6)


		Frame_For_Edit_Account_Info = Frame(Tab_Account_Info,width=int(self.x))
		Frame_For_Edit_Account_Info.pack(side=LEFT)



		toolbar1 = Frame(Frame_For_Edit_Account_Info,bg="gray")
		btnShow = Button(toolbar1,text="Show All",width=25,command=self.show_Data_For_Account_Info)
		btnShow.pack(padx=2,pady=2)
		toolbar1.pack(side=TOP,fill=X)

		toolbar2 = Frame(Frame_For_Edit_Account_Info,bg="gray")
		btnFinding = Button(toolbar2,text="Tìm kiếm",width=27,command=self.finding_For_Account_Info)
		btnFinding.pack(side=LEFT,padx=2,pady=2)
		btnAdd = Button(toolbar2,text="Thêm",width=self.x,command=self.add_For_Account_Info)
		btnAdd.pack(side=LEFT,padx=2,pady=2)
		toolbar2.pack(side=TOP,fill=X)

		toolbar3 = Frame(Frame_For_Edit_Account_Info,bg="gray")
		btnEdit = Button(toolbar3,text="Sửa",width=27,command=self.edit_For_Account_Info)
		btnEdit.pack(side=LEFT,padx=2,pady=2)
		btnDelete = Button(toolbar3,text="Xóa",width=self.x,command=self.delete_For_Account_Info)
		btnDelete.pack(side=LEFT,padx=2,pady=2)
		toolbar3.pack(side=TOP,fill=X)


		#create Form edit 
		Label(Frame_For_Edit_Account_Info,text="User Name:",width=self.x).pack()
		self.txtUser_Name_Of_Account_info = Entry(Frame_For_Edit_Account_Info,width=self.x)
		self.txtUser_Name_Of_Account_info.pack(padx=4,pady=2,side=TOP)

		Label(Frame_For_Edit_Account_Info,text="Name:",width=self.x).pack()
		self.txtName_Of_Account_info = Entry(Frame_For_Edit_Account_Info,width=self.x)
		self.txtName_Of_Account_info.pack(padx=4,pady=2,side=TOP)

		Label(Frame_For_Edit_Account_Info,text="Sex:",width=self.x).pack()
		self.txtSex_Of_Account_info = Entry(Frame_For_Edit_Account_Info,width=self.x)
		self.txtSex_Of_Account_info.pack(padx=4,pady=2,side=TOP)


		Label(Frame_For_Edit_Account_Info,text="Birthday:",width=self.x).pack()
		self.txtBirthday_Of_Account_info = Entry(Frame_For_Edit_Account_Info,width=self.x)
		self.txtBirthday_Of_Account_info.pack(padx=4,pady=2,side=TOP)


		#------end Form edit 
		#create Frame for note
		Label(Frame_For_Edit_Account_Info,text="(*) Để tìm kiếm, xóa \nvui lòng nhâp User Name của User vào ô User Name!\n").pack()
		Label(Frame_For_Edit_Account_Info,text="(*) Vui lòng điền đầy đủ thông tin \nvào các ô để có thể chỉnh sửa!\n").pack()
		Label(Frame_For_Edit_Account_Info,text="(*) Ngày sinh hợp lệ VD: 01/01/2000\n").pack()
		#--------end Frame for note

		#=================================================End Tab info


		Tab_Account.pack(fill='both')
#====================================================================================END Tab Manage


		Tabcontrol_Main.pack(fill='both')





		self.show_Data_For_Account()
		self.show_Data_For_Account_Info()
		self.show_Data_For_Sign()

		mainloop()












	def create_Toolbar_Edit_Delete(self,name,command1):
		width = 20
		toolbar_user_info = Frame(name,bg="gray")
		btnExit = Button(toolbar_user_info,text="Quay lại cửa sổ quản lý",width=width,command=command1)
		btnExit.pack(side=RIGHT,padx=2,pady=2)
		toolbar_user_info.pack(side=TOP,fill=X)

		

		#ham samloz cua t. khong can quan tam den
	def changeTextForFilIntoQuery(self,ValueCondition):
		return '"'+ValueCondition+'"'


	def exit(self):
		from MainForm import Main
		msgBox = messagebox.askquestion("Thông báo","Bạn có muốn quay lại cửa sổ quản lý không!")
		if(msgBox == 'yes'):
			self.AdminForm.destroy()
			Main(self.getUser_Name())



	#select de lay data trong database
	def take_data(self,tableName):
		tableName = self.changeTextForFilIntoQuery(tableName)
		Query = "SELECT * FROM "+tableName
		return self.execute_Query(Query)

	#show du lieu cua bang Account
	def show_Data_For_Account(self):
		children = self.Treeview.get_children()
		for x in children:
			self.Treeview.delete(x)
		for x in self.take_data(self.TB_Account):
			self.Treeview.insert('','end',values=x)



	#ham thuc thi cau lenh
	def execute_Query(self,Query):
		conn = db.connect(self.DBName)
		cur = conn.cursor()
		cur.execute(Query)
		conn.commit()
		data = cur.fetchall()
		cur.close()
		conn.close()
		return data


	def finding(self,tableName,user_name):
		tableName = self.changeTextForFilIntoQuery(tableName)
		user_name = self.changeTextForFilIntoQuery(user_name)
		Query = " SELECT * FROM "+tableName+" WHERE user_name = "+user_name
		return self.execute_Query(Query)


	def finding_For_Account(self):
		user_name = self.txtUser_Name.get().strip()
		if (user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name)):
				children = self.Treeview.get_children()
				for x in children:
					self.Treeview.delete(x)
				data = self.finding(self.TB_Account,user_name)
				for x in data:
					self.Treeview.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để tìm kiếm")


	#ham kiem tra xem user co ID duoc nhap vao co tom tai khong
	def check_Exists_User_Name(self,tableName,user_name):
		ListUser = self.take_data(tableName)
		for x in ListUser:	
			if(user_name == x[0]):
				return True
		return False

	#Ham chinh sua thong tin cho table Registered_Info
	def edit_For_Account(self):
		TB_Account = self.TB_Account
		TB_Account = self.changeTextForFilIntoQuery(TB_Account)
		user_name = self.txtUser_Name.get().strip()
		pass_word = self.txtPass_Word.get().strip()
		permission = self.txtPermission.get().strip()

		if(user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name)):
				if(pass_word):
					if(permission):
						msg = messagebox.askquestion("","Bạn có chắc muốn thay đổi thông tin ?")
						if(msg == 'yes'):
							user_name = self.changeTextForFilIntoQuery(user_name)
							pass_word = self.changeTextForFilIntoQuery(pass_word)
							permission = self.changeTextForFilIntoQuery(permission)
							Query = " UPDATE "+TB_Account+" SET user_name = "+user_name+", pass_word = "+pass_word+", permission = "+permission+" WHERE user_name = "+user_name
							self.execute_Query(Query)
							messagebox.showinfo("","Cập nhật thông tin thành công!")
							self.show_Data_For_Account()
					else:
						messagebox.showinfo("","Quyền tài khoản không được để trống")
				else:
					messagebox.showinfo("","Vui lòng điền mật khẩu !")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại USER NAME")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để thực hiện sửa thông tin")

	def delete_For_Account(self):
		TB_Account = self.TB_Account
		TB_Account = self.changeTextForFilIntoQuery(TB_Account)
		TB_Account_Info = self.TB_Account_Info
		TB_Account_Info = self.changeTextForFilIntoQuery(TB_Account_Info)

		user_name = self.txtUser_Name.get().strip()
		if(user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name)):
				if(user_name != "admin"):
					msg = messagebox.askquestion("","Bạn có chắc muôn xóa tất cả thông tin của User: \"{}\" ?".format(user_name))
					if(msg == 'yes'):
						user_name = self.changeTextForFilIntoQuery(user_name)
						Query1 = " DELETE FROM "+TB_Account_Info+" WHERE user_name = "+user_name
						self.execute_Query(Query1)
						messagebox.showinfo("","Đã xóa tất cả thông tin!")
						self.show_Data_For_Account_Info()
						Query2 = " DELETE FROM "+TB_Account+" WHERE user_name = "+user_name
						self.execute_Query(Query2)
						messagebox.showinfo("","Đã xóa Account !")
						self.show_Data_For_Account()
				else:
					messagebox.showinfo("","Không thể xóa tài khoản này!")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để thực hiện chức năng")

	def add_For_Account(self):
		TB_Account = self.TB_Account
		user_name = self.txtUser_Name.get().strip()
		pass_word = self.txtPass_Word.get().strip()
		permission = self.txtPermission.get().strip()
		if(user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name) == False):
				if(pass_word):
					if(permission):
						if(permission == "0" or permission == "1"):
							msg = messagebox.askquestion("","Bạn có chắc muốn thêm tài khoản này ?")
							if(msg == 'yes'):
								ArrayValue = [user_name,pass_word,permission]
								self.insert(TB_Account,ArrayValue)
								messagebox.showinfo("","Cập nhật thông tin thành công!")
								self.show_Data_For_Account()
						else:
							messagebox.showinfo("","Quyền tài khoản vui lòng chọn 0 hoặc 1")
					else:
						messagebox.showinfo("","Quyền tài khoản không được để trống")
				else:
					messagebox.showinfo("","Vui lòng điền mật khẩu !")
			else:
				messagebox.showinfo("","User Name này đã tồn tại\nVui lòng chọn User Name khác!")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để thực hiện sửa thông tin")


	def insert(self,TableName, ArrayValue):
		stri = self.arrToString(ArrayValue)
		Query = "INSERT INTO "+TableName+" VALUES ( "+stri+" )"
		self.execute_Query(Query)
		return True

	def arrToString(self,array):
		stri = ""
		for x in array:
			stri += '"'+x+'"'
			stri = stri.replace("\"\"","\",\"")
		return stri


	def show_Data_For_Sign(self):
		children = self.Treeview_For_Sign.get_children()
		for x in children:
			self.Treeview_For_Sign.delete(x)
		Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+" c WHERE a.user_name = b.user_name and b.user_name = c.user_name  "
		data = self.execute_Query(Query)
		for x in reversed(data):
			self.Treeview_For_Sign.insert('','end',values=x)

	def finding_All_For_Sign(self):
		user_name = self.txtUser_Name_For_Find_Sign.get().strip()
		sign = self.txtSign_For_Find_Sign.get().strip()
		Day = self.txtDay_For_Find_Sign.get().strip()
		Month = self.txtMonth_For_Find_Sign.get().strip()
		Year = self.txtYear_For_Find_Sign.get().strip()
		DMY = Day+'/'+Month+'/'+Year
		if(user_name and sign and Day and Month and Year):
			if(self.check_Exists_User_Name(self.TB_Account_Info,user_name)):
				if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
					sign = sign.upper()
					if(sign == 'IN' or sign == 'OUT'):
						self.clear_Tree_Time_IO()
						Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and c.time LIKE "%'+DMY+'%" and c.sign LIKE "%'+sign+'%" and a.user_name LIKE "%'+user_name+'%"'
						data = self.execute_Query(Query)
						for x in data:
							self.Treeview_For_Sign.insert('','end',values=x)
					else:
						messagebox.showinfo("","Sign vui lòng nhập IN hoặc OUT")
				else:
					messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		elif(user_name and sign):
			if(self.check_Exists_User_Name(self.TB_Account_Info,user_name)):
				sign = sign.upper()
				if(sign == 'IN' or sign == 'OUT'):
					self.clear_Tree_Time_IO()
					Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and c.sign LIKE "%'+sign+'%" and a.user_name LIKE "%'+user_name+'%"'
					data = self.execute_Query(Query)
					for x in data:
						self.Treeview_For_Sign.insert('','end',values=x)
				else:
					messagebox.showinfo("","Sign vui lòng nhập IN hoặc OUT")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		elif(user_name and Day and Month and Year):
			if(self.check_Exists_User_Name(self.TB_Account_Info,user_name)):
				if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
					self.clear_Tree_Time_IO()
					Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and time LIKE "%'+DMY+'%" and user_name LIKE "%'+user_name+'%"'
					data = self.execute_Query(Query)
					for x in data:
						self.Treeview_For_Sign.insert('','end',values=x)
				else:
					messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		elif(sign and Day and Month and Year):
			if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
				sign = sign.upper()
				if(sign == 'IN' or sign == 'OUT'):	
					self.clear_Tree_Time_IO()
					Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and time LIKE "%'+DMY+'%" and sign LIKE "%'+sign+'%"'
					data = self.execute_Query(Query)
					for x in data:
						self.Treeview_For_Sign.insert('','end',values=x)
				else:
					messagebox.showinfo("","Sign vui lòng nhập IN hoặc OUT")
			else:
				messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
		elif(Day or Month or Year):
			self.finding_DMY_For_Time_IO()
		elif(sign):
			self.find_Sign_For_Sign()
		elif(user_name):
			self.find_User_Name_For_Sign()
		else:
			messagebox.showinfo("","Vui lòng điền thông tin để tìm kiếm")	

	def find_User_Name_For_Sign(self):
		user_name = self.txtUser_Name_For_Find_Sign.get().strip()
		if (user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name)):
				self.clear_Tree_Time_IO()
				data = self.finding_User_Name(self.TB_Account,user_name)
				for x in data:
					self.Treeview_For_Sign.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để tìm kiếm")

	def find_Sign_For_Sign(self):
		sign = self.txtSign_For_Find_Sign.get().strip()
		if (sign):
			sign = sign.upper()
			if(sign == 'IN' or sign == 'OUT'):
				self.clear_Tree_Time_IO()
				data = self.finding_Sign(sign)
				for x in data:
					self.Treeview_For_Sign.insert('','end',values=x)
			else:
				messagebox.showinfo("","Sign vui lòng nhập IN hoặc OUT")
		else:
			messagebox.showinfo("","Vui lòng nhập Sign để tìm kiếm")

	def finding_DMY_For_Time_IO(self):
		Day = self.txtDay_For_Find_Sign.get().strip()
		Month = self.txtMonth_For_Find_Sign.get().strip()
		Year = self.txtYear_For_Find_Sign.get().strip()
		if (Day and Month and Year):
			if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
				self.clear_Tree_Time_IO()
				data = self.finding_DMY(Day,Month,Year)
				for x in data:
					self.Treeview_For_Sign.insert('','end',values=x)
			else:
				messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
		else:
			messagebox.showinfo("","Vui lòng nhập đầy đủ Ngày Tháng Năm tìm kiếm")

	def clear_Tree_Time_IO(self):
		children = self.Treeview_For_Sign.get_children()
		for x in children:
			self.Treeview_For_Sign.delete(x)

	def finding_DMY(self,day,month,year):
		DMY = day+'/'+month+'/'+year
		Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and c.time LIKE "%'+DMY+'%"'
		return self.execute_Query(Query)

	def finding_Sign(self,sign):
		Query = " SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM "+self.TB_Account+" a, "+self.TB_Account_Info +" b, "+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and c.sign LIKE "%'+sign+'%"'
		return self.execute_Query(Query)

	def finding_User_Name(self,tableName,user_name):
		tableName = self.changeTextForFilIntoQuery(tableName)
		Query = ' SELECT a.user_name,b.name,a.permission,c.sign,c.time FROM '+self.TB_Account+' a, '+self.TB_Account_Info +' b, '+self.TB_Sign+' c WHERE a.user_name = b.user_name and b.user_name = c.user_name and a.user_name LIKE "%'+user_name+'%"'
		return self.execute_Query(Query)


		#show du lieu cua bang Account info
	def show_Data_For_Account_Info(self):
		children = self.Treeview_For_Account_Info.get_children()
		for x in children:
			self.Treeview_For_Account_Info.delete(x)
		for x in self.take_data(self.TB_Account_Info):
			self.Treeview_For_Account_Info.insert('','end',values=x)

	def finding_For_Account_Info(self):
		user_name = self.txtUser_Name_Of_Account_info.get().strip()
		if (user_name):
			if(self.check_Exists_User_Name(self.TB_Account_Info,user_name)):
				children = self.Treeview_For_Account_Info.get_children()
				for x in children:
					self.Treeview_For_Account_Info.delete(x)
				data = self.finding(self.TB_Account_Info,user_name)
				for x in data:
					self.Treeview_For_Account_Info.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để tìm kiếm")

	def edit_For_Account_Info(self):
		TB_Account_Info = self.TB_Account_Info
		TB_Account_Info = self.changeTextForFilIntoQuery(TB_Account_Info)
		user_name = self.txtUser_Name_Of_Account_info.get().strip()
		name = self.txtName_Of_Account_info.get().strip()
		sex = self.txtSex_Of_Account_info.get().strip()
		birthday = self.txtBirthday_Of_Account_info.get().strip()

		if(user_name):
			if(self.check_Exists_User_Name(self.TB_Account_Info,user_name)):
				if(name):
					if(sex):
						if(birthday):
							birthday = birthday.replace(" ","")
							if(self.check_Birthday(birthday)):
								msg = messagebox.askquestion("","Bạn có chắc muốn thay đổi thông tin ?")
								if(msg == 'yes'):
									user_name = self.changeTextForFilIntoQuery(user_name)
									name = self.changeTextForFilIntoQuery(name)
									sex = self.changeTextForFilIntoQuery(sex)
									birthday = self.changeTextForFilIntoQuery(birthday)
									Query = " UPDATE "+TB_Account_Info+" SET user_name = "+user_name+", name = "+name+", sex = "+sex+", birthday = "+birthday+" WHERE user_name = "+user_name
									self.execute_Query(Query)
									messagebox.showinfo("","Cập nhật thông tin thành công!")
									self.show_Data_For_Account_Info()
						else:
							messagebox.showinfo("","Vui lòng điền Ngày sinh !")
					else:
						messagebox.showinfo("","Vui lòng điền giới tính !")
				else:
					messagebox.showinfo("","Vui lòng điền NAME !")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại USER NAME")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để thực hiện sửa thông tin")


	def check_Birthday(self,birthday):
		if(len(birthday) == 10):
			if(birthday[2] == '/' and birthday[5] == '/'):
				birthdayarr = birthday.split("/")
				if (len(birthdayarr[0]) == 2 and birthdayarr[0].isnumeric() ):
					if(len(birthdayarr[1]) == 2 and birthdayarr[1].isnumeric()):
						if(len(birthdayarr[2]) == 4 and birthdayarr[2].isnumeric()):
							return True
						else:
							messagebox.showinfo("","Năm sinh không hợp lệ !")
					else:
						messagebox.showinfo("","Tháng sinh không hợp lệ !")
				else:
					messagebox.showinfo("","Ngày sinh không hợp lệ !")
			else:
				messagebox.showinfo("",'Vui lòng ngăn cách giữa ngày tháng năm bằng "/" !')
		else:
			messagebox.showinfo("","Độ dài Ngày sinh không hợp lệ !")
		return False



	def delete_For_Account_Info(self):
		TB_Account_Info = self.TB_Account_Info
		TB_Account_Info = self.changeTextForFilIntoQuery(TB_Account_Info)
		TB_Account = self.TB_Account
		TB_Account = self.changeTextForFilIntoQuery(TB_Account)

		user_name = self.txtUser_Name_Of_Account_info.get().strip()
		if(user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name)):
				user_name = self.changeTextForFilIntoQuery(user_name)
				msg = messagebox.askquestion("","Bạn có chắc muôn xóa tất cả thông tin của User này?")
				if(msg == 'yes'):
					Query1 = " DELETE FROM "+TB_Account_Info+" WHERE user_name = "+user_name
					self.execute_Query(Query1)
					messagebox.showinfo("","Xóa thông tin User thành công!")
					self.show_Data_For_Account_Info()
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để thực hiện chức năng")

	def add_For_Account_Info(self):
		TB_Account_Info = self.TB_Account_Info
		user_name = self.txtUser_Name_Of_Account_info.get().strip()
		name = self.txtName_Of_Account_info.get().strip()
		sex = self.txtSex_Of_Account_info.get().strip()
		birthday = self.txtBirthday_Of_Account_info.get().strip()
		if(user_name):
			if(self.check_Exists_User_Name(self.TB_Account,user_name)):
				if(self.check_Exists_User_Name(self.TB_Account_Info,user_name) != True):
					if(name):
						if(sex):
							if(birthday):
								birthday = birthday.replace(" ","")
								if(self.check_Birthday(birthday)):
									msg = messagebox.askquestion("","Bạn có chắc muốn thêm thông tin cho tài khoản này ?")
									if(msg == 'yes'):
										ArrayValue = [user_name,name,sex,birthday]
										self.insert(TB_Account_Info,ArrayValue)
										messagebox.showinfo("","Thêm thông tin thành công !")
										self.show_Data_For_Account_Info()
							else:
								messagebox.showinfo("","Vui lòng điền ngày tháng năm sinh !")
						else:
							messagebox.showinfo("","Vui lòng điển giới tính !")
					else:
						messagebox.showinfo("","Vui lòng điền Name !")
				else:
					messagebox.showinfo("","User này đã được điền thông tin đầy đủ !")
			else:
				messagebox.showinfo("","Không tìm thấy User này!")
		else:
			messagebox.showinfo("","Vui lòng nhập USER NAME để thực hiện sửa thông tin")



if __name__ == '__main__':
	Admin("admin")