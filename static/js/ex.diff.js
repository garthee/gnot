function diff_draw(data, config) {
	$("#svg-box-diff").find("svg").remove();
	
	date = config['variables']['date'];
	lineA = config['variables']['lineA'];
	lineB = config['variables']['lineB'];
	
	var margin = {top : 20, right : 20, bottom : 30, left : 50},
		width = 960 - margin.left - margin.right,
		height = 500 - margin.top - margin.bottom;
	
	function isNumber(n) { return !isNaN(parseFloat(n)) && isFinite(n);}
	var str2int = function(d) { return +d; };
	var date2int = function(d) { d = d.split(/[- :]/); return (new Date(d[0], d[1] - 1, d[2])).getTime();};
	var time2int = function(d) {d = d.split(/[- :]/); return new Date(d[0], d[1] - 1, d[2], d[3], d[4], d[5]).getTime();};
	var month2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, 0));};
	
	var svg = d3.select("#svg-box-diff").append("svg")
			.attr("width", width + margin.left + margin.right)
			.attr("height",height + margin.top + margin.bottom)
		.append("g")
			.attr("transform","translate(" + margin.left + "," + margin.top + ")");

		// identify x axis
		var parseX = str2int;
		var XisInt = 1
		if (!isNumber(data[1][date])) {
			var lx = data[1][date].split(/[- :]/).length;
			if (lx >= 6) {
				parseX = time2int;
				XisInt = 0;
			} else if (lx >= 3) {
				parseX = date2int;
				XisInt = 0;
			}
			else if (lx >= 2){
				parseX = month2int;
				type = 3; // date
			}
		}

		if (XisInt)
			var x = d3.scale.linear().range([ 0, width ]);
		else
			var x = d3.time.scale().range([ 0, width ]);
			
		var y = d3.scale.linear().range([ height, 0 ]);
		var xAxis = d3.svg.axis().scale(x).orient("bottom");
		var yAxis = d3.svg.axis().scale(y).orient("left");

		var line = d3.svg.area().interpolate("basis")
			.x(function(d) { return x(parseX(d[date]));})
			.y(function(d) {return y(+d[lineA]);});

		var area = d3.svg.area().interpolate("basis")
			.x(function(d) {return x(parseX(d[date]));})
			.y1(function(d) {return y(+d[lineA]);});

		

		x.domain(d3.extent(data, function(d) {
			return parseX(d[date]);
		}));

		y.domain([ d3.min(data, function(d) {
			return Math.min(+d[lineA], +d[lineB]);
		}), d3.max(data, function(d) {
			return Math.max(+d[lineA], +d[lineB]);
		}) ]);

		svg.datum(data);

		svg.append("clipPath").attr("id", "clip-below").append("path").attr(
				"d", area.y0(height));

		svg.append("clipPath").attr("id", "clip-above").append("path").attr(
				"d", area.y0(0));

		svg.append("path").attr("class", "area above").attr("clip-path",
				"url(#clip-above)").attr("d", area.y0(function(d) {
			return y(+d[lineB]);
		}));

		svg.append("path").attr("class", "area below").attr("clip-path",
				"url(#clip-below)").attr("d", area);

		svg.append("path").attr("class", "line").attr("d", line);

		svg.append("g").attr("class", "x axis").attr("transform",
				"translate(0," + height + ")").call(xAxis);

		svg.append("g").attr("class", "y axis").call(yAxis).append("text")
				.attr("transform", "rotate(-90)").attr("y", 6).attr("dy",
						".71em");

		var color = function(d) {
			return (d == 'above') ? '#9ECAE1' : '#08519C';
		};

		var legend = svg.selectAll(".legend").data([ 'above', 'below' ])
				.enter().append("g").attr("class", "legend").attr("transform",
						function(d, i) {
							return "translate(0," + i * 20 + ")";
						});

		legend.append("rect").attr("x", width + 14).attr("width", 18)
			.attr("height", 18).style("fill", color);

		legend.append("text").attr("x", width + 10).attr("y", 9)
			.attr("dy",".35em").style("text-anchor", "end")
			.text(function(d) {return d;});
	}