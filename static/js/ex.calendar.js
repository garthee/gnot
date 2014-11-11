function calendar_draw() {	
	var date = modules['calendar']['variables']['date'],
		format = d3.time.format("%Y-%m-%d"),
		mdimension = flight.dimension(function(d){
			return d[date]; 
		}),
		mgroup = mdimension.group();
	
	modules['calendar']['crossfilter']={'dimension': mdimension, 'group': mgroup};
	calendar_update();
}

function calendar_update() {
	$("#svg-box-calendar").find("svg").remove();
	
	var data = modules['calendar']['crossfilter']['group'].all();
	var data = d3.nest().key(function(d) { return d.key;})
	.rollup(function(d) {return +d[0].value;}).map(data);
	
	var width = 960, height = 136, cellSize = 17; // cell size
	
	var year = d3.time.format("%Y"), 
		day = d3.time.format("%w"), 
		week = d3.time.format("%U"),
		format = d3.time.format("%Y-%m-%d"),
		percent = d3.format(".1%");
	
	var miny = d3.min(d3.keys(data), function(d){return format.parse(d);}).getFullYear(),
		maxy = d3.max(d3.keys(data), function(d){return format.parse(d);}).getFullYear(),
		mind = +d3.min(d3.values(data)),
		maxd = +d3.max(d3.values(data));

	var svg = d3.select("#svg-box-calendar")
			.selectAll("svg")
			.data(d3.range(miny, maxy + 1))
			.enter()
			.append("svg")
			.attr("width",width)
			.attr("height", height)
			.attr("class", "PuBu").append("g")
			.attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");

	svg.append("text").attr("transform","translate(-6," + cellSize * 3.5 + ")rotate(-90)")
		.style("text-anchor", "middle")
		.text(function(d) {return d;});

	var rect = svg.selectAll(".day")
		.data(function(d) {return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1));})
		.enter()
		.append("rect")
		.attr("class", "day")
		.attr("width", cellSize)
		.attr("height", cellSize)
		.attr("x", function(d) {return week(d) * cellSize;})
		.attr("y", function(d) {return day(d) * cellSize;})
		.datum(format);

	rect.append("title").text(function(d) {
		return d;
	});

	svg.selectAll(".month")
		.data(function(d) {return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1));})
		.enter()
		.append("path")
		.attr("class", "month")
		.attr("d", monthPath);

	$('#calendar-side-container-m').html('<p>Calendar week starts on Sunday and ends on Saturday. Values range ' 
		  +'from <span class="limit-values" id="val_min">' + mind 
		  + '</span> to <span class="limit-values" id="val_max">' + maxd 
		  + '</span>.</p><p>Hover over a cell to see it\'s value.</p>'); 
	
	//var quantize = d3.scale.quantile().domain([mind, maxd]).range(d3.range(9));
	var names = d3.scale.quantize()
		.domain([ mind, maxd ])
		.range(d3.range(9).map(function(d) {return "" + d;}));

	rect.filter(function(d) {
			return d in data;
		})
		.attr("class", function(d) {
			return "day q" + names(data[d]) + "-9";
		})
		.select("title").text(function(d) {
			return d + ": " + data[d];
		});
	
	function monthPath(t0) {
		var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0), d0 = +day(t0), w0 = +week(t0), d1 = +day(t1), w1 = +week(t1);
		return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize + "H" + w0
				* cellSize + "V" + 7 * cellSize + "H" + w1 * cellSize + "V"
				+ (d1 + 1) * cellSize + "H" + (w1 + 1) * cellSize + "V" + 0
				+ "H" + (w0 + 1) * cellSize + "Z";
	}
}