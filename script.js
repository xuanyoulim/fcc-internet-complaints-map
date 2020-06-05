(function() {
    function makeMap() {
        chart = d3.json("counties-albers-10m.json").then(function(us){
            // console.log(data.objects);
            path = d3.geoPath();
            // topojson = require("topojson-client@3");
    
            const svg = d3.create("svg")
            .attr("viewBox", [0, 0, 975, 610]);
    
            svg.append("path")
            .datum(topojson.feature(us, us.objects.nation))
            .attr("fill", "#ccc")
            .attr("d", path);
    
            return svg.node();
        })
        .catch(function(error){
            console.log("error")
        });

    }
    window.onload = function() {
        // var map = makeMap();
        // d3.select("body").append("map")        
        chart = d3.json("counties-albers-10m.json").then(function(us){
            d3.csv("csv/2015-01.csv").then(function(data) {
                data.forEach(function(d) {
                    d.total = +d.total;
                    d.per_capita = +d.per_capita
                    delete d['county'];
                    delete d['state'];
                    delete d['total'];
                    console.log(d)
                    // return Object.values(d)
                });

                data = data.map(x => Object.values(x));
                data = new Map(data);

                // console.log(data.objects);
                path = d3.geoPath();
                // topojson = require("topojson-client@3");
        
                const svg = d3.select("body").append("svg")
                .attr("viewBox", [0, 0, 975, 610]);

                feature = topojson.feature(us, us.objects.nation)
        
                svg.append("path")
                .datum(topojson.feature(us, us.objects.nation))
                .attr("fill", "#ccc")
                .attr("d", path);

                svg.append("path")
                .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
                .attr("fill", "none")
                .attr("stroke", "white")
                .attr("stroke-linejoin", "round")
                .attr("d", path);

                format = d3.format(",.0f");
                radius = d3.scaleSqrt([0, d3.quantile([...data.values()].sort(d3.ascending), 0.985)], [0, 10]);

                svg.append("g")
                    .attr("fill", "brown")
                    .attr("fill-opacity", 0.5)
                    .attr("stroke", "#fff")
                    .attr("stroke-width", 0.5)
                .selectAll("circle")
                .data(topojson.feature(us, us.objects.counties).features
                    .map(d => (d.value = data.get(d.id), d))
                    .sort((a, b) => b.value - a.value))
                .join("circle")
                    .attr("transform", d => `translate(${path.centroid(d)})`)
                    .attr("r", d => radius(d.value))
                .append("title")
                    .text(d => `${d.properties.name}
                ${format(d.value)}`);

            });

        })
        .catch(function(error){
            console.log("error")
        });;
    };
})();