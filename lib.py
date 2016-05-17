import sys
pyversion = None
if sys.version_info[0] < 3:
    pyversion = 2
else:
    pyversion = 3
#-------------------------------
import pylab, os
import matplotlib.pyplot as plt
import numpy as np
import cv2
#-------------------------------
def tqdm(x):
    return x
#-------------------------------
# def getCameraImagePath(camera_number, op, image_number):
#     return "/data/data/camera{}/{}/i{:05d}.jpg".format(camera_number, op, image_number)
# def getCameraImage(cam, op, im):
#     return cv2.imread(getCameraImagePath(cam, op, im))

def_cam, def_op = None, None
TD = 1 # preskipped
skip_frames = 1 #preskipped
def setCamera(cam, op):
    def_cam = cam
    def_op = op
def getCameraImage(ti):
    return video_images[ti]

def getCameraImageAt(time):
    return getCameraImage(int(time/TD))
def getCameraImagesDuring(t1, t2):
#     if (t2 - t1 > 8):
#         raise Error("Loading too many images simultaneously, may cause issues with RAM")
    if t2 < t1:
        t1, t2 = t2, t1
    for i in range(int(t1/TD), int(t2/TD), skip_frames):
        yield getCameraImage(i)
#-------------------------------
def getFeatureDetector():
    if (pyversion == 3):
        return cv2.xfeatures2d.SURF_create()
    else:
        return cv2.SURF(upright=True, hessianThreshold=300)
#-------------------------------
def getSharedKeypoints(img1, img2,sensitivity=.5):
    sift = getFeatureDetector()

    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(des1,des2,k=2)

    matchesMask = [[0,0] for i in range(len(matches))]

    pts1 = []
    pts2 = []

    for i,(m,n) in enumerate(matches):
        if m.distance < sensitivity*n.distance:
            pts2.append(np.asarray(kp2[m.trainIdx].pt))
            pts1.append(np.asarray(kp1[m.queryIdx].pt))
    pts1 = np.array(pts1)
    pts2 = np.array(pts2)
    return pts1, pts2
#-------------------------------
def getSharedDescriptors(img1, img2, sensitivity=.5):
    sift = getFeatureDetector()

    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(des1,des2,k=2)

    pts1 = []
    pts2 = []
    desi = []

    for i,(m,n) in enumerate(matches):
        if m.distance < sensitivity*n.distance:
            pts2.append(np.asarray(kp2[m.trainIdx].pt))
            pts1.append(np.asarray(kp1[m.queryIdx].pt))
            desi.append(i)

    pts1 = np.array(pts1)
    pts2 = np.array(pts2)
    desi = np.array(desi)

    # Create a mask that ignores points that haven't moved significantly
    moved = np.ones(len(pts1)).astype(int)
    for i,p1,p2 in zip(range(len(pts1)), pts1, pts2):
        if np.sum(np.abs(p1 - p2)) < 50:
            moved[i] = 0

    des_final = np.array([des1[i] for i in desi[moved==1]])
    return des_final
#-------------------------------
def findPointsWithDescriptors(img, train_des,sensitivity=.5):
    sift = getFeatureDetector()

    test_kp, test_des = sift.detectAndCompute(img,None)
#     return np.array([kp.pt for kp in test_kp])

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(train_des, test_des,k=2)

    pts1 = []
    train_des_used = np.zeros(train_des.shape[0])

    for i,(m,n) in enumerate(matches):
        if m.distance < sensitivity*n.distance:
            pts1.append(np.asarray(test_kp[m.trainIdx].pt))
            train_des_used[m.queryIdx] = 1
    pts1 = np.array(pts1)
    return pts1, train_des_used
    # Find average of points
#     return np.sum(pts1, axis=0) / pts1.shape[0]
#-------------------------------
class ImageLoader:
    def __init__(self):
        pass
    def loadAt(self, time):
        pass
    def loadSeries(self, t1, t2):
        return getCameraImagesDuring(t1, t2)

class Scene(object):
    def __init__(self, imageLoader, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.imageLoader = imageLoader
    def load(self, t1, t2):
        return self.imageLoader.loadSeries(self.start_time + t1, self.start_time + t2)

class CalibrationSettings:
    def __init__(self, axes, start_times, end_times):
        self.axes = axes
        self.start_times = start_times
        self.end_times = end_times
    def getCalibrationTime(self):
        return max(self.end_times)

class CalibrationScene(Scene):
    def __init__(self, imageLoader, start, settings):
        super(CalibrationScene, self).__init__(imageLoader, start, start + settings.getCalibrationTime())
        self.settings = settings
        self.calculateAxisDescriptors()

    def calculateAxisDescriptors(self):
        self.descriptors = []
        self.start = []
        self.vec = []
        self.vec_length = []
        self.sensitivites = []
        for ai in range(len(self.settings.axes)):
            imgs = list(self.load(
                self.settings.start_times[ai],
                self.settings.end_times[ai]))
            print(self.settings.start_times[ai], self.settings.end_times[ai])
            sensitivity = .5
            # cv2.imwrite("a{}_1.png".format(ai), imgs[0])
            # cv2.imwrite("a{}_2.png".format(ai), imgs[-1])
            descriptors = getSharedDescriptors(imgs[0], imgs[-1], sensitivity=sensitivity)
            # make sure there are enough descriptors
            while len(descriptors) < 20:
                sensitivity += .02
                descriptors = getSharedDescriptors(imgs[0], imgs[-1], sensitivity=sensitivity)

            des_used = np.zeros(descriptors.shape[0])
            for img in tqdm(imgs):
                pts, fdes = findPointsWithDescriptors(img, descriptors, sensitivity=sensitivity)
                des_used += fdes
            # Only use descriptors that are in atleast 25% of the calibration images
            better_descriptors = descriptors[des_used >= len(imgs)*.25]
            self.descriptors.append(better_descriptors)
            start, fdes = findPointsWithDescriptors(imgs[0], better_descriptors, sensitivity=sensitivity)
            end, fdes2 = findPointsWithDescriptors(imgs[-1], better_descriptors, sensitivity=sensitivity)
            self.sensitivites.append(sensitivity)
            self.start.append(start)
            vec = np.average(end - start, axis=0)
            self.vec_length.append(np.linalg.norm(vec))
            vec = vec / np.linalg.norm(vec)
            self.vec.append(vec)
        self.sensitivites = np.array(self.sensitivites)

    def getAxisProjection(self, img):
        projections = []
        for i, (descriptors, start, sensitivity) in enumerate(zip(self.descriptors, self.start, self.sensitivites)):
            pts, fdes = findPointsWithDescriptors(img, descriptors, sensitivity=sensitivity)
            if len(pts) == 0:
                return None
            offset =np.average(pts - start[fdes == 1], axis=0)
            projections.append(np.dot(self.vec[i], offset) / self.vec_length[i])
        return np.array(projections)

    def getFeaturesFromAxisProject(self, img):
        points = []
        for i, (descriptors, start, sensitivity) in enumerate(zip(self.descriptors, self.start, self.sensitivites)):
            pts, fdes = findPointsWithDescriptors(img, descriptors, sensitivity=sensitivity)
            points.append(pts)
        return np.array(points)

    def getAxisImages(self, axis):
        ai = self.settings.axes.index(axis)
        return self.load(
            self.settings.start_times[ai],
            self.settings.end_times[ai])

    def getAxisProjectionSeries(self, start, end):
        imgs = getCameraImagesDuring(self.cam, self.op, start, end)
        return [self.getAxisProjection(img) for img in tqdm(imgs)]
