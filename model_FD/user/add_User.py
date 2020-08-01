import cv2
import sqlite3
import os

def getImage(name):
    cam = cv2.VideoCapture(0)
    detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cam.set(3,640)
    cam.set(4,480)

    # print("dataSet/"+name+ "/User.")
    # insertOrUpdate(id,name)
    folder="dataset/"+str(name)
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
            cv2.imwrite("dataset/"+name+ "/User" + '.' + str(sampleNum) + ".jpg", img[y:y + h, x:x + w])

        cv2.imshow('frame', img)
        # Check xem có bấm q hoặc trên 100 ảnh sample thì thoát
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        elif sampleNum>14:
            break

    cam.release()
    cv2.destroyAllWindows()