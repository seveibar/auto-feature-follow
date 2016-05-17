
var coordinates = [];

var apiTicks = 0;

$(window).ready(function(){
  initializeGraphs();
  initializeCanvas();
  // requestCoordinates();
  startRedis();
});

var canvas, context;
function initializeCanvas(){
  canvas = $("#can")[0];
  context = canvas.getContext('2d');
  context.fillStyle = "#000";
  context.strokeStyle = "#fff";
  context.lineWidth = 5;
  clearCanvas();
}

function clearCanvas(){
  context.fillRect(0,0,400,400);
}

var c_minx = 0, c_maxx = 1, c_miny = 0, c_maxy = 1;
function updateCanvas(){
  clearCanvas();
  var last20 = coordinates.slice(coordinates.length - 50, coordinates.length);
  // var last20 = coordinates;
  var l2_x = last20.map(function(c){ return c[0]; });
  var l2_y = last20.map(function(c){ return c[1]; });
  c_minx = Math.min(c_minx, Math.min.apply(this,l2_x));
  c_maxx = Math.max(c_maxx, Math.max.apply(this,l2_x));
  c_miny = Math.min(c_miny, Math.min.apply(this,l2_y));
  c_maxy = Math.max(c_maxy, Math.max.apply(this,l2_y));

  for (var i = 1;i < last20.length;i++){
    var x1 = (last20[i-1][0] - c_minx) / (c_maxx-c_minx) * 350 + 25,
        y1 = (last20[i-1][1] - c_miny) / (c_maxy-c_miny) * 350 + 25,
        x2 = (last20[i][0] - c_minx) / (c_maxx-c_minx) * 350 + 25,
        y2 = (last20[i][1] - c_miny) / (c_maxy-c_miny) * 350 + 25;
    context.globalAlpha = i / last20.length;
    context.beginPath();
    context.moveTo(x1,y1);
    context.lineTo(x2,y2);
    context.closePath();
    context.stroke();
  }
  context.globalAlpha = 1;
}

function calculateVelocity(){
  var x1 = coordinates[coordinates.length-1][0],
      y1 = coordinates[coordinates.length-1][1],
      x2 = coordinates[coordinates.length-2][0],
      y2 = coordinates[coordinates.length-2][1];
  return Math.sqrt(Math.pow(x1-x2,2) + Math.pow(y1-y2,2));
}

var avgVelocity = 0;
function calculateAverageVelocity(){
  avgVelocity = avgVelocity * .9 + calculateVelocity() * .1;
  return avgVelocity;
}

function updateStats(){
  $("#xpos").text("X: " + (coordinates[coordinates.length-1][0]*100).toFixed(3));
  $("#ypos").text("Y: " + (coordinates[coordinates.length-1][1]*100).toFixed(3));
  $("#speed").text("Velocity: " + (calculateVelocity()*100).toFixed(3));
  $("#avgspeed").text("Average Velocity: " + (calculateAverageVelocity()*100).toFixed(3));
}

function updateXML(){
  $("#xml").val(
    (
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
    "<?xml-stylesheet type=\"text/xsl\" href=\"/styles/Streams.xsl\"?>\n" +
    "<MTConnectStreams xmlns:m=\"urn:mtconnect.org:MTConnectStreams:1.3\" xmlns=\"urn:mtconnect.org:MTConnectStreams:1.3\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"./schema.xml\">\n" +
    "<Header creationTime=\"{TIME}\" sender=\"mtcagent\" instanceId=\"0\" version=\"1.3.0.9\" nextSequence=\"{SEQ}\" firstSequence=\"0\" lastSequence=\"{SEQ}\"/>\n" +
    "<Streams>\n" +
    "    <DeviceStream name=\"VMC-3Axis\" uuid=\"000\">\n" +
    "      <ComponentStream component=\"Linear\" name=\"X\" componentId=\"x1\">\n" +
    "      <Samples>\n" +
    "        <Position dataItemId=\"x1\" timestamp=\"{TIMESTAMP}\" name=\"xPos\" sequence=\"{SEQ}\" subType=\"ACTUAL\">{X}</Position>\n" +
    "        <Position dataItemId=\"y1\" timestamp=\"{TIMESTAMP}\" name=\"yPos\" sequence=\"{SEQ}\" subType=\"ACTUAL\">{Y}</Position>\n" +
    "      </Samples>\n" +
    "    </DeviceStream>\n" +
    "</Streams>\n" +
    "</MTConnectStreams>"
  )
  .replace(/\{TIME\}/g, (new Date()).getTime())
  .replace(/\{X\}/g, coordinates[coordinates.length-1][0])
  .replace(/\{Y\}/g, coordinates[coordinates.length-1][1])
  .replace(/\{SEQ\}/g, coordinates.length)
  );
}

function startRedis(){
  var socketRedis = new SocketRedis('http://127.0.0.1:8090');
  socketRedis.onopen = function() {
    console.log("Connected to Redis");
    socketRedis.subscribe('coord', null, {foo: 'bar'}, function(event, data) {
      if (!data){
        data = coordinates[coordinates.length - 1]
      }
      coordinates.push(data);
      plot1.addPoint(data[0]);
      plot2.addPoint(data[1]);
      updateCanvas();
      updateXML();
      updateStats();
    });
    socketRedis.subscribe('image', null, {foo: 'bar'}, function(event, data) {
      $("#liveview").attr("src", "data:image/png;base64," + data);
    });
  };
}

function requestCoordinates(){
  apiTicks ++;
  $.getJSON("/coordinates", {
    "start": coordinates.length,
    "end": -1
  }, function(res){
    console.log(res);
    for (var i = 0;i < res.coordinates.length;i ++){
      coordinates.push(res.coordinates[i]);
      plot1.addPoint(res.coordinates[i][0]);
      plot2.addPoint(res.coordinates[i][1]);
    }
    // if (apiTicks % 10 == 0){
    //   var imgPath = "/imgs/frame" + Math.floor(coordinates.length/10) * 10 + ".png";
    //   $("#liveview").attr("src", imgPath);
    // }
    setTimeout(function(){
      requestCoordinates();
    }, 100);
  })
}

var plot1, plot2;

function initializeGraphs(){
  plot1 = Graph({
    elm: "#plot1"
  });
  plot2 = Graph({
    elm: "#plot2"
  });
}
