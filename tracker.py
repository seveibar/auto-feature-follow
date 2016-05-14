from celery import Celery

app = Celery('add',
    backend='redis://localhost',
    broker='redis://localhost',
    serializer='json')

coordinates = []
recording = []

@app.task
def setRecording(fr,to):
    recording = [fr,to]

@app.task
def numCoordinates():
    return len(coordinates)

@app.task
def addCoordinate(positions):
    if positions is None:
        addSmoothedCoordinate(coordinates[-1])
    else:
        addSmoothedCoordinate(positions)
    return len(coordinates)

def addSmoothedCoordinate(coordinate, k=8):
    xavg = sum([c[0] for c in coordinates[-k:]] + [coordinate[0]]) / (k+1)
    yavg = sum([c[1] for c in coordinates[-k:]] + [coordinate[1]]) / (k+1)
    coordinates.append([xavg, yavg])

@app.task
def getCoordinates(fr, to):
    return coordinates[fr:to]
