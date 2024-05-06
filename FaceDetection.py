from djitellopy import tello
import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector

detector = FaceDetector(minDetectionCon=0.5)

cap =cv2.VideoCapture(0)
hi,wi,_ = 480, 640, True

xPID = cvzone.PID([0.22, 0, 0.1], wi//2)
yPID = cvzone.PID([0.3, 0, 0.1], hi//2,axis=1)
zPID = cvzone.PID([0.005, 0, 0.003], 12000,limit=[-20,15])

myPlotX = cvzone.LivePlot(yLimit = [-100,100], char='X')
myPlotY = cvzone.LivePlot(yLimit = [-100,100], char='Y')
myPlotZ = cvzone.LivePlot(yLimit = [-100,100], char='Z')

# TelloDrone
# me = tello.Tello()
# me.connect()
# print(me.get_battery())
# me.streamoff()
# me.streamon()
# me.move_up(80)

while True:
    _ ,img = cap.read()
    #img = me.get_frame_read().frame #Tello
    img, bboxs = detector.findFaces(img, draw=True)

    xVal = 0
    yVal = 0
    zVal = 0

    if bboxs :
        cx,cy = bboxs[0]['center']
        x,y,w,h = bboxs[0]['bbox']
        area = w * h


        xVal = int(xPID.update(cx))
        yVal = int(yPID.update(cy))
        zVal = int(zPID.update(area))
        print(zVal)

        imgPlotX=myPlotX.update(xVal)
        imgPlotY = myPlotY.update(yVal)
        imgPlotZ = myPlotZ.update(zVal)

        img=xPID.draw(img,[cx,cy])
        img=yPID.draw(img, [cx, cy])

        imgStacked = cvzone.stackImages([img,imgPlotX,imgPlotY,imgPlotZ],2,0.75)
        cv2.putText(imgStacked,str(area),(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)
    else:
        imgStacked = cvzone.stackImages([img], 1, 0.75)

    # me.send_rc_control(0,-zVal, -yVal, xVal)

    cv2.imshow("Image Stacked", imgStacked)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
