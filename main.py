import cv2
import pickle
#import cvzone
import numpy as np
import threading
import time
import pyrebase

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.8
color = (255, 255, 255)
thickness = 1

firebaseConfig = {
  "apiKey": "AIzaSyCabVM2KN-lnk1ajd3aFQt4r3l2p3AMNzU",
  "authDomain": "iot-parking-system-c9d2a.firebaseapp.com",
  "databaseURL": "https://iot-parking-system-c9d2a-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "iot-parking-system-c9d2a",
  "databaseURL": "https://iot-parking-system-c9d2a-default-rtdb.europe-west1.firebasedatabase.app/",
  "storageBucket": "iot-parking-system-c9d2a.appspot.com",
  "messagingSenderId": "105076954508",
  "appId": "1:105076954508:web:34ff3e219a97cefe04f2a9",
  "measurementId": "G-LT0J0WKTWT"
}



firebase = pyrebase.initialize_app(firebaseConfig)
    # Authenticate user
auth = firebase.auth()
email = "abualrobhussam1@gmail.com"
password = "7iskodisco123"
user = auth.sign_in_with_email_and_password(email, password)


database = firebase.database()

collection = 'Adab'

# Video feed
cap = cv2.VideoCapture('output8-cut.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

#get the size of the list the holds the x,y values of each parking space
# the index in the list represents the place of the parking spot    
list_size = len(posList)

#false meaning occupied while true means that it is available
boolean_list = []


# Get a reference to the collection
collection_ref = database.child(collection)
# Remove all data in the collection
collection_ref.remove()

#initialize the boolean_list to the corrisponding index of the position list and set all of them to None
for index, spot in enumerate(posList):
    boolean_list.append({"index": index, "state": False})
    database.child(collection).child(index).set({"index":index,"state": False})
#json_data = json.dumps(boolean_list)

#width, height = 90, 120
def update_firebase():
    #time.sleep(10)
    while True:
        for index, spot in enumerate(boolean_list):
            database.child(collection).child(index).update({"state":boolean_list[index]["state"]})
        print("firebase updated\n")
        time.sleep(2)

firebase_thread = threading.Thread(target=update_firebase)
firebase_thread.daemon = True
firebase_thread.start()



def checkParkingSpace(imgPro):
    spaceCounter = 0#initilizes a counter for the number of free parking spaces

    for index, pos in enumerate(posList):#iterates over each parking space
        x, y, w1, h1 = pos#extracts the x and y coordinates of the top-left corner of the parking space

        imgCrop = imgPro[y:y + h1, x:x + w1]#crops the input image to the size of the parking space
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)#counts the number of non-zero (white) pixels in the cropped image

        #less than 900 meaning it is empty spot
        if count < 1600:# Checks if the count of non-zero pixels is less than a certain threshold (900 in this case).
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            #boolean_list.append({"index": index, "state": True})
            boolean_list[index]["state"] = False
            #database.child("data").child(index)
            #database.child("data").child(index).update({"state":True})
        else:
            color = (0, 0, 255)
            thickness = 2
            #boolean_list.append({"index": index, "state": False})
            boolean_list[index]["state"] = True
            #database.child("data").child(index).update({"state":False})

        cv2.rectangle(img, (pos[0], pos[1]), (pos[0] + w1, pos[1] + h1), color, thickness)
        # Calculate the position to place the number text
        text_pos = (pos[0] + 10, pos[1] + h1 - 10)  # Adjust the position as needed

        # Draw the number attribute on the image
        string = str(index) +" "+ str(count)
        cv2.putText(img, str(string), text_pos, font, font_scale, color, thickness)
        
        # cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
        #                    thickness=2, offset=0, colorR=color)

        # cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
        #                    thickness=5, offset=20, colorR=(0,200,0))
    

while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#converts the frame to grayscale using cv2.cvtColor()
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)#to reduce noise and smooth the image
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 41, 16)#it applies adaptive thresholding  to segment the image into foreground and background pixels
    imgMedian = cv2.medianBlur(imgThreshold, 5)# further remove noise.
    kernel = np.ones((3, 3), np.uint8)#
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)# fill in small gaps and connect nearby edges.

    checkParkingSpace(imgDilate)

    cv2.imshow("Image", img)
    cv2.imshow("ImageGray", imgGray)
    cv2.imshow("ImageBlur", imgBlur)
    cv2.imshow("ImageThreshold", imgThreshold)
    cv2.imshow("ImageMedian", imgMedian)
    cv2.imshow("ImageDilate", imgDilate)


    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    cv2.waitKey(10)
