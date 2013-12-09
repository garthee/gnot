var chart_auroc = function (){
	var margin = {top: 20, right: 20, bottom: 30, left: 50},
		width = 800 - margin.left - margin.right,
		height = 400 - margin.top - margin.bottom;

	var x = d3.scale.linear().domain([0,1]).range([0, width]);
	var y = d3.scale.linear().domain([0,1]).range([height, 0]);

	var xAxis = d3.svg.axis()
    	.scale(x)
    	.orient("bottom");

	var yAxis = d3.svg.axis()
    	.scale(y)
    	.orient("left");

	var area = d3.svg.area()
    	.x(function(d) { return x(d.fpr); })
    	.y0(height)
    	.y1(function(d) { return y(d.tpr); });
    	
   	var line = d3.svg.line()
    	.x(function(d) { return x(d.fpr); })
    	.y(function(d) { return y(d.tpr); });

	var randline = d3.svg.line()
		.x(function(d) { return x(d.fpr); })
		.y(function(d) { return y(d.fpr); });

	var svg = d3.select("#svg-box-auroc").append("svg")
    	.attr("width", width + margin.left + margin.right)
    	.attr("height", height + margin.top + margin.bottom)
  		.append("g")
    	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	d3.csv(file_auroc, function(error, data) {
  		data.forEach(function(d) {
    		d.fpr = +d.fpr;
    		d.tpr = +d.tpr;
  		});

		svg.append("path")
      		.datum(data)
      		.attr("class", "area")
      		.attr("d", area)
      		.style("opacity", 0.3);

  		svg.append("path")
      		.datum(data)
      		.attr("class","line")
      		.attr("d",line);
      		
		svg.append("path")
			.datum(data)
			.attr("class","line separator")
			.style("stroke-dasharray", ("5, 3"))
			.attr("d",randline);

  		svg.append("g")
      		.attr("class", "x axis")
      		.attr("transform", "translate(0," + height + ")")
      		.call(xAxis)
      	.append("text")
      		.text("False Positive Rate")
      		.attr('dx', 600)
      		.attr('dy', -10);

  		svg.append("g")
      		.attr("class", "y axis")
      		.call(yAxis)
    	.append("text")
      		.attr("transform", "rotate(-90)")
      		.attr("y", 6)
      		.attr("dy", ".71em")
      		.style("text-anchor", "end")
      		.text("True Positive Rate");
	});
}