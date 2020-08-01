from tkinter import *
from tkinter import messagebox
import sqlite3 as db
from tkinter import ttk
from AdminForm import Admin
import threading 
from threading import Thread,Event
import time
# from model_FD.new_user.train import train_new
from model_FD.user.train import train
from datetime import datetime
from PIL import Image
import numpy
import cv2
import imutils
import numpy as np
import pickle
import argparse
import face_recognition
import os
import glob		
import smtplib




def mail_send(email):
    sender_email = "nckh1205@gmail.com"
    receive_email = email
    password = "Abcdabcd123"
    message = "Your car is moving out of the parking lot, do you agree?"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    print("Login success")
    server.sendmail(sender_email, receive_email, message)
    print("Email has been sent to , receive_email")

def sort_contours(cnts):
    #sap xep lon toi nho
    reverse = False
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),key=lambda b: b[1][i], reverse=reverse))
    return cnts

def detect_lp(img):
    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY)
    plate_info = ""
    roi = img
    # Ap dung threshold de phan tach so va nen
    binary = cv2.threshold(gray, 127, 255,cv2.THRESH_BINARY_INV)[1]

    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)
    cont, _  = cv2.findContours(thre_mor, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	
    for c in sort_contours(cont):
        (x, y, w, h) = cv2.boundingRect(c)
        ratio = h/w
        if 1.5<=ratio<=3.5:
            if h/roi.shape[0]>=0.6:
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Tach so va predict
                get_num = thre_mor[y:y+h,x:x+w]
                get_num = cv2.resize(get_num, dsize=(digit_w, digit_h))
                _, get_num = cv2.threshold(get_num, 20, 255, cv2.THRESH_BINARY)
                get_num = np.array(get_num,dtype=np.float32)
                get_num = get_num.reshape(-1, digit_w * digit_h)

                # Dua vao model SVM
                result = model_svm.predict(get_num)[1]
                result = int(result[0, 0])

                if result<=9: # Neu la so thi hien thi luon
                    result = str(result)
                else: #Neu la chu thi chuyen bang ASCII
                    result = chr(result)

                plate_info +=result
    return plate_info


#Check coi trong frame co bang so hay khong (Chua lay ra so)
def check_lp(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    cnts,h = cv2.findContours(thresh,1,2)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    largest_rectangle = [0,0]
    flag = None
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        ratio = h/w
        if 0.6<=ratio<=1.1:
            img = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),1)
            approx = cv2.approxPolyDP(c,0.01*cv2.arcLength(c,True),True)
            if len(approx) == 4:
                area = cv2.contourArea(c)
                if area > largest_rectangle[0]:
                    largest_rectangle = [cv2.contourArea(c), c, approx]
                    flag=1
                    # print("Da phat hien bang so")
    return flag, largest_rectangle

def overlay(l_img,s_img,x,y):
    s_img = cv2.resize(s_img,(100,100),interpolation = cv2.INTER_AREA)
    l_img[y:y+s_img.shape[0],x:x+s_img.shape[1]] = s_img

#Tim ra chuoi co xuat hien nhieu nhat (chong nhieu)
def find_max_str(list):
    max_str = list[0]
    max = list.count(list[0])
    for values in list:
        if max <= list.count(values):
            max_str = values
    # print(max_str)
    return max_str

