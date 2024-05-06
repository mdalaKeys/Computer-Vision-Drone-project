import time
from djitellopy import tello
import cv2
import cvzone
from cvzone.PoseModule import PoseDetector

#def detect_corner(image):
    # Convert the image to grayscale
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Define parameters for Shi-Tomasi corner detection
    #max_corners = 100  # Maximum number of corners to detect
    #quality_level = 0.3  # Quality level threshold
    #min_distance = 7  # Minimum distance between detected corners

    # Detect corners using Shi-Tomasi algorithm
    #corners = cv2.goodFeaturesToTrack(gray, max_corners, quality_level, min_distance)

    # If corners are detected, return True
    #if corners is not None and len(corners) > 0:
    #    return True
    #else:
    #    return False


detector = PoseDetector()
#cap = cv2.VideoCapture(0)

snapTimer = 0
following = False
colorG = ( 0, 0, 255)

# _, img = cap.read()
hi,wi,_ = 480, 640, True

xPID = cvzone.PID([0.22, 0, 0.1], wi//2)
yPID = cvzone.PID([0.27, 0, 0.1], hi//2,axis=1)
zPID = cvzone.PID([0.00016, 0, 0.000011], 350000, limit=[-20,15])

myPlotX = cvzone.LivePlot(yLimit = [-100,100], char='X')
myPlotY = cvzone.LivePlot(yLimit = [-100,100], char='Y')
myPlotZ = cvzone.LivePlot(yLimit = [-100,100], char='Z')

# TelloDrone
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()
me.takeoff()
me.move_up(80)

# Set initial speed for forward movement
speed = 10

# Initialize corner count
corner_count = 0
max_corners = 3  # Maximum number of corners to detect before stopping

while True:
    # _ ,img = cap.read()
    img = me.get_frame_read().frame
    img = cv2.resize(img,(640,480))
    img = detector.findPose(img, draw = False)
    lmList, bboxInfo = detector.findPosition(img,draw=False)
    gesture = ''

    xVal = 0
    yVal = 0
    zVal = 0

    if bboxInfo:

        cx, cy = bboxInfo['center']
        x, y, w, h = bboxInfo['bbox']
        area = w * h

        xVal = int(xPID.update(cx))
        yVal = int(yPID.update(cy))
        zVal = int(zPID.update(area))

        angArmL = detector.findAngle(img, 13, 11, 23, draw=False)  # img,13,11,23
        angArmR = detector.findAngle(img, 14, 12, 24, draw=False)  # img, 14, 12, 24
        crossDistL, img, _ = detector.findDistance(15, 12, img)  # For cross
        crossDistR, img, _ = detector.findDistance(16, 11, img)

        if detector.angleCheck(angArmL, 90) and detector.angleCheck(angArmR, 270):
            gesture = 'Tracking Mode OFF'
            colorG= ( 0, 0, 255)
            following = False
        elif detector.angleCheck(angArmL, 170) and detector.angleCheck(angArmR, 180):
            gesture = 'Tracking Mode On'
            colorG = (0, 255, 0)
            following = True
        elif crossDistL:
            if crossDistL < 70 and crossDistR < 70:
                gesture = 'Cross'

                # Send command to move forward at current speed
                #me.send_rc_control(0, speed, 0, 0)

                # Perform obstacle detection (you need to implement this part)
                # Here, I assume you have a function called detect_corner() that returns True if corner detected
                #if detect_corner(img):
                   # corner_count += 1
                    # Rotate the drone when a corner is detected
                   # me.send_rc_control(0, speed, 0, -50)  # Adjust yaw as needed
                    #if corner_count >= max_corners:
                        # If maximum number of corners detected, stop the drone
                     #   speed = 0
                     #   me.send_rc_control(0, speed, 0, 0)

            #    snapTimer = time.time()


        # if snapTimer > 0 :
        #    totalTime = time.time() - snapTimer
            # print(totalTime)
        #    if totalTime < 1.9 :
        #        cv2.putText(img, "Ready", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)
        #    elif totalTime > 2 :
            #   snapTimer = 0
            #   cv2.imwrite(f'images/{time.time()},jpg',img)
            #   cv2.putText(img, "Saved", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

        else :
            cv2.putText(img, gesture, (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, colorG, 3)

        imgPlotX=myPlotX.update(xVal)
        imgPlotY = myPlotY.update(yVal)
        imgPlotZ = myPlotZ.update(zVal)

        img=xPID.draw(img,[cx,cy])
        img=yPID.draw(img, [cx, cy])

        imgStacked = cvzone.stackImages([img,imgPlotX,imgPlotY,imgPlotZ],2,0.75)
        # cv2.putText(imgStacked,str(area),(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)
    else:
        imgStacked = cvzone.stackImages([img], 1, 0.75)

    if following :
        me.send_rc_control(0,-zVal, -yVal, xVal)
    else :
        me.send_rc_control(0, 0, 0, 0)
    # tello show mini screen
    cv2.imshow("Image Stacked", imgStacked)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        me.land()
        break

cv2.destroyAllWindows()
