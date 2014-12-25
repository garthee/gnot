var chart_histogram = function (){
	var margin = {top: 20, right: 20, bottom: 80, left: 80},
		width = 800 - margin.left - margin.right,
		height = 300 - margin.top - margin.bottom;
	
	var x = d3.scale.ordinal().rangeRoundBands([0, width], .1, 1);
	var y = d3.scale.linear().range([height, 0]);
	
	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");
	
	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");
	
	var svg = d3.select("#svg-box-features").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	var l = weights_data.length;
	x.domain(weights_data.map(function(d) { return d.feature; }));
	y.domain([Math.min(0,d3.min(weights_data, function(d) { return d.weight; })), d3.max(weights_data, function(d) { return d.weight; })]);

	svg.append("g")
  		.attr("class", "x axis")
  		.attr("transform", "translate(0," + height + ")")
  		.call(xAxis)
  		.selectAll("text")
  		.style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", function(d) {return "rotate(-" + Math.min(90, 90*Math.max(l, 1)/25) +  ")" });
	
	svg.append("g")
  		.attr("class", "y axis")
  		.call(yAxis)
		.append("text")
  		.attr("transform", "rotate(-90)")
		.attr("y", 6)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		.text("Feature Weights");

	svg.selectAll(".bar")
		.data(weights_data).enter().append("rect")
		.attr("class", "bar")
		.attr("x", function(d) { return x(d.feature); })
		.attr("width", x.rangeBand())
		.attr("y", function(d) { return y(Math.max(0, d.weight)); })
		.attr("height", function(d) { return Math.abs(y(d.weight) - y(0)); });

	d3.select("input").on("change", change);
	
	var sortTimeout = setTimeout(function() {d3.select("input").property("checked", true).each(change);}, 2000);
	
	function change() {
		clearTimeout(sortTimeout);
		
		var x0 = x.domain(weights_data.sort(this.checked
		    ? function(a, b) { return b.weight - a.weight; }
		    : function(a, b) { return d3.ascending(a.feature, b.feature); })
		    .map(function(d) { return d.feature; }))
		    .copy();
		
		var transition = svg.transition().duration(750),
		    delay = function(d, i) { return i * 50; };
		
		transition.selectAll(".bar")
		    .delay(delay)
		    .attr("x", function(d) { return x0(d.feature); });
		
		transition.select(".x.axis")
			.call(xAxis)
			.selectAll("text")
		  	.style("text-anchor", "end")
			.attr("dx", "-.8em")
			.attr("dy", ".15em")
			.selectAll("g")
			.delay(delay);
	}
};