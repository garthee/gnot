var chart_scatter_crossfilter = function (drawLine){
	//scatter plot
	var shapes = ['circle', 'square','diamond', 'cross', 'triangle-down', 'triangle-up'],
	 		margin = {top: 40, right: 20, bottom: 50, left: 90},
		    width = 800,
		    height = 400,
		    scatterchart;
	
	if (drawLine)
		scatterchart = nv.models.scatterPlusLineChart();
	else
		scatterchart = nv.models.scatterChart();
	
	scatterchart.showDistX(true)
 		.showDistY(true)
		.width(width)
		.height(height)
		.margin(margin)
		.color(d3.scale.category10().range());
 	
 	scatterchart.scatter.onlyCircles(false);
   	scatterchart.tooltipContent(function(key, xVal, yVal, e, chart) {
   		return '<h3>' + key + '</h3>';
   	});
	scatterchart.dispatch.on('stateChange', function(e) { ('New State:', JSON.stringify(e)); });
	nv.utils.windowResize(scatterchart.update);

	d3.text(file_provenance, function(text) {
		var data = d3.csv.parseRows(text),
			header = data[0],
			charts = [];
		data = data.slice(1,data.length);
		
		var flight = crossfilter(data),
	  		all = flight.groupAll(),
	  		flightId = flight.dimension(function(d){return d[0];}),
  			flightIds = flightId.group();
		
		function scatter_plot() {
			// 0:id,1:prediction result (grouping),2:actual label(shape),3:error,4:y,or features
			
			var	idsarray = flightIds.all(),
				scatter_data = {};
				
			var x1 = 0, x2 = 0, intercept = 0, slope = 0;
			if (drawLine){
				weights_data.forEach(function (d) { if(d.feature == scatter_x2_name) x2 = d.weight;});
				weights_data.forEach(function (d) { if(d.feature == scatter_x1_name) x1 = d.weight;});
				weights_data.forEach(function (d) { if(d.feature == 'intercept') intercept = d.weight;});
				
				intercept = -1.0*intercept/x2;
				slope = -1.0*x1/x2;
			}
			
			var xi1  = header.indexOf(scatter_x1_name),
				xi2  = header.indexOf(scatter_x2_name);
			
			idsarray.forEach(function(d,i){
				if (d.value > 0) {
					i = d.key;
					if (!(data[i][1] in scatter_data)) {
						scatter_data[data[i][1]] = {key:data[i][1], values:[], slope:slope, intercept:intercept};
					}
					scatter_data[data[i][1]].values.push({x:+data[i][xi1], y:+data[i][xi2], shape:shapes[+data[i][2]], size:(+data[i][3])});
				}
			});
			
			scatterchart.xAxis.tickFormat(d3.format('.2f')).axisLabel(scatter_x1_name);
		 	scatterchart.yAxis.tickFormat(d3.format('.2f')).axisLabel(scatter_x2_name);

		 	//scatter_data = ;//( getValues(scatter_data);
			d3.select('#svg-box-scatter svg')
					.datum(d3.keys(scatter_data).sort().map(function (d){return scatter_data[d];}))
					.transition().duration(500)
					.call(scatterchart);
		}
		
		$( document ).ready(function() {
		$("#scatter_x1 a").click(function(){
			scatter_x1_name = $(this).text();
			scatter_plot();
		});
		$("#scatter_x2 a").click(function(){			
			scatter_x2_name = $(this).text();
			scatter_plot();
		});
		});
		
		// crossfilter
		var num_bins = 70, chart_width = 760,
			formatNumber = d3.format(",d"),
	  		str2int = function(d){return +d;},
	  		month2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, 0));},
	  		date2int = function(d){ d = d.split(/[- :]/); return (new Date(d[0], d[1]-1, d[2]));};;
	
		function isNumber(n) {
			return !isNaN(parseFloat(n)) && isFinite(n);
		}
	
		var sr = data[0];
	  	for (j = 3; j < sr.length; j++){
			var parseX = str2int, 
				type = 1; 
			if (!isNumber(sr[j])){
				var lx = sr[j].split(/[- :]/).length;
				if (lx >= 3)
					parseX = date2int;
				else if (lx >= 2)
					parseX = month2int;
				type = 3; // date
			}
			
			var maxX = parseX(sr[j]), minX = parseX(sr[j]);
			for (i = 1; i < data.length; i++){
				maxX  = Math.max(maxX, parseX(data[i][j]));
				minX  = Math.min(minX, parseX(data[i][j]));
			}
			var dxx = ((maxX-minX)/num_bins);
			if (dxx == 0) dxx = 1;
			var groupint = function(d){return Math.floor(d / dxx) * dxx;};
			
			var row = flight.dimension(function(d) { 
				return parseX(d[j]); }
			);
			if (type == 3) {
				//var group = row.group(d3.time.day),
				var group = row.group(function(d) { return groupint(d); }),
			 	sw = (group.size() > 35 ? chart_width : 
			 		(group.size() > 17 ? chart_width/2-11*2 : chart_width/4-11*2));
				 var bar = barChart()
			        .dimension(row)
			        .group(group)
			        .round(d3.time.day.round)
			      	.x(d3.time.scale().domain([minX, maxX]).rangeRound([0, sw]));
				 charts.push(bar);
			}
			else {
				var group = row.group(function(d) { return groupint(d); }),
				 	sw = (group.size() > 35 ? chart_width : 
				 		(group.size() > 17 ? chart_width/2-11*2 : chart_width/4-11*2));
				// full, half, and quarter sized boxes
				var bar = barChart()
	        		.dimension(row)
	        		.group(group)
	      			.x(d3.scale.linear()
	      				.domain([minX-dxx*2, maxX+dxx*2])
	      				.rangeRound([0, sw]));
				charts.push(bar);
			}
	  }

	  var chart = d3.selectAll(".chart")
	      .data(charts)
	      .each(function(chart) { chart.on("brush", renderAll).on("brushend", renderAll); });

	d3.selectAll("#total").text(formatNumber(flight.size()));
	renderAll();
	
	//reorder based on their widths
	$('.chart').sort(function (a, b) { 
		  return $(a).width() < $(b).width() ? 1 : -1;  
	}).appendTo('#svg-box-provenance');

	function render(method) { d3.select(this).call(method); }
	
	  // Whenever the brush moves, re-rendering everything.
	function renderAll() {
	  	scatter_plot();	
	    chart.each(render);
	    d3.select("#active").text(formatNumber(all.value()));
	}
	
	window.filter = function(filters) {
	    filters.forEach(function(d, i) { charts[i].filter(d); });
	    renderAll();
	};
	
	window.reset = function(i) {
	    charts[i].filter(null);
	    renderAll();
	};
	
	 
	function barChart() {
	    if (!barChart.id) barChart.id = 0;
	
	    var margin = {top: 10, right: 10, bottom: 20, left: 10},
	        x,
	        y = d3.scale.linear().range([100, 0]),
	        id = barChart.id++,
	        axis = d3.svg.axis().orient("bottom"),
	        brush = d3.svg.brush(),
	        brushDirty,
	        dimension,
	        group,
	        round;
	
	    function chart(div) {
	      var width = x.range()[1],
	          height = y.range()[0];
	
	      var temp = group.top(1);
	      y.domain([0, group.top(1)[0].value]);
	
	      div.each(function() {
	        var div = d3.select(this),
	            g = div.select("g");
	
	        // Create the skeletal chart.
	        if (g.empty()) {
	          div.select(".title").append("a")
	              .attr("href", "javascript:reset(" + id + ")")
	              .attr("class", "reset")
	              .text("reset")
	              .style("display", "none");
	
	          g = div.append("svg")
	              .attr("width", width + margin.left + margin.right)
	              .attr("height", height + margin.top + margin.bottom)
	            .append("g")
	              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	          g.append("clipPath")
	              .attr("id", "clip-" + id)
	            .append("rect")
	              .attr("width", width)
	              .attr("height", height);
	
	          g.selectAll(".bar")
	              .data(["background", "foreground"])
	            .enter().append("path")
	              .attr("class", function(d) { return d + " bar" + " classid"+id; })
	              .datum(group.all());
	
	          g.selectAll(".foreground.bar")
	              .attr("clip-path", "url(#clip-" + id + ")");
	
	          g.append("g")
	              .attr("class", "axis")
	              .attr("transform", "translate(0," + height + ")")
	              .call(axis);
	
	          // Initialize the brush component with pretty resize handles.
	          var gBrush = g.append("g").attr("class", "brush").call(brush);
	          gBrush.selectAll("rect").attr("height", height);
	          gBrush.selectAll(".resize").append("path").attr("d", resizePath);
	        }
	
	        // Only redraw the brush if set externally.
	        if (brushDirty) {
	          brushDirty = false;
	          g.selectAll(".brush").call(brush);
	          div.select(".title a").style("display", brush.empty() ? "none" : null);
	          if (brush.empty()) {
	            g.selectAll("#clip-" + id + " rect")
	                .attr("x", 0)
	                .attr("width", width);
	          } else {
	            var extent = brush.extent();
	            g.selectAll("#clip-" + id + " rect")
	                .attr("x", x(extent[0]))
	                .attr("width", x(extent[1]) - x(extent[0]));
	          }
	        }
	
	        g.selectAll(".bar").attr("d", barPath);
	      });
	
	      function barPath(groups) {
	        var path = [],
	            i = -1,
	            n = groups.length,
	            d;
	        while (++i < n) {
	          d = groups[i];
	          path.push("M", x(d.key), ",", height, "V", y(d.value), "h9V", height);
	        }
	        return path.join("");
	      }
	
	      function resizePath(d) {
	        var e = +(d == "e"),
	            x = e ? 1 : -1,
	            y = height / 3;
	        return "M" + (.5 * x) + "," + y
	            + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6)
	            + "V" + (2 * y - 6)
	            + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y)
	            + "Z"
	            + "M" + (2.5 * x) + "," + (y + 8)
	            + "V" + (2 * y - 8)
	            + "M" + (4.5 * x) + "," + (y + 8)
	            + "V" + (2 * y - 8);
	      }
	    }
	
	    brush.on("brushstart.chart", function() {
	      var div = d3.select(this.parentNode.parentNode.parentNode);
	      div.select(".title a").style("display", null);
	    });
	
	    brush.on("brush.chart", function() {
	      var g = d3.select(this.parentNode),
	          extent = brush.extent();
	      if (round) g.select(".brush")
				.call(brush.extent(extent = extent.map(round)))
				.selectAll(".resize")
				.style("display", null);
	      g.select("#clip-" + id + " rect")
	          .attr("x", x(extent[0]))
	          .attr("width", x(extent[1]) - x(extent[0]));
	      dimension.filterRange(extent);
	    });
	
	    brush.on("brushend.chart", function() {
	      if (brush.empty()) {
	        var div = d3.select(this.parentNode.parentNode.parentNode);
	        div.select(".title a").style("display", "none");
	        div.select("#clip-" + id + " rect").attr("x", null).attr("width", "100%");
	        dimension.filterAll();
	      }
	    });
	
	    chart.margin = function(_) {
	      if (!arguments.length) return margin;
	      margin = _;
	      return chart;
	    };
	
	    chart.x = function(_) {
	      if (!arguments.length) return x;
	      x = _;
	      axis.scale(x).ticks(Math.floor(x.range()[1]/40));
	      brush.x(x);
	      return chart;
	    };
	
	    chart.y = function(_) {
	      if (!arguments.length) return y;
	      y = _;
	      return chart;
	    };
	
	    chart.dimension = function(_) {
	      if (!arguments.length) return dimension;
	      dimension = _;
	      return chart;
	    };
	
	    chart.filter = function(_) {
	      if (_) {
	        brush.extent(_);
	        dimension.filterRange(_);
	      } else {
	        brush.clear();
	        dimension.filterAll();
	      }
	      brushDirty = true;
	      return chart;
	    };
	
	    chart.group = function(_) {
	      if (!arguments.length) return group;
	      group = _;
	      return chart;
	    };
	
	    chart.round = function(_) {
	      if (!arguments.length) return round;
	      round = _;
	      return chart;
	    };
	
	    return d3.rebind(chart, brush, "on");
	  }
	});
	function getValues(x){
		var y = [];
		for (i in x){ y.push(x[i]);}
		return y;
	}
}