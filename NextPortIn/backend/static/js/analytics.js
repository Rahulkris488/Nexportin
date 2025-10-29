document.addEventListener('DOMContentLoaded', () => {
    // Set up D3 charts
    const timeDistribution = setupTimeDistributionChart();
    const costImpact = setupCostImpactChart();
    const performance = setupPerformanceChart();
    const recovery = setupRecoveryChart();

    // Initialize data
    let analyticsData = {
        deliveryTimes: [],
        costs: [],
        disruptions: [],
        recoveryImpact: []
    };

    // Fetch and update data periodically
    async function updateAnalytics() {
        try {
            const response = await fetch('/api/map');
            const data = await response.json();
            
            // Process data for charts
            processDeliveryTimes(data.shipments);
            processCosts(data.shipments);
            processDisruptions(data);
            processRecoveryImpact(data);
            
            // Update charts
            updateCharts();
            
        } catch (error) {
            console.error('Failed to update analytics:', error);
        }
    }

    function setupTimeDistributionChart() {
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const width = document.getElementById('timeDistributionChart').clientWidth - margin.left - margin.right;
        const height = document.getElementById('timeDistributionChart').clientHeight - margin.top - margin.bottom;

        const svg = d3.select('#timeDistributionChart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        return {svg, width, height};
    }

    function setupCostImpactChart() {
        const margin = {top: 20, right: 20, bottom: 30, left: 60};
        const width = document.getElementById('costImpactChart').clientWidth - margin.left - margin.right;
        const height = document.getElementById('costImpactChart').clientHeight - margin.top - margin.bottom;

        const svg = d3.select('#costImpactChart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        return {svg, width, height};
    }

    function setupPerformanceChart() {
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const width = document.getElementById('performanceChart').clientWidth - margin.left - margin.right;
        const height = document.getElementById('performanceChart').clientHeight - margin.top - margin.bottom;

        const svg = d3.select('#performanceChart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        return {svg, width, height};
    }

    function setupRecoveryChart() {
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const width = document.getElementById('recoveryChart').clientWidth - margin.left - margin.right;
        const height = document.getElementById('recoveryChart').clientHeight - margin.top - margin.bottom;

        const svg = d3.select('#recoveryChart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        return {svg, width, height};
    }

    function processDeliveryTimes(shipments) {
        analyticsData.deliveryTimes = shipments
            .filter(s => s.status === 'delivered')
            .map(s => {
                return {
                    id: s.id,
                    time: s.estimated_arrival - s.start_time
                };
            });
    }

    function processCosts(shipments) {
        analyticsData.costs = shipments.map(s => {
            return {
                id: s.id,
                cost: calculateShipmentCost(s)
            };
        });
    }

    function processDisruptions(data) {
        analyticsData.disruptions = [
            ...data.nodes
                .filter(n => n.status === 'disrupted')
                .map(n => ({
                    type: 'node',
                    id: n.id,
                    impact: calculateDisruptionImpact(n)
                })),
            ...data.edges
                .filter(e => e.status === 'disrupted')
                .map(e => ({
                    type: 'edge',
                    id: e.id,
                    impact: calculateDisruptionImpact(e)
                }))
        ];
    }

    function processRecoveryImpact(data) {
        // This would need to be implemented based on your recovery tracking
        analyticsData.recoveryImpact = [];
    }

    function calculateShipmentCost(shipment) {
        // Simplified cost calculation
        return shipment.route.length * 1000;
    }

    function calculateDisruptionImpact(entity) {
        // Simplified impact calculation
        return Math.random() * 100;
    }

    function updateCharts() {
        updateTimeDistributionChart();
        updateCostImpactChart();
        updatePerformanceChart();
        updateRecoveryChart();
    }

    function updateTimeDistributionChart() {
        const {svg, width, height} = timeDistribution;
        
        // Clear previous content
        svg.selectAll('*').remove();

        // Create histogram
        const histogram = d3.histogram()
            .value(d => d.time)
            .domain([0, d3.max(analyticsData.deliveryTimes, d => d.time)])
            .thresholds(20);

        const bins = histogram(analyticsData.deliveryTimes);

        // Create scales
        const x = d3.scaleLinear()
            .domain([0, d3.max(bins, d => d.x1)])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(bins, d => d.length)])
            .range([height, 0]);

        // Add bars
        svg.selectAll('rect')
            .data(bins)
            .enter()
            .append('rect')
            .attr('x', d => x(d.x0))
            .attr('y', d => y(d.length))
            .attr('width', d => x(d.x1) - x(d.x0) - 1)
            .attr('height', d => height - y(d.length))
            .style('fill', '#3498db');

        // Add axes
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).ticks(10));

        svg.append('g')
            .call(d3.axisLeft(y));
    }

    function updateCostImpactChart() {
        const {svg, width, height} = costImpact;
        
        // Clear previous content
        svg.selectAll('*').remove();

        // Create line chart
        const x = d3.scaleLinear()
            .domain([0, analyticsData.costs.length])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(analyticsData.costs, d => d.cost)])
            .range([height, 0]);

        // Add line
        const line = d3.line()
            .x((d, i) => x(i))
            .y(d => y(d.cost));

        svg.append('path')
            .datum(analyticsData.costs)
            .attr('fill', 'none')
            .attr('stroke', '#e74c3c')
            .attr('stroke-width', 2)
            .attr('d', line);

        // Add axes
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x));

        svg.append('g')
            .call(d3.axisLeft(y));
    }

    function updatePerformanceChart() {
        const {svg, width, height} = performance;
        
        // Clear previous content
        svg.selectAll('*').remove();

        // Create bar chart for network performance
        const data = [
            {metric: 'Node Health', value: calculateNodeHealth()},
            {metric: 'Edge Health', value: calculateEdgeHealth()},
            {metric: 'Delivery Rate', value: calculateDeliveryRate()}
        ];

        const x = d3.scaleBand()
            .domain(data.map(d => d.metric))
            .range([0, width])
            .padding(0.1);

        const y = d3.scaleLinear()
            .domain([0, 100])
            .range([height, 0]);

        // Add bars
        svg.selectAll('rect')
            .data(data)
            .enter()
            .append('rect')
            .attr('x', d => x(d.metric))
            .attr('y', d => y(d.value))
            .attr('width', x.bandwidth())
            .attr('height', d => height - y(d.value))
            .style('fill', '#2ecc71');

        // Add axes
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x));

        svg.append('g')
            .call(d3.axisLeft(y));
    }

    function updateRecoveryChart() {
        const {svg, width, height} = recovery;
        
        // Clear previous content
        svg.selectAll('*').remove();

        // Create scatter plot for recovery effectiveness
        const x = d3.scaleLinear()
            .domain([0, d3.max(analyticsData.recoveryImpact, d => d.cost)])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(analyticsData.recoveryImpact, d => d.time)])
            .range([height, 0]);

        // Add points
        svg.selectAll('circle')
            .data(analyticsData.recoveryImpact)
            .enter()
            .append('circle')
            .attr('cx', d => x(d.cost))
            .attr('cy', d => y(d.time))
            .attr('r', 5)
            .style('fill', '#9b59b6');

        // Add axes
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x));

        svg.append('g')
            .call(d3.axisLeft(y));
    }

    function calculateNodeHealth() {
        return Math.random() * 100;  // Replace with actual calculation
    }

    function calculateEdgeHealth() {
        return Math.random() * 100;  // Replace with actual calculation
    }

    function calculateDeliveryRate() {
        return Math.random() * 100;  // Replace with actual calculation
    }

    // Time range change handler
    document.getElementById('timeRange').addEventListener('change', (e) => {
        // Update data based on new time range
        updateAnalytics();
    });

    // Metric visibility handlers
    document.getElementById('showDeliveryTimes').addEventListener('change', updateCharts);
    document.getElementById('showCosts').addEventListener('change', updateCharts);
    document.getElementById('showDisruptions').addEventListener('change', updateCharts);
    document.getElementById('showRecovery').addEventListener('change', updateCharts);

    // Initial load
    updateAnalytics();

    // Refresh data periodically
    setInterval(updateAnalytics, 5000);

    // Handle window resize
    window.addEventListener('resize', () => {
        // Recreate charts with new dimensions
        timeDistribution = setupTimeDistributionChart();
        costImpact = setupCostImpactChart();
        performance = setupPerformanceChart();
        recovery = setupRecoveryChart();
        updateCharts();
    });
});