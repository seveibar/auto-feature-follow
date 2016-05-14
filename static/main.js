
var coordinates = [];

var apiTicks = 0;

$(window).ready(function(){
  initializeGraphs();
  requestCoordinates();
});

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
