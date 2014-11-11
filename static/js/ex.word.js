function word_update(){
	$("#svg-box-word").find("svg").remove();
	var Text = modules['word']['variables']['Text'];
	var words = {};
	var d3min = Infinity, d3max = 0;
	var re =  new RegExp("[^a-z0-9@]+", "gi"); 
	var ids  = modules['word']['crossfilter']['group'].all();
	ids.forEach(function(d){
		if (d.value>0){
			var line = bigdata[d.key][Text];
			if (line.length>0){
				line = line.toLowerCase().replace(re, ' ').split(' ');
				line.forEach(function(d){
					if (d in words) {
						words[d]["size"]++;
					}
					else{
						if (d.length > 3){
							words[d] = {size:1, text:d};
						}
					}
				});				
			}			
		}
	});    
	var fill = d3.scale.linear().domain([ 0, 100 ]).range([ "#000", "#bbb" ]);
	words = d3.values(words);
	var min_size = d3.min(words, function(d) {return +d.size;});
	var range_size = d3.max(words, function(d) {return +d.size;}) - min_size;
	var change_size = function(d) {
		var r = ~~((d - min_size) * 120 / range_size) + 10;
		return r;
	};
	words.forEach(function(d) {d['size'] = change_size(d['size'])});

	d3.layout.cloud()
		.size([960, 400])
		.words(words)
		.padding(5)
		.rotate(function() {return ~~(Math.random() * 2) * 90;})
		.font("helvetica-neue")
		.fontSize(function(d) {return d.size;})
		.on("end", draw)
		.start();

	function draw(words) {
		d3.select("#svg-box-word")
			.append("svg")
				.attr("width", 960)
				.attr("height", 400)
			.append("g")
				.attr("transform","translate(480,200)")
			.selectAll("text")
				.data(words)
				.enter()
			.append("text")
				.style("font-size", function(d) {return d.size + "px";})
				.style("font-family", "helvetica-neue").style("fill",function(d, i) {return fill(i);})
				.attr("text-anchor", "middle")
				.attr("transform",function(d) {return "translate(" + [ d.x, d.y ] + ")rotate(" + d.rotate + ")";})
				.text(function(d) {return d.text;});
	}
		
}


function word_draw() {	    


	var mdimension = flight.dimension(function(d){ return d.cf_id;}),
		msgroup = mdimension.group();
	modules['word']['crossfilter']={'dimension': mdimension, 'group': msgroup};
	
	word_update();
}