def checkin_main():
    #Load model detect face
    print("Loading model face-detect...")
    cas = "model_FD/user/haarcascade_frontalface_default.xml"
    enc = "model_FD/user/encodings.pickle"
    data = pickle.loads(open(enc, "rb").read())
    detector = cv2.CascadeClassifier(cas)

    # load model SVM detect char
    print("Loading model charect-detect...")
    digit_w = 30
    digit_h = 60
    model_svm = cv2.ml.SVM_load('model_CD/svm.xml')

    #cam
    print("Openning video stream...")
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)

    #connect database
    conn = db.connect("DB/mydb.db")

    #khoi tao bien, co
    skip_frame = 0
    str_lp = ""
    name = ""
    have_lp = 0
    have_name = 0
    check_in = "Moi ban vao!!"
    add_user = "Vui long nhin thang vao camera"
    new_user = 1
    thongbao = 0
    start_time = 0 
    xacsuat = 0
    list = []
    values = ""
    studentId_of_LP = ""
    lp_Registered = 0
    isStudent =0
    finish_detect = 0
    use_face_detect = 0
    training = 1
    sampleNum=0
    trained = 0
    reset = 0
    list_owner = []
    # ------------------------------------------------------
    #bat dau
    while(cap.isOpened()):
        ret,frame = cap.read()
        img_save = frame
        cv2.namedWindow('checkin')
        cv2.setWindowProperty('checkin',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.moveWindow('checkin',0,100)
        # detect lincense plate
        
        if len(str_lp)<9:  
            flag,largest_rectangle = check_lp(frame)
            if flag:
                # time.sleep(2)
                x,y,w,h = cv2.boundingRect(largest_rectangle[1])
                cropped=frame[y:y+h,x:x+w]
                cropped= cv2.resize(cropped,(230,170))
                #Cat ra bien so nhung ma day la bien so xe may (Co 2 dong)
                x = cropped.shape[1]
                y = cropped.shape[0]

                #Cat nua tren bang so
                crp1 = cropped[0:int(y/2),0:int(x)]
                #Cat nua duoi bang so
                crp2 = cropped[int(y/2):int(y),0:int(x)]

                #Detect chu so nua phan tren
                above = detect_lp(crp1)
                #Detect chu so nua phan duoi
                below = detect_lp(crp2)

                #bien so thoa man so ki tu
                if len(above) == 4 and len(below) >=4 and len(below) <=5 and below.isnumeric() == True and above[0:2].isnumeric() == True and above[2].isnumeric() == False: 
                    str_lp = above+ '-' + below
                    print("Bien so: ", str_lp)

                    #kiem tra bien so co dang ki hay chua
                    cvt_str_lp = str_lp.replace(str_lp,"'"+str_lp+"'")
                    cur = conn.cursor()
                    query = "SELECT studentID FROM lp_Registered where LicensePlate="+cvt_str_lp
                    cur.execute(query)
                    studentID = cur.fetchall()
                    print(studentID)
                    if studentID:
                        if len(studentID[0][0])==10:
                            studentId_of_LP = studentID[0][0]
                            list_owner = studentID
                            lp_Registered = 1
                            for owner in list_owner:
                                print("Bien so thuoc sv: ",owner)
                    else:
                        print("Bien so chua dang ki")
                        use_face_detect = 1
                    #reset variable
                    list.clear()
                    values = ""
                    xacsuat = 0
                    have_lp = 1 #Co bang so

        #Neu bien so chua dang ki thi khong can kiem tra khuon mat            
        if use_face_detect == 1:
            finish_detect = 1      


        if have_lp == 1 and lp_Registered == 1 and have_name == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.putText(frame,"Vui long bo khau trang ra!!",(10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),3, lineType=cv2.LINE_AA)
            #Lay ra cac phan cho la khuon mat
            rects = detector.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)

            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            if(boxes):
                if (boxes[0][2] - boxes[0][0])/frame.shape[0] > 0.4:
                    encodings = face_recognition.face_encodings(rgb, boxes)
                    names = []

                    #Su dung model da train coi day la ai
                    for encoding in encodings:
                        matches = face_recognition.compare_faces(data["encodings"],encoding)

                        if True in matches:
                            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                            counts = {}

                            for i in matchedIdxs:
                                name = data["names"][i]
                                counts[name] = counts.get(name, 0) + 1

                            name = max(counts, key=counts.get)
                
                        names.append(name)

                    for ((top, right, bottom, left), name) in zip(boxes, names):
                        cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
                        value = name
                        list.append(value)
                        # print(list)
                        #Tai la mssv nen se la 10 ki tu
                        if len(list)==10:
                            name = find_max_str(list)
                            xacsuat = list.count(name)/len(list)
                            have_name = 1 
        
                            #Kiem tra lai neu ai do lay xe nguoi da dang ki di 
                            if lp_Registered == 1:
                                #Kiem tra chu so huu co di xe dang ki hay khong
                                for owner in list_owner:
                                    if name == owner[0]:
                                        #Neu co thi khong detect new user
                                        new_user = 0

                                        #Luu hinh anh lai
                                        cur = conn.cursor()
                                        query = "SELECT count(*) FROM time_IO"
                                        cur.execute(query)
                                        id = cur.fetchall()[0][0]+1
                                        print(owner)
                                        cv2.imwrite("Storage/Check-in/"+str(id) + ".jpg", img_save[top:bottom,left:right])
                    
                            finish_detect = 1

                            #reset variable
                            list.clear()
                            values = ""
                            xacsuat = 0

        #Bat dau dem thoi gian.
        if finish_detect ==1 and thongbao == 0:
            start_time = time.time()
            thongbao =1
            # print("Cho 5s")
        if finish_detect == 1:
            if new_user == 0:
                cv2.putText(frame,check_in,(10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),3, lineType=cv2.LINE_AA)
                if time.time()-start_time > 5:
                    # print("Moi ban di qua")

                    #Lay thoi gian hien tai
                    now = datetime.now()

                    #convert thoi gian
                    fm_time = now.strftime("%H:%M:%S %d/%m/%Y")
                    status = 'IN'
                    ins = "INSERT INTO time_IO(studentID,LicensePlate,time,status,newUser) VALUES('"+name+"','"+str_lp+"','"+fm_time+"','"+status+"',0)"
                    print("Insert succesfully!!")
                    print(ins)

                    #Ghi vao database
                    conn.execute(ins)
                    conn.commit()

                    #doi 5s cho user di qua va reset variable
                    new_user = 1
                    have_name = 0
                    str_lp = ""
                    name = ""
                    have_lp = 0
                    thongbao = 0
                    studentId_of_LP = ""
                    lp_Registered = 0
                    finish_detect = 0
                    use_face_detect = 0
                    print("----------------------NEXT-----------------------")
            
            #Them moi nguoi dung
            else:
                if sampleNum <5:
                    img = frame
                    add_user = "Vui long nhin thang vao camera"
                    cv2.putText(frame,add_user,(10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),2, lineType=cv2.LINE_AA)
                    cur = conn.cursor()
                    query = "SELECT count(*) FROM time_IO"
                    cur.execute(query)
                    studentID = cur.fetchall()
                    id = studentID[0][0]+1
                    name = "User"+str(studentID[0][0]+1)
                    folder="model_FD/new_user/dataset/"+name
                    faces = detector.detectMultiScale(img, 1.3, 5)
                    if os.path.exists(folder)==False:
                        os.mkdir(folder)
                    if skip_frame%20==0:
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            sampleNum = sampleNum + 1
                            cv2.imwrite(folder+ "/"+name + '.' + str(sampleNum) + ".jpg", img_save[y:y + h, x:x + w])
                            if sampleNum == 4:
                                cv2.imwrite("Storage/Check-in/"+str(id) + ".jpg", img_save[y:y + h, x:x + w])
                else:
                    cv2.putText(frame,add_user,(10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),2, lineType=cv2.LINE_AA)
                    if training == 1:
                        add_user = "Moi ban di qua!"
                        # train_new()
                        trained = 1
                        training = 0
                        # print("Trained")
                    # print(name)
                    if trained == 1:
                        start_time = time.time()
                        trained = 0
                        reset = 1
                    # print("Vui long doi ty")
                    #doi 5s cho user di qua va reset tat ca variable
                    if reset == 1 and time.time()-start_time > 5:
                        now = datetime.now()
                        fm_time = now.strftime("%H:%M:%S %d/%m/%Y")
                        status = 'IN'
                        ins = "INSERT INTO time_IO(studentID,LicensePlate,time,status,newUser) VALUES('"+name+"','"+str_lp+"','"+fm_time+"','"+status+"',1)"
                        print(ins)
                        print("Insert succesfully!!")

                        #Ghi vao database
                        conn.execute(ins)
                        conn.commit()
                        # print("reset")
                        new_user = 1
                        have_name = 0
                        str_lp = ""
                        name = ""
                        have_lp = 0
                        thongbao = 0
                        studentId_of_LP =""
                        lp_Registered = 0
                        finish_detect = 0
                        use_face_detect= 0
                        sampleNum = 0
                        training = 1
                        add_user = ""
                        reset = 0
                        skip_frame = 0
                        print("----------------------NEXT-----------------------")
        
        cv2.imshow('checkin',frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    conn.close()
    cap.release()
    cv2.destroyAllWindows()


def checkout_main():
    #Load model detect face
    print("Loading model face-detect...")
    cas = "model_FD/user/haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cas)

    # Model danh cho nguoi da dang ki
    enc = "model_FD/user/encodings.pickle"
    data = pickle.loads(open(enc, "rb").read())
    

    # load model SVM detect char
    

    #cam
    print("Openning video stream...")
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)

    #connect database
    conn = db.connect("DB/mydb.db")

    #khoi tao bien, co
    skip_frame = 0
    str_lp = ""
    name = ""
    have_lp = 0
    have_name = 0
    check_out = "Moi ban ra!!"
    add_user = "Vui long nhin thang vao camera"
    new_user = 1
    thongbao = 0
    start_time = 0 
    xacsuat = 0
    list = []
    values = ""
    studentId_of_LP = ""
    lp_Registered = 0
    isStudent =0
    finish_detect = 0
    use_face_detect = 0
    training = 1
    sampleNum=0
    trained = 0
    reset = 0
    studentID = ""
    model = 1
    next = 1
    id_check_in = 0
    img_check_in = None
    wait_start = 0
    adminAccept = 0
    list_owner = []
    not_owner= "Khong phai chu xe!"
    not_owner_next= "Bam dau cach de cho qua!"
    img_check_out = None
    succes = "Hop le. Moi Ban di qua!!"
    fail = "Khong hop le. Vui long kiem tra lai!!"
    # ------------------------------------------------------
    #bat dau
    while(cap.isOpened()):
        ret,frame = cap.read()
        img_save = frame
        cv2.namedWindow('checkout')
        cv2.moveWindow('checkout',400,100)
        # detect lincense plate
        if len(str_lp)<9:  
            flag,largest_rectangle = check_lp(frame)
            if flag:
                # time.sleep(2)
                x,y,w,h = cv2.boundingRect(largest_rectangle[1])
                cropped=frame[y:y+h,x:x+w]
                cropped= cv2.resize(cropped,(230,170))
                #Cat ra bien so nhung ma day la bien so xe may (Co 2 dong)
                x = cropped.shape[1]
                y = cropped.shape[0]

                #Cat nua tren bang so
                crp1 = cropped[0:int(y/2),0:int(x)]
                #Cat nua duoi bang so
                crp2 = cropped[int(y/2):int(y),0:int(x)]

                #Detect chu so nua phan tren
                above = detect_lp(crp1)
                #Detect chu so nua phan duoi
                below = detect_lp(crp2)

                #bien so thoa man so ki tu
                if len(above) == 4 and len(below) >=4 and len(below) <=5 and below.isnumeric() == True and above[0:2].isnumeric() == True and above[2].isnumeric() == False: 
                    str_lp = above + '-' + below
                    #kiem tra bien so co dang ki hay chua
                    cvt_str_lp = str_lp.replace(str_lp,"'"+str_lp+"'")
                    cur = conn.cursor()
                    query = "SELECT id, studentID, newUser FROM time_IO where LicensePlate="+cvt_str_lp+"ORDER BY id DESC LIMIT 1"
                    cur.execute(query)
                    result = cur.fetchall()
                    if result:
                        print("Bien so: ", str_lp)
                        id_check_in = result[0][0]
                        studentID =  result[0][1]
                        check_new_user = result[0][2]
                        print(studentID)
                        if check_new_user == 0:
                            list_cur = conn.cursor()
                            query = "SELECT studentID FROM lp_Registered where LicensePlate="+cvt_str_lp
                            list_cur.execute(query)
                            list_owner = list_cur.fetchall()
                            print(list_owner)
                            print("User")
                            model = 1
                        else:
                            model = 2
                            print("Khach")
                            # next = 0
                        have_lp = 1 #Co bang so
                    else:
                        str_lp = ""

        #Detect face with model user
        if have_lp == 1 and have_name == 0 and model == 1:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            #Lay ra cac phan cho la khuon mat
            rects = detector.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)

            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            if(boxes):
                if (boxes[0][2] - boxes[0][0])/frame.shape[0] > 0.4:
                    encodings = face_recognition.face_encodings(rgb, boxes)
                    names = []
        
                    #Su dung model da train coi day la ai
                    for encoding in encodings:
                        matches = face_recognition.compare_faces(data["encodings"],encoding)

                        if True in matches:
                            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                            counts = {}
        
                            for i in matchedIdxs:
                                name = data["names"][i]
                                counts[name] = counts.get(name, 0) + 1

                            name = max(counts, key=counts.get)
                
                        names.append(name)

                    for ((top, right, bottom, left), name) in zip(boxes, names):
                        cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
                        value = name
                        list.append(value)
                        # print(list)
                        #Tai la mssv nen se la 10 ki tu
                        if len(list)==10:
                            name = find_max_str(list)
                            xacsuat = list.count(name)/len(list)
                            have_name = 1 

                            print(name)
                            #Kiem tra chu so huu co di xe dang ki hay khong
                            for owner in list_owner:
                                if name == owner[0]:
                                    #Neu co thi khong detect new user
                                    new_user = 0

                                    #Luu hinh anh lai
                                    cur = conn.cursor()
                                    query = "SELECT count(*) FROM time_IO"
                                    cur.execute(query)
                                    id = cur.fetchall()[0][0]+1
                                    cv2.imwrite("Storage/Check-out/"+str(id) + ".jpg", img_save[top:bottom,left:right])
                                    img_check_out = img_save[top:bottom,left:right]
                                    break
                                else: 
                                    email_of_owner = owner[0]
                                    cvt_email_of_owner = email_of_owner.replace(email_of_owner,"'"+email_of_owner+"'")
                                    cur = conn.cursor()
                                    query = "SELECT email FROM info_User where studentID="+cvt_email_of_owner
                                    cur.execute(query)
                                    result = cur.fetchall()
                                    print(result[0][0])
                                    print("Sending email....")
                                    mail_send(result[0][0])
                                    next = 0
                                    new_user = 0
                                    wait_start = 1
                                    img_check_out = img_save[top:bottom,left:right]


                    
                            finish_detect = 1

                            #reset variable
                            list.clear()
                            values = ""
                            xacsuat = 0

        #Detect face with model visitor
        if have_lp == 1 and have_name == 0 and model == 2:

            # Model for visitor
            enc = "model_FD/new_user/encodings.pickle"
            data = pickle.loads(open(enc, "rb").read())

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            #Lay ra cac phan cho la khuon mat
            rects = detector.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)

            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            if(boxes):
                if (boxes[0][2] - boxes[0][0])/frame.shape[0] > 0.4:
                    encodings = face_recognition.face_encodings(rgb, boxes)
                    names = []

                    #Su dung model da train coi day la ai
                    for encoding in encodings:
                        matches = face_recognition.compare_faces(data["encodings"],encoding)

                        if True in matches:
                            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                            counts = {}
        
                            for i in matchedIdxs:
                                name = data["names"][i]
                                counts[name] = counts.get(name, 0) + 1
        
                            name = max(counts, key=counts.get)
                        
                        names.append(name)
        
                    for ((top, right, bottom, left), name) in zip(boxes, names):
                        cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
                        value = name
                        list.append(value)
                        # print(list)
                        #Tai la mssv nen se la 10 ki tu
                        if len(list)==10:
                            name = find_max_str(list)
                            xacsuat = list.count(name)/len(list)
                            have_name = 1 
        
                            print(name)
                            #Kiem tra chu so huu co di xe dang ki hay khong
                            if name == studentID:
                                #Neu co thi khong detect new user
                                new_user = 1
        
                                #Luu hinh anh lai
                                cur = conn.cursor()
                                query = "SELECT count(*) FROM time_IO"
                                cur.execute(query)
                                id = cur.fetchall()[0][0]+1
                                cv2.imwrite("Storage/Check-out/"+str(id) + ".jpg", img_save[top:bottom,left:right])
                                img_check_out = img_save[top:bottom,left:right]
                            else: 
                                print("Thong bao den quan ly")
                                next = 0
                                wait_start = 1
                                img_check_out = img_save[top:bottom,left:right]

                    
                            finish_detect = 1

                            #reset variable
                            list.clear()
                            values = ""
                            xacsuat = 0

        # Bat dau dem thoi gian.
        if finish_detect ==1 and thongbao == 0:
            start_time = time.time()
            thongbao =1
            # print("Cho 5s")
        if finish_detect == 1:
            if next == 1:
                img_check_in = cv2.imread("Storage/Check-in/"+str(id_check_in)+".jpg")
                if img_check_in is not None:    
                    # cv2.imshow('checkin',img_check_in)
                    cv2.putText(frame,"IN",(440, 380), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),2, lineType=cv2.LINE_AA)
                    overlay(frame,img_check_in,440,380)
                    # img_check_in = cv2.resize(img_check_in,(100,100),interpolation = cv2.INTER_AREA)
                    # frame[380:380+img_check_in.shape[0],540:540+img_check_in.shape[1]] = img_check_in
                if img_check_out is not None:
                    # cv2.imshow('checkout',img_check_out)
                    cv2.putText(frame,"OUT",(540, 380), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),2, lineType=cv2.LINE_AA)
                    overlay(frame,img_check_out,540,380)

                cv2.putText(frame,succes,(10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0),3, lineType=cv2.LINE_AA)
                
                if time.time()-start_time > 5:
                    # print("Moi ban di qua")

                    #Lay thoi gian hien tai
                    now = datetime.now()

                    # convert thoi gian
                    fm_time = now.strftime("%H:%M:%S %d/%m/%Y")
                    status = 'OUT'
                    if new_user == 1:
                        ins = "INSERT INTO time_IO(studentID,LicensePlate,time,status,newUser) VALUES('"+name+"','"+str_lp+"','"+fm_time+"','"+status+"',1)"
                    else:
                        ins = "INSERT INTO time_IO(studentID,LicensePlate,time,status,newUser) VALUES('"+name+"','"+str_lp+"','"+fm_time+"','"+status+"',0)"
                    print("Insert succesfully!!")
                    print(ins)
                    conn.execute(ins)
                    conn.commit()
                    
                    if model == 2:
                        # reload model user
                        enc = "model_FD/user/encodings.pickle"
                        data = pickle.loads(open(enc, "rb").read())
                        print("Xoa hinh anh cua visitor")
                        files = glob.glob('model_FD/new_user/dataset/'+studentID+'/*.jpg')
                        for f in files:
                            try:
                                os.remove(f)
                            except:
                                print("Delete failed")
                        try:
                            os.rmdir("model_FD/new_user/dataset/"+studentID)
                        except:
                            print("delete failed")

                    #doi 5s cho user di qua va reset variable
                    new_user = 1
                    have_name = 0
                    str_lp = ""
                    name = ""
                    have_lp = 0
                    thongbao = 0
                    studentId_of_LP = ""
                    lp_Registered = 0
                    finish_detect = 0
                    use_face_detect = 0
                    model = 1
                    list_ownew = []
                    # cv2.destroyWindow('checkout')
                    # cv2.destroyWindow('checkin')
                    print("----------------------NEXT-----------------------")
            if next == 0:
                cv2.putText(frame,fail,(10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255),2, lineType=cv2.LINE_AA)
                # cv2.putText(frame,not_owner_next,(50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255),2, lineType=cv2.LINE_AA)

                #Show image check in, check out
                img_check_in = cv2.imread("Storage/Check-in/"+str(id_check_in)+".jpg")
                if img_check_in is not None:    
                    # cv2.imshow('checkin',img_check_in)
                    cv2.putText(frame,"IN",(440, 380), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),2, lineType=cv2.LINE_AA)
                    overlay(frame,img_check_in,440,380)
                if img_check_out is not None:
                    # cv2.imshow('checkout',img_check_out)
                    cv2.putText(frame,"OUT",(540, 380), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),2, lineType=cv2.LINE_AA)
                    overlay(frame,img_check_out,540,380)
                cv2.putText(frame,"KHONG CHO QUA (N)",(10, 455), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),2, lineType=cv2.LINE_AA)
                cv2.putText(frame,"CHO QUA (Y)",(10, 477), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),2, lineType=cv2.LINE_AA)

                if adminAccept ==0:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('n'):
                        print("Khong cho qua")
                        #Khong cho qua
                        adminAccept = 2
                    if key == ord('y'):
                        print("Cho qua")
                        adminAccept = 1
                if adminAccept == 1:
                    if wait_start == 1:
                        wait_5s = time.time()
                        wait_start = 0
                        not_owner = "Moi ban di qua"
                        not_owner_next = ""
                    
                    if time.time()- wait_5s >5:
                        #Luu hinh anh lai
                        cur = conn.cursor()
                        query = "SELECT count(*) FROM time_IO"
                        cur.execute(query)
                        id = cur.fetchall()[0][0]+1
                        cv2.imwrite("Storage/Check-out/"+str(id) + ".jpg", img_save[top:bottom,left:right])

                        if model == 2:
                            # reload model user
                            enc = "model_FD/user/encodings.pickle"
                            data = pickle.loads(open(enc, "rb").read())
                            print("Xoa hinh anh cua visitor")
                            cvt_str_lp = str_lp.replace(str_lp,"'"+str_lp+"'")
                            id_cur = conn.cursor()
                            query = "SELECT studentID FROM time_IO where LicensePlate="+cvt_str_lp+"ORDER BY id DESC LIMIT 1"
                            id_cur.execute(query)
                            owner = id_cur.fetchall()
                            studentID = owner[0][0]
                            files = glob.glob('model_FD/new_user/dataset/'+studentID+'/*.jpg')
                            for f in files:
                                try:
                                    os.remove(f)
                                except:
                                    print("Delete failed")
                            try:
                                os.rmdir("model_FD/new_user/dataset/"+studentID)
                            except:
                                print("delete failed")

                        #Lay thoi gian hien tai
                        now = datetime.now()
                        # convert thoi gian
                        fm_time = now.strftime("%H:%M:%S %d/%m/%Y")
                        status = 'OUT'
                        if new_user == 1:
                            ins = "INSERT INTO time_IO(studentID,LicensePlate,time,status,newUser) VALUES('AdminAccept','"+str_lp+"','"+fm_time+"','"+status+"',1)"
                        else:
                            ins = "INSERT INTO time_IO(studentID,LicensePlate,time,status,newUser) VALUES('OwnerAccept','"+str_lp+"','"+fm_time+"','"+status+"',0)"

                        print("Insert succesfully!!")
                        print(ins)
                        conn.execute(ins)
                        conn.commit()


                        # cv2.destroyWindow('checkout')
                        # cv2.destroyWindow('checkin')
                        
                        #doi 5s cho user di qua va reset variable
                        img_check_in = None
                        next =1 
                        new_user = 1
                        have_name = 0
                        str_lp = ""
                        name = ""
                        have_lp = 0
                        thongbao = 0
                        studentId_of_LP = ""
                        lp_Registered = 0
                        finish_detect = 0
                        use_face_detect = 0
                        studentId = ""
                        model = 1
                        wait_start = 0
                        adminAccept = 0
                        not_owner= "Khong phai chu xe!"
                        not_owner_next= "Bam dau cach de cho qua!"
                        list_ownew = []
                        print("----------------------NEXT-----------------------")
                if adminAccept == 2:
                        print("Da tam giu xe va khong cho qua!!")
                        if model == 2:
                            # reload model user
                            enc = "model_FD/user/encodings.pickle"
                            data = pickle.loads(open(enc, "rb").read())

                        #doi 5s cho user di qua va reset variable
                        img_check_in = None
                        next =1 
                        new_user = 1
                        have_name = 0
                        str_lp = ""
                        name = ""
                        have_lp = 0
                        thongbao = 0
                        studentId_of_LP = ""
                        lp_Registered = 0
                        finish_detect = 0
                        use_face_detect = 0
                        studentId = ""
                        model = 1
                        wait_start = 0
                        adminAccept = 0
                        not_owner= "Khong phai chu xe!"
                        not_owner_next= "Bam dau cach de cho qua!"
                        list_ownew = []
                        print("----------------------NEXT-----------------------")
        
        cv2.imshow('checkout',frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    conn.close()
    cap.release()
    cv2.destroyAllWindows()

# print("Loading model charect-detect...")
digit_w = 30
digit_h = 60
model_svm = cv2.ml.SVM_load('model_CD/svm.xml')

#==========================================================================================================================

class Main(object):
	__user_name = ""
	def getUser_Name(self):
		return self.__user_name

	def __init__(self,user_name):
		self.__user_name = user_name

		#database name
		self.DBName = "DB/mydb.db"
		#Name of table in database
		self.Tb_User_info = "info_User"
		self.TB_Registered_Info = "lp_Registered"
		self.Tb_Time_IO = "time_IO"  

		#chieu dai rong cua man hinh
		x = 1300 
		y = 600
		screen = str(x)+"x"+str(y)
		self.MainForm = Tk()
		user_name_login = self.getUser_Name()
		self.MainForm.title("Manager ("+user_name_login+")")
		self.MainForm.geometry(screen)


		self.MainForm.geometry("+100+100")	
		
		#create Toolbar
		toolbar_main = Frame(self.MainForm,bg="gray")
		width = 480
		btnAdmin = Button(toolbar_main,text="Admin",width=width,command=self.open_Admin_Form)
		btnAdmin.pack(side=TOP,padx=4,pady=2)

		frame_For_Check_In_Out = Frame(toolbar_main,bg='gray')
		frame_For_Check_In_Out.pack(fill=X)

		btnCheck_In = Button(frame_For_Check_In_Out,text="Check In",fg='blue',width=int(77),command=checkin_main)#============================================= button check in
		btnCheck_In.pack(side=LEFT,padx=4,pady=2)

		btnCheck_Out = Button(frame_For_Check_In_Out,text="Check Out",fg='blue',width=int(x),command=checkout_main)#============================================= button check out
		btnCheck_Out.pack(side=LEFT,padx=4,pady=2)


		btnExit = Button(toolbar_main,text="Exit",width=width,command=self.exit)
		btnExit.pack(side=TOP,padx=4,pady=2)
		toolbar_main.pack(side=TOP,fill=X)
		#--------end Toolbar


		#create main Tabcontrol
		tabcontrol_main = ttk.Notebook()

		

		#tab Time_IO
		time_io = ttk.Frame(tabcontrol_main)
		tabcontrol_main.add(time_io,text="Time IO")
		
		#------end tab time IO




		#tab user
		user = ttk.Frame(tabcontrol_main)
		tabcontrol_main.add(user,text="User")

		#create user tabcontroll in user in Main tabcontrol
		tabcontrol_user = ttk.Notebook(user)

		user_info = ttk.Frame(tabcontrol_user)
		registered_info = ttk.Frame(tabcontrol_user)
		sign_up = ttk.Frame(tabcontrol_user)
		

		tabcontrol_user.add(user_info,text="User Info")
		tabcontrol_user.add(registered_info,text="Registered Info")
		tabcontrol_user.add(sign_up,text="Sign Up")


		# create Frame new user in sign up
		new_user = self.create_Frame_To_Show_Data(sign_up,x,y)
		new_rlp = self.create_Frame_To_Edit(sign_up,x,y)

		frame_of_New_User = Frame(new_user,bg='gray',height=20)
		frame_of_New_User.pack(side=TOP,fill=X)
		Label(frame_of_New_User,text="CREATE NEW USER").pack(padx=2,pady=2)


		#Tab SIGN UP
#===============================================================
		z = 100
		t = 40
		Label(new_user,text="ID User:",width=z).pack()
		self.txtID_Of_New_User = Entry(new_user,width=t)
		self.txtID_Of_New_User.pack(padx=4,pady=2)
		Label(new_user,text="Name:",width=z).pack()
		self.txtName_of_New_User = Entry(new_user,width=t)
		self.txtName_of_New_User.pack(padx=4,pady=2)
		Label(new_user,text="Phone Number:",width=z).pack()
		self.txtPhone_Number_of_New_User = Entry(new_user,width=t)
		self.txtPhone_Number_of_New_User.pack(padx=4,pady=2)
		Label(new_user,text="Email:",width=z).pack()
		self.txtEmail_of_New_User = Entry(new_user,width=t)
		self.txtEmail_of_New_User.pack(padx=4,pady=2)
		Label(new_user,text="Adress:",width=z).pack()
		self.txtAdress_of_New_User = Entry(new_user,width=t)
		self.txtAdress_of_New_User.pack(padx=4,pady=2)
        

		Label(new_user,text="",width=z).pack()
		frame_For_Btn_Of_New_User = Frame(new_user,height=20)
		frame_For_Btn_Of_New_User.pack()

		btn_New_User = Button(frame_For_Btn_Of_New_User,text="Đăng kí thông tin",width=20,fg='green',command=self.add_For_User)
		btn_New_User.pack(padx=4,pady=2,side=RIGHT)

		btn_Take_IMG = Button(frame_For_Btn_Of_New_User,text="Lấy hình ảnh",width=20,fg='green',command=self.getImage_For_Sign_Up)#-------------------------------------- button lay hinh anh
		btn_Take_IMG.pack(padx=4,pady=2,side=RIGHT)

		frame_Of_Train = Frame(new_user)
		frame_Of_Train.pack()

		Label(frame_Of_Train,text="",width=z).pack()
		btn_Take_IMG = Button(frame_Of_Train,text="Train",width=20,fg='green',command="trainU")#-------------------------------------- Train
		btn_Take_IMG.pack(padx=4,pady=2,side=TOP)
        





		frame_of_New_RLP = Frame(new_rlp,bg='gray',height=20)
		frame_of_New_RLP.pack(side=TOP,fill=X)
		Label(frame_of_New_RLP,text="CREATE NEW RLP").pack(padx=2,pady=2)

		#create Form edit for User info
		Label(frame_of_New_RLP,text="ID User:",width=x,bg='gray').pack()
		self.txtID_Of_New_Registered = Entry(frame_of_New_RLP,width=t)
		self.txtID_Of_New_Registered.pack(padx=4,pady=2)
		Label(frame_of_New_RLP,text="Biển số:",width=x,bg='gray').pack()
		self.txtLicense_Plate_Of_New_RLP = Entry(frame_of_New_RLP,width=t)
		self.txtLicense_Plate_Of_New_RLP.pack(padx=4,pady=2)
		Label(frame_of_New_RLP,text="",width=x,bg='gray').pack()

		frame_For_Btn_Of_New_RLP = Frame(frame_of_New_RLP,bg='gray',height=20)
		frame_For_Btn_Of_New_RLP.pack()
		btn_New_RLP = Button(frame_For_Btn_Of_New_RLP,text="Đăng kí",width=20,fg='green',command=self.add_For_Registered)
		btn_New_RLP.pack()
#===============================================================end Tab Sign Up
		


				#TAB Time IO
#==============================================================================
		#create Toolbar
		toolbar_Time_IO_Show = Frame(time_io,bg="gray")
		toolbar_Time_IO_Show.pack(side=TOP,fill=X)

		Label(toolbar_Time_IO_Show,text="",bg="gray").pack()



		toolbar_Time_IO_Btn = Frame(time_io,bg="gray")
		toolbar_Time_IO_Btn.pack(side=TOP,fill=X)

		toolbar_Time_IO_Btn1 = Frame(toolbar_Time_IO_Btn,bg='gray',width=x/3)
		toolbar_Time_IO_Btn1.pack()

		
		btnShow_Time_IO = Button(toolbar_Time_IO_Btn1,text="Refesh",width=30,command=self.show_Data_of_Time_Io)
		btnShow_Time_IO.pack(side=LEFT,padx=2,pady=2)

		btn_Find_All_IO = Button(toolbar_Time_IO_Btn1,text="Tìm kiếm",width=30,command=self.finding_All_For_Time_IO)
		btn_Find_All_IO.pack(side=LEFT, padx=4,pady=4)



		toolbar_Time_IO_Edit_Text = Frame(time_io,bg="gray")
		toolbar_Time_IO_Edit_Text.pack(side=TOP,fill=X)

		toolbar_Time_IO_Edit_Text1 = Frame(toolbar_Time_IO_Edit_Text,bg='gray',width=x/3)
		toolbar_Time_IO_Edit_Text1.pack()


		Label(toolbar_Time_IO_Edit_Text1,text="ID USER: ",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtID_For_Find_IO = Entry(toolbar_Time_IO_Edit_Text1)
		self.txtID_For_Find_IO.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Biển số: ",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtLicense_For_Find_IO = Entry(toolbar_Time_IO_Edit_Text1)
		self.txtLicense_For_Find_IO.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Ngày",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtDay_For_Find_IO = Entry(toolbar_Time_IO_Edit_Text1,width=7)
		self.txtDay_For_Find_IO.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Tháng",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtMonth_For_Find_IO = Entry(toolbar_Time_IO_Edit_Text1,width=7)
		self.txtMonth_For_Find_IO.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)

		Label(toolbar_Time_IO_Edit_Text1,text="Năm",bg='gray').pack(padx=2,pady=2,side=LEFT)
		self.txtYear_For_Find_IO = Entry(toolbar_Time_IO_Edit_Text1,width=7)
		self.txtYear_For_Find_IO.pack(padx=2,pady=2,side=LEFT)
		Label(toolbar_Time_IO_Edit_Text1,text="",bg='gray',width=5).pack(padx=2,pady=2,side=LEFT)



		#Label(toolbar_Time_IO_Btn3,text="asg").pack(side=TOP, padx=4,pady=4)

		# btnShow_Time_IO = Button(toolbar_Time_IO_Btn,text="Refesh",width=20,command=self.show_Data_of_Time_Io)
		# btnShow_Time_IO.pack(padx=2,pady=2)


		#-------ENd Toolbar

		#create Treeview
		self.treeview_for_time_io = ttk.Treeview(time_io,column=(1,2,3,4,5,6), show="headings", height=y)
		self.treeview_for_time_io.heading(1,text="ID")
		self.treeview_for_time_io.heading(2,text="ID USER")
		self.treeview_for_time_io.heading(3,text="LICENSE PLATE")
		self.treeview_for_time_io.heading(4,text="TIME")
		self.treeview_for_time_io.heading(5,text="STATUS")
		self.treeview_for_time_io.heading(6,text="NEW USER")
		self.treeview_for_time_io.pack()
		#----------END Tree View
#=============================END Tab time IO



		#Tab User Info
#==========================================================================================================
		# tao 4 nut refesh, tim kiem, sua, xoa cho table user info
		toolbar_user_info = self.create_Toolbar_Edit_Delete(user_info,self.show_Data_of_User_Info,self.finding_ID_For_User_Info,self.edit_For_User_Info,self.delete_For_User_Info)
		#lay cho de show data trong table user info
		frame_of_data_in_user_info = self.create_Frame_To_Show_Data(user_info,x,y)
		#lay cho de tao form edit
		frame_of_Edit_in_user_info = self.create_Frame_To_Edit(user_info,x,y)


		#create Form edit for User info
		Label(frame_of_Edit_in_user_info,text="ID User:",width=x).pack()
		self.txtID_Of_User_Info = Entry(frame_of_Edit_in_user_info,width=x)
		self.txtID_Of_User_Info.pack(padx=4,pady=2)
		Label(frame_of_Edit_in_user_info,text="Name:",width=x).pack()
		self.txtName = Entry(frame_of_Edit_in_user_info,width=x)
		self.txtName.pack(padx=4,pady=2)
		Label(frame_of_Edit_in_user_info,text="Phone Number:",width=x).pack()
		self.txtPhone_Number = Entry(frame_of_Edit_in_user_info,width=x)
		self.txtPhone_Number.pack(padx=4,pady=2)
		Label(frame_of_Edit_in_user_info,text="Email:",width=x).pack()
		self.txtEmail = Entry(frame_of_Edit_in_user_info,width=x)
		self.txtEmail.pack(padx=4,pady=2)
		Label(frame_of_Edit_in_user_info,text="Adress:",width=x).pack()
		self.txtAdress = Entry(frame_of_Edit_in_user_info,width=x)
		self.txtAdress.pack(padx=4,pady=2)
		#------end Form edit for User info

		#create Frame for note
		Label(frame_of_Edit_in_user_info,text="",width=x).pack()
		Label(frame_of_Edit_in_user_info,text="",bg='gray',width=x).pack()
		Label(frame_of_Edit_in_user_info,text="(*) Để tìm kiếm, xóa \nvui lòng nhâp ID của User vào ô ID User!\n",bg='gray').pack()
		Label(frame_of_Edit_in_user_info,text="(*) Vui lòng điền đầy đủ thông tin \nvào các ô để có thể chỉnh sửa!",bg='gray').pack()
		#--------end Frame for note

		#create Treeview de hien thi data 
		self.treeview_for_user_info = ttk.Treeview(frame_of_data_in_user_info,column=(1,2,3,4,5), show="headings", height=y)
		self.treeview_for_user_info.heading(1,text="ID USER")
		self.treeview_for_user_info.heading(2,text="NAME")
		self.treeview_for_user_info.heading(3,text="PHONE NUMBER")
		self.treeview_for_user_info.heading(4,text="EMAIL")
		self.treeview_for_user_info.heading(5,text="ADRESS")
		self.treeview_for_user_info.pack()
#========================= END Tab User Info




		#Tab Registered Info
#=================================================================================================================
		# tao 4 nut refesh, tim kiem, sua, xoa cho table registered info
		toolbar_registered_info = self.create_Toolbar_Edit_Delete(registered_info,self.show_Data_of_Registered_Info,self.finding_ID_For_Registered_Info,self.edit_For_Registered_Info,self.delete_For_Registered_Info)
		#lay cho de show data trong table registered info
		frame_of_data_in_registered_info = self.create_Frame_To_Show_Data(registered_info,x,y)
		#lay cho de tao form edit
		frame_of_edit_in_registered_info = self.create_Frame_To_Edit(registered_info,x,y)


		#create Form edit for User info
		Label(frame_of_edit_in_registered_info,text="ID User:",width=x).pack()
		self.txtID_Of_Registered_Info = Entry(frame_of_edit_in_registered_info,width=x)
		self.txtID_Of_Registered_Info.pack(padx=4,pady=2)
		Label(frame_of_edit_in_registered_info,text="Biển số:",width=x).pack()
		self.txtLicense_Plate = Entry(frame_of_edit_in_registered_info,width=x)
		self.txtLicense_Plate.pack(padx=4,pady=2)

		Label(frame_of_edit_in_registered_info,text="Biển số mới: (Nhập biển số mới khi chỉnh sửa)",width=x).pack()
		self.txtLicense_Plate_New = Entry(frame_of_edit_in_registered_info,width=x)
		self.txtLicense_Plate_New.pack(padx=4,pady=2)
		#------end Form edit for User info

		#create Frame for note
		Label(frame_of_edit_in_registered_info,text="",width=x).pack()
		Label(frame_of_edit_in_registered_info,text="",bg='gray',width=x).pack()
		Label(frame_of_edit_in_registered_info,text="(*) Để tìm kiếm, xóa \nvui lòng nhâp ID của User vào ô ID User!\n",bg='gray').pack()
		Label(frame_of_edit_in_registered_info,text="(*) Vui lòng điền đầy đủ thông tin \nvào các ô để có thể chỉnh sửa!\n",bg='gray').pack()
		Label(frame_of_edit_in_registered_info,text="(*) Khi chỉnh sửa\n\"Biển số\" sẽ là biển số cần thay đổi\n\"Biển số mới\" sẽ là biển số sau khi thay đổi!",bg='gray').pack()
		#--------end Frame for note

		#create Treeview de hien thi data 
		self.treeview_for_registered_info = ttk.Treeview(frame_of_data_in_registered_info,column=(1,2,3), show="headings", height=y)
		self.treeview_for_registered_info.heading(1,text="ID")
		self.treeview_for_registered_info.heading(2,text="ID USER")
		self.treeview_for_registered_info.heading(3,text="LICENSE PLATE")
		self.treeview_for_registered_info.pack()
		#-------END Tree View

		
#============================ END tab Registered Info

		#Load data init
		self.show_Data_of_Time_Io()
		self.show_Data_of_User_Info()
		self.show_Data_of_Registered_Info()

		# self.stop_threads = Event()
		# self.thread_Load_Data_IO = threading.Thread(target=self.thread_show_Data_of_Time_Io)
		# self.start_Thread_Show_IO()




		tabcontrol_user.pack(fill="both")
		#-------end tab user

		tabcontrol_main.pack(fill="both")
		#---------end Tabcontrol


		mainloop()





	#ham samloz cua t. khong can quan tam den
	def changeTextForFilIntoQuery(self,ValueCondition):
		return '"'+ValueCondition+'"'

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

	# thoat
	def exit(self):
		msgBox = messagebox.askquestion("Thông báo","Bạn có muốn thoát không!")
		if(msgBox == 'yes'):
			self.MainForm.destroy()

	#tao button edit va delete
	def create_Toolbar_Edit_Delete(self,name,command1,command2,command3,command4):
		width = 15
		toolbar_user_info = Frame(name,bg="gray")
		btnEelete = Button(toolbar_user_info,text="Xóa",width=width,command=command4)
		btnEelete.pack(side=RIGHT,padx=2,pady=2)
		btnEdit = Button(toolbar_user_info,text="Sửa",width=width,command=command3)
		btnEdit.pack(side=RIGHT,padx=2,pady=2)
		btnFind = Button(toolbar_user_info,text="Tìm kiếm",width=width,command=command2)
		btnFind.pack(side=RIGHT,padx=2,pady=2)
		btnShow = Button(toolbar_user_info,text="Show All",width=width,command=command1)
		btnShow.pack(side=RIGHT,padx=2,pady=2)
		toolbar_user_info.pack(side=TOP,fill=X)


	#lay frame hien thi data
	def create_Frame_To_Show_Data(self,name,x,y):
		frame_of_data = Frame(name,width=x/10*6,height=y,borderwidth=1)
		frame_of_data.pack(side=LEFT,fill='both',padx=4,pady=4)
		return frame_of_data

	#lay frame hien thi edit form
	def create_Frame_To_Edit(self,name,x,y):
		frame_of_edit = Frame(name,width=x/10*4,height=y,borderwidth=1,bg='gray')
		frame_of_edit.pack(side=RIGHT,fill='both',padx=4,pady=4)
		return frame_of_edit

	#select de lay data trong database
	def take_data(self,tableName):
		tableName = self.changeTextForFilIntoQuery(tableName)
		Query = "SELECT * FROM "+tableName
		return self.execute_Query(Query)





	#show du lieu cua bang User Info
	def show_Data_of_User_Info(self):
		children = self.treeview_for_user_info.get_children()
		for x in children:
			self.treeview_for_user_info.delete(x)
		for x in self.take_data(self.Tb_User_info):
			self.treeview_for_user_info.insert('','end',values=x)

	#show du lieu cua bang registered Info
	def show_Data_of_Registered_Info(self):
		children = self.treeview_for_registered_info.get_children()
		for x in children:
			self.treeview_for_registered_info.delete(x)
		for x in self.take_data(self.TB_Registered_Info):
			self.treeview_for_registered_info.insert('','end',values=x)

	def show_Data_of_Time_Io(self):
		self.clear_Tree_Time_IO()
		for x in reversed(self.take_data(self.Tb_Time_IO)):
			self.treeview_for_time_io.insert('','end',values=x)
	def thread_show_Data_of_Time_Io(self):
		while not self.stop_threads.is_set():
			self.show_Data_of_Time_Io()
			time.sleep(2)

	# ham tim kiem voi ID user
	def finding_ID(self,tableName,id_user):
		tableName = self.changeTextForFilIntoQuery(tableName)
		Query = " SELECT * FROM "+tableName+" WHERE studentID = "+id_user
		return self.execute_Query(Query)

	# ham tim kiem voi ID user tren table user info
	def finding_ID_For_User_Info(self):
		id_user = self.txtID_Of_User_Info.get().strip()
		if (id_user):
			if(self.check_Exists_Id_User(self.Tb_User_info,id_user)):
				children = self.treeview_for_user_info.get_children()
				for x in children:
					self.treeview_for_user_info.delete(x)
				data = self.finding_ID(self.Tb_User_info,id_user)
				for x in data:
					self.treeview_for_user_info.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để tìm kiếm")


	# ham tim kiem voi ID user tren table user info
	def finding_ID_For_Registered_Info(self):
		id_user = self.txtID_Of_Registered_Info.get().strip()
		if (id_user):
			if(self.check_Exists_Id_User(self.TB_Registered_Info,id_user)):
				children = self.treeview_for_registered_info.get_children()
				for x in children:
					self.treeview_for_registered_info.delete(x)
				data = self.finding_ID(self.TB_Registered_Info,id_user)
				for x in data:
					self.treeview_for_registered_info.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để tìm kiếm")

	#ham kiem tra xem user co ID duoc nhap vao co tom tai khong
	def check_Exists_Id_User(self,tableName,id_user):
		ListUser = self.take_data(tableName)
		if(tableName == self.Tb_User_info):
			for x in ListUser:	
				if(id_user == x[0]):
					return True
			return False
		else:
			for x in ListUser:
				if(id_user == x[1]):
					return True
			return False


	#Ham chinh sua thong tin cho table User Info
	def edit_For_User_Info(self):
		tableName = self.Tb_User_info
		tableName = self.changeTextForFilIntoQuery(tableName)
		id_user = self.txtID_Of_User_Info.get().strip()
		if(id_user):
			if(self.check_Exists_Id_User(self.Tb_User_info,id_user)):
				name = self.txtName.get().strip()
				phone_number = self.txtPhone_Number.get().strip()
				email = self.txtEmail.get().strip()
				address = self.txtAdress.get().strip()

				if(name and phone_number and email and address):
					msg = messagebox.askquestion("","Bạn có chắc muốn thay đổi thông tin ?")
					if(msg == 'yes'):
						name = self.changeTextForFilIntoQuery(name)
						phone_number = self.changeTextForFilIntoQuery(phone_number)
						email = self.changeTextForFilIntoQuery(email)
						address = self.changeTextForFilIntoQuery(address)
						Query = " UPDATE "+tableName+" SET name = "+name+", phoneNumber = "+phone_number+",email = "+email+", address = "+address+" WHERE studentID = "+id_user
						self.execute_Query(Query)
						messagebox.showinfo("","Cập nhật thông tin thành công!")
						self.show_Data_of_User_Info()
				else:
					messagebox.showinfo("","Vui lòng điền đầy đủ tất cả thông tin!")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để thực hiện sửa thông tin")

	#Ham chinh sua thong tin cho table Registered_Info
	def edit_For_Registered_Info(self):
		TB_Registered_Info = self.TB_Registered_Info
		TB_Registered_Info = self.changeTextForFilIntoQuery(TB_Registered_Info)
		id_user = self.txtID_Of_Registered_Info.get().strip()
		if(id_user):
			if(self.check_Exists_Id_User(self.TB_Registered_Info,id_user)):
				License_Plate = self.txtLicense_Plate.get().strip()
				if(License_Plate):
					if(self.check_Exists_License_Plate(self.TB_Registered_Info,License_Plate)):
						License_Plate_New = self.txtLicense_Plate_New.get().strip()
						if(License_Plate_New):
							if(self.check_License_Plate(License_Plate_New)):
								msg = messagebox.askquestion("","Bạn có chắc muốn thay đổi thông tin ?")
								if(msg == 'yes'):
									License_Plate = self.changeTextForFilIntoQuery(License_Plate)
									License_Plate_New = self.changeTextForFilIntoQuery(License_Plate_New)

									Query = " UPDATE "+TB_Registered_Info+" SET LicensePlate = "+License_Plate_New+" WHERE studentID = "+id_user+" AND LicensePlate = "+License_Plate
									self.execute_Query(Query)
									messagebox.showinfo("","Cập nhật thông tin thành công!")
									self.show_Data_of_Registered_Info()
						else:
							messagebox.showinfo("","Vui lòng điền biển số xe mới !")
					else:
						messagebox.showinfo("","Biển số cần sửa thông tin không tồn tại !")
				else:
					messagebox.showinfo("","Vui lòng điền biển số xe !")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để thực hiện sửa thông tin")

	#Ham xoa user voi ID nhap vao
	def delete_For_Registered_Info(self):
		TB_Registered_Info = self.TB_Registered_Info
		TB_Registered_Info = self.changeTextForFilIntoQuery(TB_Registered_Info)
		id_user = self.txtID_Of_Registered_Info.get().strip()
		if(id_user):
			if(self.check_Exists_Id_User(self.TB_Registered_Info,id_user)):
				License_Plate = self.txtLicense_Plate.get().strip()
				if(License_Plate):
					msg = messagebox.askquestion("","Bạn có chắc muôn xóa biển số này?")
					if(msg == 'yes'):
						License_Plate = self.changeTextForFilIntoQuery(License_Plate)
						Query = " DELETE FROM "+TB_Registered_Info+" WHERE studentID = "+id_user+" and LicensePlate = "+License_Plate
						self.execute_Query(Query)
						messagebox.showinfo("","Xóa thông tin thành công!")
						self.show_Data_of_Registered_Info()
				else:
					messagebox.showinfo("","Vui lòng điền biển số xe !")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để thực hiện chức năng")

	def delete_For_User_Info(self):
		TB_Registered_Info = self.TB_Registered_Info
		TB_Registered_Info = self.changeTextForFilIntoQuery(TB_Registered_Info)
		Tb_User_info = self.Tb_User_info
		Tb_User_info = self.changeTextForFilIntoQuery(Tb_User_info)

		id_user = self.txtID_Of_User_Info.get().strip()
		if(id_user):
			if(self.check_Exists_Id_User(self.Tb_User_info,id_user)):
				msg = messagebox.askquestion("","Bạn có chắc muôn xóa tất cả thông tin của User này?")
				if(msg == 'yes'):
					Query1 = " DELETE FROM "+TB_Registered_Info+" WHERE studentID = "+id_user
					self.execute_Query(Query1)
					messagebox.showinfo("","Xóa thông tin đăng kí biển số thành công!")
					Query2 = " DELETE FROM "+Tb_User_info+" WHERE studentID = "+id_user
					self.execute_Query(Query2)
					messagebox.showinfo("","Đã xóa tất cả thông tin!")
					self.show_Data_of_User_Info()
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại ID USER")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để thực hiện chức năng")

	def check_Permission_Of_Account(self,user_name):
		user_name = self.changeTextForFilIntoQuery(user_name)
		Query = " SELECT permission FROM Account WHERE user_name = "+user_name
		conn = db.connect("DB/Account.db")
		cur = conn.cursor()
		cur.execute(Query)
		conn.commit()
		data = cur.fetchall()
		cur.close()
		conn.close()
		if(int(data[0][0])):
			return True
		else:
			return False

	def open_Admin_Form(self):
		user_name_login = self.getUser_Name()
		if(self.check_Permission_Of_Account(user_name_login)):
			self.MainForm.destroy()
			Admin(self.getUser_Name())
		else:
			messagebox.showinfo("","Chỉ Admin mới có quyền truy cập vào đây!")



	def add_For_User(self):
		id_user = self.txtID_Of_New_User.get().strip()
		user_name = self.txtName_of_New_User.get().strip()
		phone_number = self.txtPhone_Number_of_New_User.get().strip()
		email = self.txtEmail_of_New_User.get().strip()
		address = self.txtAdress_of_New_User.get().strip()

		if(id_user):
			if(self.check_Exists_Id_User(self.Tb_User_info,id_user) != True):
				if(user_name and  phone_number and email and address):
					msg = messagebox.askquestion("","Bạn có muốn thên USER này ?")
					if(msg == 'yes'):
						ArrayValue = [id_user,user_name,phone_number,email,address]
						self.insert(self.Tb_User_info,ArrayValue)
						messagebox.showinfo("","Đã thêm USER thành công")
				else:
					messagebox.showinfo("","Vui lòng điền đầy đủ thông tin")
			else:
				messagebox.showinfo("","ID USER này đã tồn tại")
		else:
			messagebox.showinfo("","Vui lòng điền ID USER")



	def add_For_Registered(self):
		id_user = self.txtID_Of_New_Registered.get().strip()
		license_plate = self.txtLicense_Plate_Of_New_RLP.get().strip()

		if(id_user):
			if(self.check_Exists_Id_User(self.Tb_User_info,id_user)):
				if(license_plate):
					if(self.check_License_Plate(license_plate)):
						msg =messagebox.askquestion("","Bạn có muốn thêm thông tin này ?")
						if(msg == 'yes'):
							ArrayValue = [id_user,license_plate]
							self.insertNULL(self.TB_Registered_Info,ArrayValue)
							messagebox.showinfo("","Đã thêm thông tin thành công")
				else:
					messagebox.showinfo("","Vui lòng điền biển số")
			else:
				messagebox.showinfo("","không tìm thấy ID USER này")
		else:
			messagebox.showinfo("","Vui lòng điền ID USER")


	def insert(self,TableName, ArrayValue):
		stri = self.arrToString(ArrayValue)
		Query = "INSERT INTO "+TableName+" VALUES ( "+stri+" )"
		self.execute_Query(Query)
		return True

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

	def check_License_Plate(self,License_Plate):
		if(len(License_Plate) >= 9 and len(License_Plate) <= 10):
			if(License_Plate[4] == '-'):
				license_plate2 = License_Plate.split('-')
				if(license_plate2[1].isnumeric()):
					if(license_plate2[0][0].isnumeric() and license_plate2[0][1].isnumeric()):
						if(license_plate2[0][2].isnumeric() != True):
							return True
						else:
							messagebox.showinfo("","Mã khu vực không hợp lệ")
					else:
						messagebox.showinfo("","Mã tỉnh không hợp lệ")
				else:
					messagebox.showinfo("","Biển số không hợp lệ")
			else:
				messagebox.showinfo("","Kí tự nối không hợp lệ")
		else:
			messagebox.showinfo("","Độ dài biển số không đúng quy định")
		return False

	def check_Exists_License_Plate(self,tableName,License_Plate):
		data = self.take_data(tableName)
		for x in data:
			if (x[2] == License_Plate):
				return True
		return False


	def start_Thread_Show_IO(self):
		if(not self.thread_Load_Data_IO.is_alive()):
			self.thread_Load_Data_IO.start()
	def stop_Thread_Show_IO(self):
		if(self.thread_Load_Data_IO.is_alive()):
			self.stop_threads.set()
			self.thread_Load_Data_IO.join()

	def finding_DMY(self,tableName,day,month,year):
		tableName = self.changeTextForFilIntoQuery(tableName)
		DMY = day+'/'+month+'/'+year
		Query = ' SELECT * FROM '+tableName+' WHERE time LIKE "%'+DMY+'%"'
		return self.execute_Query(Query)

	def find_ID_User_For_Time_IO(self):
		id_user = self.txtID_For_Find_IO.get().strip()
		if (id_user):
			if(self.check_Exists_Id_User(self.Tb_Time_IO,id_user)):
				self.clear_Tree_Time_IO()
				data = self.finding_ID(self.Tb_Time_IO,id_user)
				for x in data:
					self.treeview_for_time_io.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		else:
			messagebox.showinfo("","Vui lòng nhập ID USER để tìm kiếm")

	def find_RLP_For_Time_IO(self):
		License_Plate = self.txtLicense_For_Find_IO.get().strip()
		if (License_Plate):
			if(self.check_Exists_License_Plate(self.Tb_Time_IO,License_Plate)):
				self.clear_Tree_Time_IO()
				data = self.finding_License_Plate(self.Tb_Time_IO,License_Plate)
				for x in data:
					self.treeview_for_time_io.insert('','end',values=x)
			else:
				messagebox.showinfo("","Không tìm thấy Biển số này\nVui lòng kiểm tra lại")
		else:
			messagebox.showinfo("","Vui lòng nhập biển số để tìm kiếm")

	def finding_License_Plate(self,tableName,License_Plate):
		tableName = self.changeTextForFilIntoQuery(tableName)
		License_Plate = self.changeTextForFilIntoQuery(License_Plate)
		Query = " SELECT * FROM "+tableName+" WHERE LicensePlate = "+License_Plate
		return self.execute_Query(Query)

	def finding_DMY_For_Time_IO(self):
		Day = self.txtDay_For_Find_IO.get().strip()
		Month = self.txtMonth_For_Find_IO.get().strip()
		Year = self.txtYear_For_Find_IO.get().strip()
		if (Day and Month and Year):
			if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
				self.clear_Tree_Time_IO()
				data = self.finding_DMY(self.Tb_Time_IO,Day,Month,Year)
				for x in data:
					self.treeview_for_time_io.insert('','end',values=x)
			else:
				messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
		else:
			messagebox.showinfo("","Vui lòng nhập đầy đủ Ngày Tháng Năm tìm kiếm")


	def finding_All_For_Time_IO(self):
		id_user = self.txtID_For_Find_IO.get().strip()
		license_plate = self.txtLicense_For_Find_IO.get().strip()
		Day = self.txtDay_For_Find_IO.get().strip()
		Month = self.txtMonth_For_Find_IO.get().strip()
		Year = self.txtYear_For_Find_IO.get().strip()
		DMY = Day+'/'+Month+'/'+Year
		if(id_user and license_plate and Day and Month and Year):
			if(self.check_Exists_Id_User(self.Tb_Time_IO,id_user)):
				if(self.check_Exists_License_Plate(self.Tb_Time_IO,license_plate)):
					if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
						id_user = self.changeTextForFilIntoQuery(id_user)
						license_plate = self.changeTextForFilIntoQuery(license_plate)
						self.clear_Tree_Time_IO()
						Query = " SELECT * FROM time_IO WHERE  studentID = "+id_user+" and  LicensePlate = "+license_plate+'  and time like "%'+DMY+'%"'
						data = self.execute_Query(Query)
						for x in data:
							self.treeview_for_time_io.insert('','end',values=x)
					else:
						messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
				else:
					messagebox.showinfo("","Không tìm thấy Biển số này\nVui lòng kiểm tra lại")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		elif(id_user and license_plate):
			if(self.check_Exists_Id_User(self.Tb_Time_IO,id_user)):
				if(self.check_Exists_License_Plate(self.Tb_Time_IO,license_plate)):
					id_user = self.changeTextForFilIntoQuery(id_user)
					license_plate = self.changeTextForFilIntoQuery(license_plate)
					self.clear_Tree_Time_IO()
					Query = " SELECT * FROM time_IO WHERE  studentID = "+id_user+" and  LicensePlate = "+license_plate
					data = self.execute_Query(Query)
					for x in data:
						self.treeview_for_time_io.insert('','end',values=x)
				else:
					messagebox.showinfo("","Không tìm thấy Biển số này\nVui lòng kiểm tra lại")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		elif(id_user and Day and Month and Year):
			if(self.check_Exists_Id_User(self.Tb_Time_IO,id_user)):
				if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
					id_user = self.changeTextForFilIntoQuery(id_user)
					self.clear_Tree_Time_IO()
					Query = " SELECT * FROM time_IO WHERE  studentID = "+id_user+'  and time like "%'+DMY+'%"'
					data = self.execute_Query(Query)
					for x in data:
						self.treeview_for_time_io.insert('','end',values=x)
				else:
					messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
			else:
				messagebox.showinfo("","Không tìm thấy USER này\nVui lòng kiểm tra lại")
		elif(license_plate and Day and Month and Year):
			if(self.check_Exists_License_Plate(self.Tb_Time_IO,license_plate)):
				if(Day.isnumeric() and Month.isnumeric() and Year.isnumeric()):
					license_plate = self.changeTextForFilIntoQuery(license_plate)
					self.clear_Tree_Time_IO()
					Query = " SELECT * FROM time_IO WHERE  LicensePlate = "+license_plate+'  and time like "%'+DMY+'%"'
					data = self.execute_Query(Query)
					for x in data:
						self.treeview_for_time_io.insert('','end',values=x)
				else:
					messagebox.showinfo("","Vui lòng nhập Ngày Tháng Năm là số")
			else:
				messagebox.showinfo("","Không tìm thấy Biển số này\nVui lòng kiểm tra lại")
		elif(Day or Month or Year):
			self.finding_DMY_For_Time_IO()
		elif(license_plate):
			self.find_RLP_For_Time_IO()
		elif(id_user):
			self.find_ID_User_For_Time_IO()
		else:
			messagebox.showinfo("","Vui lòng điền thông tin để tìm kiếm")	

	def clear_Tree_Time_IO(self):
		children = self.treeview_for_time_io.get_children()
		for x in children:
			self.treeview_for_time_io.delete(x)


	def getImage(self,name):
	    cam = cv2.VideoCapture(0)
	    detector=cv2.CascadeClassifier('model_FD/user/haarcascade_frontalface_default.xml')
	    cam.set(3,640)
	    cam.set(4,480)

	    # print("model_FD/user/dataSet/"+name+ "/User.")
	    # insertOrUpdate(id,name)
	    folder="model_FD/user/dataset/"+name
	    os.mkdir(folder)
	    sampleNum=0
	    while(True):

	        ret, img = cam.read()

	        # Lật ảnh cho đỡ bị ngược
	        # img = cv2.flip(img,1)
	        faces = detector.detectMultiScale(img, 1.3, 5)
	        for (x, y, w, h) in faces:
	            # Vẽ hình chữ nhật quanh mặt nhận được
	            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
	            sampleNum = sampleNum + 1
	            # Ghi dữ liệu khuôn mặt vào thư mục dataSet
	            cv2.imwrite("model_FD/user/dataset/"+name+ "/" + str(sampleNum) + ".jpg", img[y:y + h, x:x + w])

	        cv2.imshow('frame', img)
	        # Check xem có bấm q hoặc trên 100 ảnh sample thì thoát
	        if cv2.waitKey(100) & 0xFF == ord('q'):
	            break
	        elif sampleNum>14:
	            break
	    cam.release()
	    cv2.destroyAllWindows()

	def getImage_For_Sign_Up(self):
		id_user = self.txtID_Of_New_User.get().strip()
		self.getImage(id_user)

	


if __name__ == '__main__':
	
	Main("admin")
