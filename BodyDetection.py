from cvzone.PoseModule import PoseDetector
import cv2

detector = PoseDetector()
cap =cv2.VideoCapture(0)

while True:
    _, img = cap.read()

    img = detector.findPose(img,draw=True)
    lmList, bboxInfo = detector.findPosition(img,draw=True)
    gesture = ''

    if bboxInfo :
        angArmL = detector.findAngle(img,13,11,23, draw=True) # img,13,11,23
        angArmR = detector.findAngle(img, 14, 12, 24, draw=True) # img, 14, 12, 24
        crossDistL, img, _= detector.findDistance(15,12,img) # For cross
        crossDistR, img, _ = detector.findDistance(16, 11, img)

        if detector.angleCheck(angArmL, 90) and detector.angleCheck(angArmR, 270):
            gesture = 'T pose'
        elif detector.angleCheck(angArmL, 170) and detector.angleCheck(angArmR, 180):
            gesture = 'Up'
        elif crossDistL:
            if crossDistL < 70 and crossDistR < 70:
                gesture = 'Cross'


        cv2.putText(img,gesture,(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)

    cv2.imshow("Image",img)
    cv2.waitKey(1)