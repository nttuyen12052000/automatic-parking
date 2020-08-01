import cv2
import sqlite3
from datetime import datetime

def insert_infoUser():
    conn = sqlite3.connect("mydb.db")
    # conn.execute('DROP TABLE myTable')
    # conn.execute('CREATE TABLE info_User(studentID varchar(10), name NVARCHAR(50), phoneNumber varchar(10), email VARCHAR(50), address NVARCHAR(50))')
    studentID=input('Nhap mssv:')
    name=input('Nhap ho ten:')
    phoneNumber=input('Nhap sdt:')
    email=input('Nhap email:')
    address=input('Nhap dia chi:')
    ins = "INSERT INTO info_User(studentID,name,phoneNumber,email,address) VALUES("+studentID+",'"+name+"','"+phoneNumber+"','"+email+"','"+address+"')"
    print("Insert successfully")
    conn.execute(ins)
    conn.commit()
    # print(conn.rowcount,"record inserted")
    conn.close()


def insert_lpRegistered():
    conn = sqlite3.connect("mydb.db")
    # conn.execute('CREATE TABLE lp_Registered(id INTEGER PRIMARY KEY, studentID varchar(10), LincensePlate varchar(11))')
    studentID=input('Nhap mssv:')
    LincensePlate=input('Nhap bien so dang ki:')
    ins = "INSERT INTO lp_Registered(studentID,LincensePlate) VALUES("+studentID+",'"+LincensePlate+"')"
    print("Insert successfully")
    conn.execute(ins)
    conn.commit()
    conn.close()
def create_time_IO():
    conn = sqlite3.connect("mydb.db")
    # studentID = '1811063212'
    # lincensePlate = '63B9-99999'
    # now = datetime.now()
    # print("now",now)
    # fm_time = now.strftime("%H:%M:%S %d/%m/%Y")
    # print(fm_time)
    # status = 'IN'
    # newUser = 0
    conn.execute('CREATE TABLE time_IO(id INTEGER PRIMARY KEY, studentID varchar(10), lincensePlate varchar(11),time varchar(20),status varchar(3), newUser integer)')
    # ins = "INSERT INTO time_IO(studentID,LincensePlate,time,status,newUser) VALUES('"+studentID+"','"+lincensePlate+"','"+fm_time+"','"+status+"',1)"
    # print(ins)
    # conn.execute(ins)
    conn.commit()
    conn.close()

# create_time_IO()
insert_lpRegistered()
# insert_infoUser()

conn = sqlite3.connect("mydb.db")
cur = conn.cursor()
# conn.execute('DROP TABLE time_IO')
# conn.execute("Delete from time_IO")
# conn.execute("Delete from lp_Registered")
# query = "Delete from info_User"
# lp = "63B9-99999"
# lp = lp.replace(lp,"'"+lp+"'")
# query = "SELECT studentID FROM lp_Registered where LincensePlate="+lp

# print(query)
# cur.execute(query)
# studentID = cur.fetchall()
# print(studentID)
# for x in studentID:
#     print(x[0])
conn.commit()
conn.close()