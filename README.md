# Auto Feature Follow

Auto Feature Follow provides an HTTP endpoint, calibration method and real time
streaming to a website for automatic feature detection and tracking. This can be
used to detect progress and throughput on machinery, or simply to log an
arbitrary number of axes viewed from a webcam over time.

The application currently has two stages. In the first stage, the X and Y axes
are calibrated (this happens in `positiondaemon.py`). After the calibration images
are taken, they are processed to generate the best descriptors for getting
feature positions. A matrix transform is then created to transform the vectors
the features move against to a cartesian coordinate space. Finally the program
enters an infinite loop of taking images from the web cam and transforming the
features into coordinate space. All the data can be visualized at
`http://127.0.0.1:5000`.

## Capabilities

* Any number of axes
* Linear Feature Movement
* Realtime video output to browser
* Velocity calculation (relative to calibrated area)
* Robust feature pruning
* Client/browser-side MTConnect XML output

## Usage

Assuming you have all the requirements in [running](#running). Simply run the
`./run.sh` file to start the server.

## Library Usage

The `lib.py` file can be used independently of the server for more complex
feature following tasks.

```python
import lib

# Grab some images using cv2.VideoCapture, pull from server etc.
# images = [<image1>, <image2>, <image3>, ...]

class CamImageLoader:
    def loadSeries(self, t1,t2):
      return images[t1:t2]

settings = lib.CalibrationSettings(
        ['x','y'],
        [0,calFrames+1],
        [calFrames-1,calFrames*2])

loader = CamImageLoader()

scene = lib.CalibrationScene(loader, 0, settings)

newCoordinateProjection = scene.getAxisProjection(newFrame)
```

## Running

This project requires the following libraries/services to be installed.
* Redis Server (`redis-server` or an active service)
* `socket-redis` install using `npm install -g socket-redis`
* Python2.7
* Flask
* OpenCV 2 (recommended 2.4.2)

## TODOs

* Non-linear (radial or heterogenous) feature movement
* Built-in throughput/progress display
* Server-side MTConnect XML output
* Server-side JSON XML output
* Session playback (for testing)
* Automated test suite for parameter optimization
* More extensive library documentation
* Full electron application for deployment
