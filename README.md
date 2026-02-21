# CurHand

#### CurHand is my humorous attempt to do mouse control through the camera.

<img src=".assets/demo.gif">

> I don't recommend using it seriously, it's just my experiment coded in one evening.

## Installation (for what?)
1) Download the contents of the `src` directory using any method.

2) Install dependencies from `requrements.txt`

3) Edit if necessary `config.py`

> By default, the configuration only works for *Linux* and only with *ydotool*, so if you are using a different system or need to manage another tool, change the functions to `config.py`.

Variables in the config:
1) `movePoints` - which 2 points on the hand should be next to each other so that the cursor starts moving
2) `moveDistanceTrigger` - how close should these 2 points be in order for the movement to begin
3) `cursorPoint` - which point will the cursor focus on
4) `pressPoints` - which 2 points on the hand should be next to each other in order for the cursor to switch to press mode
5) `pressDistanceTrigger` - how far should these 2 points be in order to switch to press mode
6) `monitorResolution` - resolution of your monitor

Functions in the config:
1) `mouseMoveTo` - your cursor movement function (in absolute coordinates)
2) `mouseDown` - a function for holding down the left mouse button
3) `mouseUp` - a function for releasing the left mouse button

## How to use
Your camera opens in front of you (your face is blurred)<br>
When you raise your hand (please, no more than one hand should be in the camera), you see parts of it labeled with numbers<br>
The action occurs if the numbers specified in the ...Points variables are close enough (...DistanceTrigger variables)

### Well, that's it, have fun 🎉

