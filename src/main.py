import cv2
from cv2.typing import MatLike

import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import mouseMoveTo, mouseDown, mouseUp, movePoints, pressPoints, cursorPoint, moveDistanceTrigger, pressDistanceTrigger, monitorResolution


def workWithFrame(frame: MatLike, detectorHand, detectorFace, moveCoords: list[int], pressed: bool) -> tuple[MatLike, list[int], bool]:
    """
    :param frame: frame from camera
    :param detectorHand: hand detector
    :param detectorFace: face detector
    :param moveCoords: last move coordinates of the cursor
    :param pressed: last state of the cursor
    """
    frame = cv2.flip(frame, 1)

    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frameRGB)

    detectionsHand = detectorHand.detect(image)

    # detect hand
    if len(detectionsHand.hand_landmarks) > 0:
        detection = detectionsHand.hand_landmarks[0]

        # draw points
        for num, point in enumerate(detection):
            x = round(point.x * frame.shape[1])
            y = round(point.y * frame.shape[0])

            cv2.putText(frame, str(num), (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        # move cursor
        dist = np.sqrt((detection[movePoints[0]].x - detection[movePoints[1]].x)**2 + (detection[movePoints[0]].y - detection[movePoints[1]].y)**2)
        move = dist < moveDistanceTrigger

        updatedX = (detection[cursorPoint].x - 0.2) / 0.6 + 0.1
        updatedY = (detection[cursorPoint].y - 0.2) / 0.6 + 0.1

        screenX = round( ( updatedX ) * monitorResolution[0] )
        screenY = round( ( updatedY ) * monitorResolution[1] )

        if (abs(moveCoords[0] - screenX) > 15 and move):
            moveCoords[0] = screenX
        if (abs(moveCoords[1] - screenY) > 15 and move):
            moveCoords[1] = screenY

        mouseMoveTo(moveCoords[0], moveCoords[1])

        # press
        dist = np.sqrt((detection[pressPoints[0]].x - detection[pressPoints[1]].x)**2 + (detection[pressPoints[0]].y - detection[pressPoints[1]].y)**2)
        press = dist < pressDistanceTrigger

        if press and not pressed:
            mouseDown()
            pressed = True
        elif not press and pressed:
            mouseUp()
            pressed = False

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

    return (frame, moveCoords, pressed)


def main():
    baseOptionsHand = python.BaseOptions(model_asset_path='hand_landmarker.task')
    optionsHand = vision.HandLandmarkerOptions(base_options=baseOptionsHand, num_hands=1)
    detectorHand = vision.HandLandmarker.create_from_options(optionsHand)

    baseOptionsFace = python.BaseOptions(model_asset_path='face_detector.tflite')
    optionsFace = vision.FaceDetectorOptions(base_options=baseOptionsFace)
    detectorFace = vision.FaceDetector.create_from_options(optionsFace)

    moveCoords = [-100, -100]
    pressed = False

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print('Cannot open camera')
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frameData = workWithFrame(frame, detectorHand, detectorFace, moveCoords, pressed)

        frame = frameData[0]
        moveCoords = frameData[1]
        pressed = frameData[2]

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
    mouseUp()

