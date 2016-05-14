function getTime(){ return new Date().getTime(); }

function Graph(params){
  if (!params) params = {};
  params.width = params.width || 400;
  params.height = params.height || 400;
  params.elm = params.elm || "body";


  // Number of points to display, start with random data
  var n = 40,
      data = d3.range(n).map(function(){return 0;});

  // Graph margins
  var margin = {top: 20, right: 20, bottom: 20, left: 40},
      width = params.width - margin.left - margin.right,
      height = params.height - margin.top - margin.bottom;

  // Set X and Y domain/range
  var x = d3.scale.linear()
      .domain([0, n - 1])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([-1, 1])
      .range([height, 0]);

  // Create line for using the data
  var line = d3.svg.line()
      .x(function(d, i) { return x(i); })
      .y(function(d, i) { return y(d); });

  // Create SVG to store graph
  var svg = d3.select(params.elm).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Set clip mask
  svg.append("defs").append("clipPath")
      .attr("id", "clip")
    .append("rect")
      .attr("width", width)
      .attr("height", height);

  // Create x axis
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + y(0) + ")")
      .call(d3.svg.axis().scale(x).orient("bottom"));

  // Create y axis
  svg.append("g")
      .attr("class", "y axis")
      .call(d3.svg.axis().scale(y).orient("left"));

  // Apply clip path to lines
  var path = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", line);

  // Update graph with current data
  function updateGraph(){
    if (queuedData.length > 0){
      data.push(queuedData[0]);
      queuedData.shift();
      data.shift();
    }
    var speed = .1 + queuedData.length/5;
    path
        .attr("d", line)
        .attr("transform", null)
      .transition()
        .duration(500 / speed)
        .ease("linear")
        .attr("transform", "translate(" + x(-1) + ",0)")
        .each('end', updateGraph);
  }

  var queuedData = [];

  function addPoint(point){
    y.domain([
      Math.min(y.domain()[0], point),
      Math.max(y.domain()[1], point)
    ]);
    queuedData.push(point);
    if (queuedData.length > n){
      queuedData.shift();
    }
  }

  updateGraph();

  return {
    addPoint: addPoint
  };

}
