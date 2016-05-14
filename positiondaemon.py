import lib
import cv2
import time
import pickle
import sys
import tracker


vc = cv2.VideoCapture(1)

frameTime = .25
calTime = 10
calFrames = int(calTime / frameTime)

xcalFrames, ycalFrames = None, None
settings, scene = None, None

class CamImageLoader:
    def loadSeries(self, t1,t2):
        if t1 < calFrames:
            for i in range(t1,t2):
                yield xcalFrames[i]
        else:
            for i in range(t1-calFrames,t2-calFrames):
                yield ycalFrames[i]

loader = CamImageLoader()

def loadPreviousCalibration():
    global xcalFrames, ycalFrames, settings, scene
    prev = pickle.load(open('last_cal.pickle'))
    xcalFrames = prev['xcal']
    ycalFrames = prev['ycal']
    settings = prev['settings']
    scene = prev['scene']

def promptForCalibration():
    global xcalFrames, ycalFrames, settings, scene
    if raw_input("Use previous calibration[no]?").lower()[:1] == "y":
        loadPreviousCalibration()
    else:
        raw_input("Press to begin xcal...")
        # Read all the frames for xcal
        xcalFrames = []
        for i in range(calFrames):
            time.sleep(frameTime)
            rval, frame = vc.read()
            xcalFrames.append(frame)
        print("xcal complete")

        raw_input("Press to begin ycal...")
        ycalFrames = []
        for i in range(calFrames):
            time.sleep(frameTime)
            rval, frame = vc.read()
            ycalFrames.append(frame)
        print("ycal complete")

        settings = lib.CalibrationSettings(
            ['x','y'],
            [0,calFrames],
            [calFrames-1,calFrames*2])

        scene = lib.CalibrationScene(loader, 0, settings)

        pickle.dump({
            "xcal": xcalFrames,
            "ycal": ycalFrames,
            "settings": settings,
            "scene": scene
        }, open('last_cal.pickle','w'))

promptForCalibration()
# loadPreviousCalibration()
#
while True:
    # time.sleep(1)
    rval, frame = vc.read()
    coordinate = scene.getAxisProjection(frame)
    if coordinate is not None:
        # n = tracker.addCoordinate.delay(coordinate.tolist()).get()
        tracker.addCoordinate.delay(coordinate.tolist())
    else:
        tracker.addCoordinate.delay(None)
    # if (n % 10 == 0):
    #     cv2.imwrite("static/imgs/frame{}.png".format(n), frame)
