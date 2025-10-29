document.addEventListener('DOMContentLoaded', () => {
    // Ensure simulation is available
    if (!window.simulation) {
        console.error('Simulation not initialized');
        alert('Error: Simulation not properly initialized. Please refresh the page.');
        return;
    }
    const simulation = window.simulation;

    // Control handlers
    document.getElementById('startSimulation').addEventListener('click', () => {
        if (!simulation.isRunning) {
            simulation.start();
        }
    });

    document.getElementById('pauseSimulation').addEventListener('click', () => {
        simulation.pause();
    });

    document.getElementById('resetSimulation').addEventListener('click', () => {
        simulation.reset();
    });

    document.getElementById('speedControl').addEventListener('input', (e) => {
        simulation.speed = parseInt(e.target.value);
    });

    // Modal handlers
    const disruptionModal = document.getElementById('disruptionModal');
    const recoveryModal = document.getElementById('recoveryModal');

    document.getElementById('injectDisruption').addEventListener('click', () => {
        disruptionModal.style.display = 'block';
        populateDisruptionTargets();
    });

    document.getElementById('applyRecovery').addEventListener('click', () => {
        recoveryModal.style.display = 'block';
        populateRecoveryOptions();
    });

    // Close modals when clicking cancel or outside
    document.querySelectorAll('.modal .cancel').forEach(button => {
        button.addEventListener('click', () => {
            disruptionModal.style.display = 'none';
            recoveryModal.style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target === disruptionModal) disruptionModal.style.display = 'none';
        if (e.target === recoveryModal) recoveryModal.style.display = 'none';
    });

    // Form submissions
    document.getElementById('disruptionForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const disruption = {
            type: document.getElementById('disruptionType').value,
            target_id: document.getElementById('targetId').value,
            duration: parseInt(document.getElementById('duration').value),
            severity: parseInt(document.getElementById('severity').value) / 10
        };

        try {
            await simulation.injectDisruption(disruption);
            disruptionModal.style.display = 'none';
        } catch (error) {
            alert('Failed to inject disruption: ' + error.message);
        }
    });

    document.getElementById('recoveryForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const strategyType = document.getElementById('strategyType').value;
        if (!strategyType) {
            alert('Please select a recovery strategy type');
            return;
        }

        const strategy = {
            type: strategyType,
            parameters: {}
        };

        try {
            if (strategy.type === 'reroute') {
                const origin = document.getElementById('origin').value;
                const destination = document.getElementById('destination').value;
                
                if (!origin || !destination) {
                    throw new Error('Please select both origin and destination');
                }
                
                strategy.parameters = {
                    origin: origin,
                    destination: destination,
                    new_route: [origin + '-' + destination] // Simplified route for demonstration
                };
            } else if (strategy.type === 'alternate_supplier') {
                const original = document.getElementById('originalSupplier').value;
                const alternate = document.getElementById('alternateSupplier').value;
                
                if (!original || !alternate) {
                    throw new Error('Please select both original and alternate suppliers');
                }
                
                strategy.parameters = {
                    original: original,
                    alternate: alternate
                };
            } else {
                throw new Error('Invalid strategy type');
            }

            await simulation.applyRecoveryStrategy(strategy);
            recoveryModal.style.display = 'none';
        } catch (error) {
            console.error('Recovery strategy application failed:', error);
            alert('Failed to apply recovery strategy: ' + error.message);
        }
    });

    // Recovery strategy type change handler
    document.getElementById('strategyType').addEventListener('change', (e) => {
        const reroute = document.getElementById('reroute-options');
        const supplier = document.getElementById('supplier-options');
        
        if (e.target.value === 'reroute') {
            reroute.style.display = 'block';
            supplier.style.display = 'none';
        } else {
            reroute.style.display = 'none';
            supplier.style.display = 'block';
        }
    });

    async function populateDisruptionTargets() {
        try {
            const response = await fetch('/api/map');
            const data = await response.json();
            
            const targetSelect = document.getElementById('targetId');
            targetSelect.innerHTML = '';
            
            const type = document.getElementById('disruptionType').value;
            
            if (type === 'node') {
                data.nodes.forEach(node => {
                    const option = document.createElement('option');
                    option.value = node.id;
                    option.textContent = `${node.id} (${node.type})`;
                    targetSelect.appendChild(option);
                });
            } else {
                data.edges.forEach(edge => {
                    const option = document.createElement('option');
                    option.value = edge.id;
                    option.textContent = `${edge.id} (${edge.transport_type})`;
                    targetSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load targets:', error);
        }
    }

    async function populateRecoveryOptions() {
        try {
            const response = await fetch('/api/map');
            const data = await response.json();
            
            // Populate origin/destination selects
            const originSelect = document.getElementById('origin');
            const destSelect = document.getElementById('destination');
            
            originSelect.innerHTML = '';
            destSelect.innerHTML = '';
            
            data.nodes.forEach(node => {
                const optionOrigin = document.createElement('option');
                optionOrigin.value = node.id;
                optionOrigin.textContent = `${node.id} (${node.type})`;
                originSelect.appendChild(optionOrigin);
                
                const optionDest = document.createElement('option');
                optionDest.value = node.id;
                optionDest.textContent = `${node.id} (${node.type})`;
                destSelect.appendChild(optionDest);
            });
            
            // Populate supplier selects
            const originalSelect = document.getElementById('originalSupplier');
            const alternateSelect = document.getElementById('alternateSupplier');
            
            originalSelect.innerHTML = '';
            alternateSelect.innerHTML = '';
            
            const factories = data.nodes.filter(node => node.type === 'factory');
            
            factories.forEach(factory => {
                const optionOriginal = document.createElement('option');
                optionOriginal.value = factory.id;
                optionOriginal.textContent = factory.id;
                originalSelect.appendChild(optionOriginal);
                
                const optionAlternate = document.createElement('option');
                optionAlternate.value = factory.id;
                optionAlternate.textContent = factory.id;
                alternateSelect.appendChild(optionAlternate);
            });
        } catch (error) {
            console.error('Failed to load recovery options:', error);
        }
    }

    // Disruption type change handler
    document.getElementById('disruptionType').addEventListener('change', populateDisruptionTargets);

    // Initial setup
    populateDisruptionTargets();
    populateRecoveryOptions();
});