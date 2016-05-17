from flask import Flask, request, send_from_directory, url_for,jsonify
from random import random
import threading
import time
import tracker
import json

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/sample')
def sample():
    #TODO server-side sampling
    return """

    """

@app.route('/coordinates')
def getWebcam():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    return json.dumps(
    {
        'start': start,
        'end': end,
        'coordinates': tracker.getCoordinates.delay(start,end).get(timeout=1)
    }
    )

if __name__ == "__main__":
    app.run(debug=True)
