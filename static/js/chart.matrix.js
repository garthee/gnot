var chart_matrix = function() {
	d3.csv(file_pca_matrix, function(data) {
		var pca_features =  get_pca_features(data);
	  	var atts = data.map(function(d){ return d.feature;}).sort();
	  	var cats = d3.keys(data[0]).filter(function(d) { return d != 'feature'; }).sort();
	  	var matrix_data = get_matrix_data(pca_features, atts, cats);
	
		var rect_width = 16, rect_gap = 1;
		var maxd = Math.max(d3.max(d3.max(matrix_data)), -1*d3.min(d3.min(matrix_data)));
		var opacity = d3.scale.linear()
			.domain([0, maxd])
			.range([0, 1]);
	      
		var grid = d3.select("#svg-pca_matrix").append("svg:svg")
			.attr("width", 200 + atts.length*(rect_width+rect_gap))
			.attr("height", 80 + cats.length*(rect_width+rect_gap))
			.append("g")
			.classed("grid", true)
			.attr("transform", "translate(150, 60)");
		      
		var rows = grid.selectAll("g")
			.data(matrix_data)
			.enter().append("g");
		
		rows.selectAll("rect")
			.data(function(d) {return d;})
		    .enter().append("rect")
			.attr("x", function(d, i, j) {return j*(rect_width+rect_gap);})
			.attr("y", function(d, i, j) {return i*(rect_width+rect_gap);})
			.attr("width", function(d, i, j) {return rect_width;})
			.attr("height", function(d, i, j) {return rect_width;})
			.style("fill", function(d){ if (d > 0){ return 'steelblue'; }else{return '#ff7f0e';}})
			.style("opacity", function(d){ return Math.abs(d)/maxd; })
			.append("svg:title")
			.text(function(d) { return d; });
		
		var att_labels = d3.select("#svg-pca_matrix svg")
		  	.append("g")
		  	.classed("att labels", true)
		  	.attr("transform", "translate(162, 55)");
		att_labels.selectAll("text")
			.data(atts)
			.enter().append("text")
			.attr("transform", function(d, i) {return "translate("+i*(rect_width+rect_gap)+", 0) rotate(270)";})
			.text(function(d) {return d;})
			.on("click", sortCatsByAtt);
		
		var cat_labels = d3.select("#svg-pca_matrix svg")
		  	.append("g")
		  	.classed("cat labels", true)
		  	.attr("transform", "translate(50, 72)");
		cat_labels.selectAll("text")
			.data(cats)
			.enter().append("text")
			.attr("x", 95)
			.attr("y", function(d, i) {return i*(rect_width+rect_gap);})
			.text(function(d) {return d;})
			.on("click", sortAttsByCat);
		
		function updateGrid() {
			var matrix_data = get_matrix_data(pca_features, atts, cats);
		    var rows = d3.select(".grid").selectAll("g")
				.data(matrix_data)
		    	.selectAll("rect")
		        .data(function(d) {return d;})
		        .style("fill", function(d){ if (d > 0){ return 'steelblue'; }else{return '#ff7f0e';}})
				.style("opacity", function(d){ return Math.abs(d)/maxd; })
				.select("title").text(function(d) { return d; });
			
		
		    var cat_labels = d3.select(".cat.labels")
		    	.selectAll("text")
		        .data(cats)
		        .text(function(d) {return d;});
		
		    var att_labels = d3.select(".att.labels")
		    	.selectAll("text")
		        .data(atts)
		        .text(function(d) {return d;});
		}
		
		function get_pca_features(data) {
		    var pca_features = {}; 
		    for(var i=0; i<data.length; i++) {
				pca_features[data[i].feature] = data[i];
		    }
		    return pca_features;
		}
		
		function get_matrix_data(pca_features, atts, cats) {
		    var data = [];
		    for(var a=0; a<atts.length; a++) {
				data[a] = [];
		      	for(var c=0; c<cats.length; c++) {
		        	var freq = pca_features[atts[a]][cats[c]] === undefined? 0 : pca_features[atts[a]][cats[c]];
		        	data[a][c] = (freq === undefined) ? 0 : freq; 
		      	}
		    }
		    return data;
		}
		
		function sortAttsByCat(d) {
		    //sort atts by weight of attendence to category d and refresh
		    atts.sort(function(a, b) {
				a_freq = pca_features[a][d] === undefined ? 0 : pca_features[a][d];
		      	b_freq = pca_features[b][d] === undefined ? 0 : pca_features[b][d];
		      	if(a_freq === b_freq)
		        	return a<b?-1:1;
		      	return b_freq-a_freq;
		    });
		    updateGrid();
		}
		
		function sortCatsByAtt(d) {
		    //sort topics by weight of attendence by attendee d and refresh
		    cats.sort(function(a, b) {
		    	a_freq = pca_features[d][a] === undefined ? 0 : pca_features[d][a];
		      	b_freq = pca_features[d][b] === undefined ? 0 : pca_features[d][b];
		      	if(a_freq === b_freq)
		        	return a<b?-1:1;
		      	return b_freq-a_freq;
		    	});
		    updateGrid();
		}
	});
};