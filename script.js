(function() {
    function update(svg, us, ym) {
        let file = '';
        file = file.concat("csv/", ym, ".csv");
        d3.csv(file).then(function(data) {
            data.forEach(function(d) {
                // extract only c_fips and per_capita (or total)
                d.total = +d.total;
                d.per_capita = +d.per_capita
                delete d['county'];
                delete d['state'];
                delete d['total'];
                // delete d['per_capita'];
            });
        
            // transform data to Map of c_fips => per_capita
            data = data.map(x => Object.values(x));
            data = new Map(data);
            
            format = d3.format(",.7f");
            radius = d3.scaleSqrt([0, d3.quantile([...data.values()].sort(d3.ascending), 0.985)], [0, 10])

            svg.select("g")
                .selectAll("circle")
                .data(topojson.feature(us, us.objects.counties).features
                .map(d => (d.value = data.get(d.id), d))
                .sort((a, b) => b.value - a.value))
            .join("circle")
                .attr("transform", d => `translate(${path.centroid(d)})`)
                .attr("r", d => radius(d.value))
                .append("title")
                .text(d => `${d.properties.name}${format(d.value)}`);

            // change label
            d3.select("body").select("h2").text(ym);
        });
    }

    window.onload = function() {
        d3.select("body").append("h1").text("FCC Internet Complaints Per County Per Capita");
        d3.select("body").append("h2");

        d3.json("counties-albers-10m.json").then(function(us){
            path = d3.geoPath();

            const svg = d3.select("body").append("svg")
                            .attr("viewBox", [-10, 0, 975, 610]);

            // outline us map
            svg.append("path")
                .datum(topojson.feature(us, us.objects.nation))
                .attr("fill", "#ccc")
                .attr("d", path);

            // outline state border
            svg.append("path")
                .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
                .attr("fill", "none")
                .attr("stroke", "white")
                .attr("stroke-linejoin", "round")
                .attr("d", path);

            // for circle
            svg.append("g")
                .attr("fill", "brown")
                .attr("fill-opacity", 0.5)
                .attr("stroke", "#fff")
                .attr("stroke-width", 0.5)

            // initialize start and end ym
            let y = 2014;
            let m = 10;
            let endY = 2020;
            let endM = 5;

            var animate = setInterval(function() {
                // get year-month string
                let yStr = y.toString();
                let mStr = m.toString();
                if (m < 10) {
                    mStr = "0" + mStr;
                }
                let ym = yStr.concat("-", mStr);

                // call update function
                update(svg, us, ym);

                // check for end point
                if (y == endY && m == endM) {
                    clearInterval(animate);
                }
                // update year
                if (m == 12) {
                    y += 1;
                }
                // update month
                if (m == 12) {
                    m = 1;
                } else {
                    m += 1;
                }
            }, 1000);
        })
        .catch(function(error){
            console.log(error);
        });
    };
})();