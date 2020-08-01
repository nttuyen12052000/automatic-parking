import sqlite3 as db 
from tkinter import *
from tkinter import messagebox  
import os

def clear():
    os.system('cls')



master = Tk()

DBName = "mydb.db"
TableName = "lp_Registered"


Label(master,text="Tìm thông tin chủ xe").grid()
Label(master,text="License Plate: ").grid(row=1,column=0)
txtlicenseplate = Entry(master,width=20)
txtlicenseplate.grid(row=1,column=1)
Label(master,text="").grid()


def execute_Query(Query):
	conn = db.connect(DBName)
	cur = conn.cursor()
	cur.execute(Query)
	conn.commit()
	data = cur.fetchall()
	cur.close()
	conn.close()
	return data


# Take a list ABC from a table.
def take_List(Field,TableName):
	Query = "SELECT "+Field+" from "+TableName
	return execute_Query(Query)

def changeTextForFilIntoQuery(ValueCondition):
	return "\""+ValueCondition+"\""


def find_Owner_Of_License_Plate(license_plate):
	license_plate = changeTextForFilIntoQuery(license_plate)
	Query = "SELECT b.* FROM lp_Registered a,info_User b where a.studentID = b.studentID AND a.LicensePlate = "+license_plate
	return execute_Query(Query)

def search(value,List):
	for x in List:
		if(x[0] == value):
			return True
	return False

def printList(List):
	for x in List:
		print(x)

def show_Info_Of_Owner():
	license_plate = txtlicenseplate.get()
	List = take_List("LicensePlate",TableName)
	if(search(license_plate,List)):
		owner = find_Owner_Of_License_Plate(license_plate)
		printList(owner)
	else:
		messagebox.showinfo("","Không tìm thấy thông tin của biển số này")





btnsubmit = Button(master,text="Tìm",command=show_Info_Of_Owner,width=20)
btnsubmit.grid(column=1)




mainloop()
