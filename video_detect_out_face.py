import cv2
import imutils
import numpy as np
from PIL import Image
import pytesseract
import pickle
import argparse
import face_recognition
import time
import sqlite3
from datetime import datetime
import os
# from model_FD.new_user.train import train
import glob
import smtplib

def overlay(l_img,s_img,x,y):
    s_img = cv2.resize(s_img,(100,100),interpolation = cv2.INTER_AREA)
    l_img[y:y+s_img.shape[0],x:x+s_img.shape[1]] = s_img

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

#Tim ra chuoi co xuat hien nhieu nhat (chong nhieu)
def find_max_str(list):
    max_str = list[0]
    max = list.count(list[0])
    for values in list:
        if max <= list.count(values):
            max_str = values
    # print(max_str)
    return max_str

if __name__ == "__main__":
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
    conn = sqlite3.connect("DB/mydb.db")

    #khoi tao bien, co
    skip_frame = 0
    str_lp = "90B2-99999"   #Sua cho nay
    name = ""
    have_lp = 1
    have_name = 1
    check_out = "Moi ban ra!!"
    add_user = "Vui long nhin thang vao camera"
    new_user = 1
    thongbao = 0
    start_time = 0 
    xacsuat = 0
    list = []
    values = ""
    studentId_of_LP = "1811060924"  #Sua cho nay
    lp_Registered = 0
    isStudent =0
    finish_detect = 0
    use_face_detect = 0
    training = 1
    sampleNum=0
    trained = 0
    reset = 0
    studentID = "1811060924"
    model = 1
    next = 1
    id_check_in = 1504
    img_check_in = None
    wait_start = 0
    adminAccept = 0
    list_owner = ["1811060924"]
    flagg = 0
    a=0
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
        # cv2.namedWindow('checkout')
        # cv2.moveWindow('checkout',400,100)
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
        if flagg == 0:
            a = time.time()
            flagg = 1
        if time.time() - a > 5:
            have_name = 0
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
                                    result = "nttuyen12052000@gmail.com"
                                    print(result)
                                    print("Sending email....")
                                    # mail_send(result)  #Sua
                                    next = 0
                                    new_user = 0
                                    wait_start = 1
                                    have_lp = 0
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
                    # conn.execute(ins)
                    # conn.commit()
                    
                    # if model == 2:
                    #     # reload model user
                    #     enc = "model_FD/user/encodings.pickle"
                    #     data = pickle.loads(open(enc, "rb").read())
                    #     print("Xoa hinh anh cua visitor")
                    #     files = glob.glob('model_FD/new_user/dataset/'+studentID+'/*.jpg')
                    #     for f in files:
                    #         try:
                    #             os.remove(f)
                    #         except:
                    #             print("Delete failed")
                    #     try:
                    #         os.rmdir("model_FD/new_user/dataset/"+studentID)
                    #     except:
                    #         print("delete failed")

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

                        # if model == 2:
                        #     # reload model user
                        #     enc = "model_FD/user/encodings.pickle"
                        #     data = pickle.loads(open(enc, "rb").read())
                        #     print("Xoa hinh anh cua visitor")
                        #     cvt_str_lp = str_lp.replace(str_lp,"'"+str_lp+"'")
                        #     id_cur = conn.cursor()
                        #     query = "SELECT studentID FROM time_IO where LicensePlate="+cvt_str_lp+"ORDER BY id DESC LIMIT 1"
                        #     id_cur.execute(query)
                        #     owner = id_cur.fetchall()
                        #     studentID = owner[0][0]
                        #     files = glob.glob('model_FD/new_user/dataset/'+studentID+'/*.jpg')
                        #     for f in files:
                        #         try:
                        #             os.remove(f)
                        #         except:
                        #             print("Delete failed")
                        #     try:
                        #         os.rmdir("model_FD/new_user/dataset/"+studentID)
                        #     except:
                        #         print("delete failed")

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
                        # conn.commit()


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
        cv2.namedWindow('checkout-face')
        cv2.setWindowProperty('checkout-face',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow('checkout-face',frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    conn.close()
    cap.release()
    cv2.destroyAllWindows()



