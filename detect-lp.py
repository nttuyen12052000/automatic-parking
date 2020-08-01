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
        # print(ratio)
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
                    else:
                        print("Bien so chua dang ki")
                        use_face_detect = 1
                    #reset variable
                    # list.clear()
                    values = ""
                    xacsuat = 0
                    have_lp = 1 #Co bang so
        if have_lp == 1:
            str_lp = ""
            have_lp=0
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    conn.close()
    cap.release()
    cv2.destroyAllWindows()
