import lib
import cv2
import time
import pickle
import sys
import json
import redis as Redis
import base64

redis = Redis.StrictRedis(host='localhost', port=6379, db=0)

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

def clearVideoBuffer():
    global vc
    for i in range(4):
        vc.read()

def loadPreviousCalibration():
    global xcalFrames, ycalFrames, settings, scene
    prev = pickle.load(open('last_cal.pickle'))
    settings = prev['settings']
    scene = prev['scene']

def promptForCalibration():
    global xcalFrames, ycalFrames, settings, scene
    if raw_input("Use previous calibration[no]?").lower()[:1] == "y":
        loadPreviousCalibration()
    else:
        raw_input("Press to begin xcal...")
        clearVideoBuffer()
        # Read all the frames for xcal
        xcalFrames = []
        for i in range(calFrames):
            time.sleep(frameTime)
            rval, frame = vc.read()
            xcalFrames.append(frame)
        print("xcal complete")

        raw_input("Press to begin ycal...")
        clearVideoBuffer()
        # clear buffer
        ycalFrames = []
        for i in range(calFrames):
            time.sleep(frameTime)
            rval, frame = vc.read()
            ycalFrames.append(frame)
        print("ycal complete")

        # for i,f in enumerate(xcalFrames):
        #     cv2.imwrite("x_{}.png".format(i), f)
        # for i,f in enumerate(ycalFrames):
        #     cv2.imwrite("y_{}.png".format(i), f)

        settings = lib.CalibrationSettings(
            ['x','y'],
            [0,calFrames+1],
            [calFrames-1,calFrames*2])

        scene = lib.CalibrationScene(loader, 0, settings)

        pickle.dump({
            "settings": settings,
            "scene": scene
        }, open('last_cal.pickle','w'))

promptForCalibration()
# loadPreviousCalibration()
#
print(scene.vec)
while True:
    # time.sleep(1)
    rval, frame = vc.read()
    # encoded = base64.b64encode(open("filename.png", "rb").read())
    coordinate = scene.getAxisProjection(frame)
    if coordinate is not None:
        coordinate = coordinate.tolist()
    frame_encoded = base64.encodestring(cv2.imencode('.png',frame)[1])
    redis.publish("socket-redis-down", json.dumps({
        "type": "publish",
        "data": {
            "channel":"coord",
            "event":"coord",
            "data": coordinate
        }
    }))
    redis.publish("socket-redis-down", json.dumps({
        "type": "publish",
        "data": {
            "channel":"image",
            "event":"image",
            "data": frame_encoded
        }
    }))
    # if (n % 10 == 0):
    #     cv2.imwrite("static/imgs/frame{}.png".format(n), frame)
