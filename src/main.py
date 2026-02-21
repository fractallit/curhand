import cv2
from cv2.typing import MatLike

import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import mouseSetPoint, mouseDown, mouseUp, movePoints, pressPoints, cursorPoint, moveDistanceTrigger, pressDistanceTrigger, monitorResolution, drawPointsNums


def smoothMove(old_x: int, old_y, new_x: int, new_y: int) -> tuple[int, int]:
    target_x = round( (old_x + (old_x + new_x) / 2) / 2 );
    target_y = round( (old_y + (old_y + new_y) / 2) / 2 );

    mouseSetPoint(target_x, target_y)

    return target_x, target_y


def update(frame: MatLike, detectorHand, detectorFace, pressed: bool, old_x: int, old_y: int) -> tuple[MatLike, bool, int, int]:
    """
    :param frame: frame from camera
    :param detectorHand: hand detector
    :param detectorFace: face detector
    :param pressed: last state of the cursor
    """
    frame = cv2.flip(frame, 1)

    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frameRGB)

    detectionsHand = detectorHand.detect(image)

    new_x, new_y = old_x, old_y

    # detect hand
    if len(detectionsHand.hand_landmarks) > 0:
        detection = detectionsHand.hand_landmarks[0]

        # draw points nums
        if drawPointsNums:
            for num, point in enumerate(detection):
                x = round(point.x * frame.shape[1])
                y = round(point.y * frame.shape[0])

                cv2.putText(frame, str(num), (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        # move cursor
        dist = np.sqrt((detection[movePoints[0]].x - detection[movePoints[1]].x)**2 + (detection[movePoints[0]].y - detection[movePoints[1]].y)**2)
        move = dist < moveDistanceTrigger

        normalizedX = (detection[cursorPoint].x - 0.2) / 0.6 + 0.1
        normalizedY = (detection[cursorPoint].y - 0.3) / 0.4 + 0.1

        screenX = round( ( normalizedX ) * monitorResolution[0] )
        screenY = round( ( normalizedY ) * monitorResolution[1] )

        if (move):
            new_x, new_y = smoothMove(old_x, old_y, screenX, screenY)

        # press
        dist = np.sqrt((detection[pressPoints[0]].x - detection[pressPoints[1]].x)**2 + (detection[pressPoints[0]].y - detection[pressPoints[1]].y)**2)
        press = dist < pressDistanceTrigger

        if press and not pressed:
            mouseDown()
            pressed = True
        elif not press and pressed:
            mouseUp()
            pressed = False

        # draw points

        # cursor point
        cursorPointXOnCamera = round(detection[cursorPoint].x * frame.shape[1])
        cursorPointYOnCamera = round(detection[cursorPoint].y * frame.shape[0])

        cv2.circle(frame, (cursorPointXOnCamera, cursorPointYOnCamera), 7, (0, 255, 255), -1)

        # move points
        movePoint1XOnCamera = round(detection[movePoints[0]].x * frame.shape[1])
        movePoint1YOnCamera = round(detection[movePoints[0]].y * frame.shape[0])
        movePoint2XOnCamera = round(detection[movePoints[1]].x * frame.shape[1])
        movePoint2YOnCamera = round(detection[movePoints[1]].y * frame.shape[0])

        moveColor = (0, 255, 0) if move else (0, 0, 255)

        cv2.circle(frame, (movePoint1XOnCamera, movePoint1YOnCamera), round(moveDistanceTrigger/1.5*frame.shape[0]), moveColor, -1)
        cv2.circle(frame, (movePoint2XOnCamera, movePoint2YOnCamera), round(moveDistanceTrigger/1.5*frame.shape[0]), moveColor, -1)

        # press points
        pressPoint1XOnCamera = round(detection[pressPoints[0]].x * frame.shape[1])
        pressPoint1YOnCamera = round(detection[pressPoints[0]].y * frame.shape[0])
        pressPoint2XOnCamera = round(detection[pressPoints[1]].x * frame.shape[1])
        pressPoint2YOnCamera = round(detection[pressPoints[1]].y * frame.shape[0])

        pressColor = (0, 255, 0) if press else (0, 0, 255)

        cv2.circle(frame, (pressPoint1XOnCamera, pressPoint1YOnCamera), round(pressDistanceTrigger/1.5*frame.shape[0]), pressColor, -1)
        cv2.circle(frame, (pressPoint2XOnCamera, pressPoint2YOnCamera), round(pressDistanceTrigger/1.5*frame.shape[0]), pressColor, -1)

        # draw lines

        # move line
        cv2.line(frame, (movePoint1XOnCamera, movePoint1YOnCamera), (movePoint2XOnCamera, movePoint2YOnCamera), (50, 50, 50), 5)

        # press line
        cv2.line(frame, (pressPoint1XOnCamera, pressPoint1YOnCamera), (pressPoint2XOnCamera, pressPoint2YOnCamera), (50, 50, 50), 5)

    # detect face
    detectionsFace = detectorFace.detect(image)

    if len(detectionsFace.detections) > 0:
        face = detectionsFace.detections[0]

        bounding_box = face.bounding_box

        x = np.clip(bounding_box.origin_x - 20, 0, bounding_box.origin_x)
        y = np.clip(bounding_box.origin_y - 20, 0, bounding_box.origin_y)
        width = bounding_box.width + 40
        height = bounding_box.height + 40

        roi = frame[y:y+height, x:x+width]
        blurredRoi = cv2.GaussianBlur(roi, (41, 41), 30)

        frame[y:y+height, x:x+width] = blurredRoi

    return frame, pressed, new_x, new_y


def main():
    baseOptionsHand = python.BaseOptions(model_asset_path='hand_landmarker.task')
    optionsHand = vision.HandLandmarkerOptions(base_options=baseOptionsHand, num_hands=1)
    detectorHand = vision.HandLandmarker.create_from_options(optionsHand)

    baseOptionsFace = python.BaseOptions(model_asset_path='face_detector.tflite')
    optionsFace = vision.FaceDetectorOptions(base_options=baseOptionsFace)
    detectorFace = vision.FaceDetector.create_from_options(optionsFace)

    pressed = False

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print('Cannot open camera')
        return

    old_x, old_y = 0, 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frameData = update(frame, detectorHand, detectorFace, pressed, old_x, old_y)

        frame = frameData[0]
        pressed = frameData[1]
        old_x, old_y = frameData[2], frameData[3]

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
    mouseUp()

