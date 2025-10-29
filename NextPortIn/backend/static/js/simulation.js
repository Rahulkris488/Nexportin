class SupplyChainSimulation {
    constructor() {
        this.isRunning = false;
        this.speed = 5;
        this.currentTime = 0;
        this.networkState = null;
        this.eventLog = [];
    }

    async start() {
        this.isRunning = true;
        while (this.isRunning) {
            await this.step();
            await this.sleep(1000 / this.speed);
        }
    }

    pause() {
        this.isRunning = false;
    }

    reset() {
        this.currentTime = 0;
        this.networkState = null;
        this.eventLog = [];
        this.updateUI();
    }

    async step() {
        try {
            const response = await fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ steps: 1 })
            });
            
            const data = await response.json();
            this.networkState = data;
            this.currentTime += 1;
            this.updateUI();
            
        } catch (error) {
            console.error('Simulation step failed:', error);
            this.logEvent('error', 'Simulation step failed: ' + error.message);
        }
    }

    async injectDisruption(disruption) {
        try {
            const response = await fetch('/api/disrupt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(disruption)
            });
            
            const data = await response.json();
            this.logEvent('disruption', `Disruption injected: ${disruption.type} at ${disruption.target_id}`);
            return data;
            
        } catch (error) {
            console.error('Failed to inject disruption:', error);
            this.logEvent('error', 'Failed to inject disruption: ' + error.message);
            throw error;
        }
    }

    async applyRecoveryStrategy(strategy) {
        if (!strategy || !strategy.type) {
            const error = new Error('Invalid recovery strategy: missing required parameters');
            this.logEvent('error', error.message);
            throw error;
        }

        try {
            const response = await fetch('/api/recover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(strategy)
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.logEvent('recovery', `Recovery strategy applied: ${strategy.type}`);
            return data;
            
        } catch (error) {
            console.error('Failed to apply recovery strategy:', error);
            this.logEvent('error', 'Failed to apply recovery strategy: ' + error.message);
            throw error;
        }
    }

    updateUI() {
        if (!this.networkState) return;

        // Update metrics
        document.getElementById('activeShipments').textContent = 
            this.networkState.metrics.active_shipments;
        document.getElementById('totalDelay').textContent = 
            this.formatTime(this.networkState.metrics.total_delay);
        document.getElementById('totalCost').textContent = 
            this.formatCurrency(this.networkState.metrics.total_cost);
        
        const healthPercentage = this.calculateNetworkHealth();
        document.getElementById('networkHealth').textContent = 
            `${healthPercentage}%`;

        // Update event log
        this.updateEventLog();
    }

    calculateNetworkHealth() {
        if (!this.networkState) return 100;

        const totalNodes = Object.keys(this.networkState.nodes || {}).length;
        const totalEdges = Object.keys(this.networkState.edges || {}).length;
        
        const disruptedNodes = this.networkState.metrics.disrupted_nodes;
        const disruptedEdges = this.networkState.metrics.disrupted_edges;
        
        if (totalNodes === 0 || totalEdges === 0) return 100;
        
        const nodeHealth = ((totalNodes - disruptedNodes) / totalNodes) * 100;
        const edgeHealth = ((totalEdges - disruptedEdges) / totalEdges) * 100;
        
        return Math.round((nodeHealth + edgeHealth) / 2);
    }

    logEvent(type, message) {
        const event = {
            timestamp: new Date(),
            type,
            message
        };
        this.eventLog.unshift(event);
        this.updateEventLog();
    }

    updateEventLog() {
        const logElement = document.getElementById('eventLog');
        logElement.innerHTML = this.eventLog
            .slice(0, 100)  // Keep only last 100 events
            .map(event => {
                const time = event.timestamp.toLocaleTimeString();
                return `
                    <div class="event-${event.type}">
                        <strong>${time}</strong>: ${event.message}
                    </div>
                `;
            })
            .join('');
    }

    formatTime(hours) {
        return `${Math.round(hours)}h`;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize simulation and make it globally available
window.simulation = new SupplyChainSimulation();