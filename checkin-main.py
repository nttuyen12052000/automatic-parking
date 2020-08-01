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
from model_FD.new_user.train import train


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
    conn = sqlite3.connect("DB/mydb.db")

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

                    # cv2.putText(frame,str_lp,(50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), lineType=cv2.LINE_AA)
                    # cv2.imshow("Reult",img)
                    # print("Co bang so roi lam cai khac di")
        #Neu bien so chua dang ki thi khong can kiem tra khuon mat            
        if use_face_detect == 1:
            finish_detect = 1      


        if have_lp == 1 and lp_Registered == 1 and have_name == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.putText(frame,"Vui long bo khau trang ra!!",(50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),3, lineType=cv2.LINE_AA)
            #Lay ra cac phan cho la khuon mat
            rects = detector.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)

            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            if boxes:
                print((boxes[0][2] - boxes[0][0])/frame.shape[0])
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
                cv2.putText(frame,check_in,(50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),3, lineType=cv2.LINE_AA)
                if time.time()-start_time > 5:
                    # print("Moi ban di qua")

                    #Lay thoi gian hien tai
                    now = datetime.now()

                    #convert thoi gian
                    fm_time = now.strftime("%H:%M:%S %d/%m/%Y")
                    status = 'IN'
                    ins = "INSERT INTO time_IO(studentID,LincensePlate,time,status,newUser) VALUES('"+name+"','"+str_lp+"','"+fm_time+"','"+status+"',0)"
                    print("Insert succesfully!!")
                    print(ins)

                    #Ghi vao database
                    # conn.execute(ins)
                    # conn.commit()

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
                    cv2.putText(frame,add_user,(50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),2, lineType=cv2.LINE_AA)
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
                    if skip_frame%15==0:
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            sampleNum = sampleNum + 1
                            cv2.imwrite(folder+ "/"+name + '.' + str(sampleNum) + ".jpg", img[y:y + h, x:x + w])
                            if sampleNum == 4:
                                cv2.imwrite("Storage/Check-in/"+str(id) + ".jpg", img[y:y + h, x:x + w])
                else:
                    cv2.putText(frame,add_user,(50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255),2, lineType=cv2.LINE_AA)
                    if training == 1:
                        add_user = "Moi ban di qua!"
                        train()
                        trained = 1
                        training = 0
                        print("Trained")
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
                        ins = "INSERT INTO time_IO(studentID,LincensePlate,time,status,newUser) VALUES('"+name+"','"+str_lp+"','"+fm_time+"','"+status+"',1)"
                        print(ins)
                        print("Insert succesfully!!")

                        #Ghi vao database
                        # conn.execute(ins)
                        # conn.commit()
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
        
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    conn.close()
    cap.release()
    cv2.destroyAllWindows()



