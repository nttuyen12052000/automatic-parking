import cv2
import os
from random import choice
from random import randint
from imutils import paths
import sqlite3
data = "../model_FD/user/dataset/"
a = len(list(os.walk(data)))
print(a)
c = list(os.walk(data))
d= 0
mssv = 1811060111
# list = os.listdir(data)
# print(list)
# for f in list:
#     print(f)
#     mssv+=1
#     os.rename("images/"+f,"images/"+str(mssv))
imagePaths = list(paths.list_images(data))
# for (path, i,list) in c:
#     z = 0
#     print(i)
#     # print(imagePath)
#     print(path)
#     list.sort()
#     for f in list:
#         z+=1
#         if z < 3:
#             print(path+"/"+f)
            # try:
            #     os.remove(path+"/"+f)
            # except:
            #     print("Delete failed")
    # mssv+=1



# for (path, i,list) in c:
#     ho = choice(["Nguyen ","Tran ","Le ","Pham ","Huynh ","Phan ","Vo ","Do "])
#     tenlot = choice(["Thi ","Tuan ","Cong ","Anh ","Trung ","Hoang ","Minh ","Thanh "])
#     ten  = choice(["Thang","Duy", "Ngan", "Linh","Minh","Anh","Huy","Phong","Vu","Mai","Nhi","Thao","Uyen"])
#     phoneNumber = choice(["0904382301","0934556498","0934418109","0931111217","0934553769","0931776251","0934542766	","0934418357","0931786238","0931102396","0936302896","0931790396","0931778596","0935176938","0936160078","0901152396","0907625196","0935082069","0935070538","0906153896","0907532196","0903102596","0932055196","0907215196","0932017238","0931107869","0936303796","0933105296","0901162738","0931175696","0935083178","0904358730"])
#     email = choice(["khongcodon12@gmail.com","chieckhangioam22@gmail.com","abcd123422@gmail.com","thichthilam12@gmail.com","khongthichthilam2@gmail.com","boycodon3@gmail.com","girlcodon@gmail.com","idoit@gmail.com","ican@gmail.com","ngua22@gmail.com","leuleu342@gmail.com","kkkk341@gmail.com","vykhung@gmail.com","thanhkhung32@gmail.com","thanhbingu412@gmail.com","thanhoccho11@gmail.com","thanhcodon@gmail.com",])
#     diachi = choice(["42, kp3, Q. Tan Binh, TP.HCM","32,kp3, Q. 3, TP.HCM","424, kp3, Q. 4, TP.HCM","426, kp5, Q. 5, TP.HCM","412, kp6, Q. 6, TP.HCM","42, kp3, Q. 7, TP.HCM","42, kp9, Q. 8, TP.HCM","42, kp8, Q. 9, TP.HCM","42, kp2, Q. 2, TP.HCM","42, kp3, Q. 10, TP.HCM","42, kp3, Q. 1, TP.HCM","424, kp4, Q.12, TP.HCM","142, kp6, Q. Binh Tan, TP.HCM","412, kp3, Q. Phu Nhuan, TP.HCM","42, kp5, Q. Binh Thanh, TP.HCM","122, kp4, Q. Tan Phu, TP.HCM"])
#     print(path)
#     studentID = path[25:]
#     if studentID != "" and studentID != "unknown":
#         name = ho + tenlot + ten
#         print(studentID)
#         if studentID != '1811063212':
#             # print(name)
#             # print(id)
#             # print(sdt)
#             # print(email)
#             # print(diachi)
#             conn = sqlite3.connect("mydb.db")
#             ins = "INSERT INTO info_User(studentID,name,phoneNumber,email,address) VALUES("+studentID+",'"+name+"','"+phoneNumber+"','"+email+"','"+diachi+"')"
#             print(ins)
#             print("Insert successfully")
#             conn.execute(ins)
#             conn.commit()
#             # print(conn.rowcount,"record inserted")
#             conn.close()

# while True:
#     bs1  = randint(11,99)
#     bs2 = choice(["A","B","C","D","E","F","G","H","Q","W","T","Y","U","I","O","P","L","K","J","Z","X","V","N","M"])
#     bs3 = randint(1,9)
#     bs4 = randint(1000,99999)
#     bs = str(bs1) + bs2 +str(bs3)+"-"+str(bs4)
#     print(bs)

# conn = sqlite3.connect("mydb.db")
# for (path, i,list) in c:
#     bs1  = randint(11,99)
#     bs2 = choice(["A","B","C","D","E","F","G","H","Q","W","T","Y","U","I","O","P","L","K","J","Z","X","V","N","M"])
#     bs3 = randint(1,9)
#     bs4 = randint(1000,99999)
#     LicensePlate = str(bs1) + bs2 +str(bs3)+"-"+str(bs4)
#     print(path)
#     studentID = path[25:]
#     if studentID != "" and studentID != "unknown":
#         print(studentID)
#         if studentID != '1811063212':
#             ins = "INSERT INTO lp_Registered(studentID,LicensePlate) VALUES("+studentID+",'"+LicensePlate+"')"
#             print("Insert successfully")
#             conn.execute(ins)
# conn.commit()
# conn.close()

# print(d)
# for (path, i,list) in c:
#     # print(i)
#     # print(path)
#     # list.sort()
#     for f in list:
#         link = path + "/" + f
#         image = cv2.imread(link)
#         # print(image.shape[0])
#         if image.shape[0] == 182:
#             resized = cv2.resize(image, (128,128), interpolation = cv2.INTER_AREA)
#             cv2.imwrite(link,resized)
# x = 0
# for (path, i,list) in c:
#     for f in list:
#         x+=1
# print(x)