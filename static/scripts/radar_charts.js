document.addEventListener('DOMContentLoaded', function() {
    function createRadarChart(ctx, labels, datasets, legend) {
        const data = {
            labels: labels.map(label => label.text),
            datasets: datasets
        };

        const config = {
            type: 'radar',
            data: data,
            options: {
                plugins: {
                    
                    legend: {
                        display: legend
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItem) {
                                const index = tooltipItem[0].dataIndex;
                                return labels[index].text;
                            }
                        }
                    }
                }
            }
        };

        new Chart(ctx, config);
    }

    const resourceCtx = document.getElementById('resource-data').getContext('2d');
    createRadarChart(resourceCtx, radarGraphInfo.resource_graph.labels, radarGraphInfo.resource_graph.datasets, true);

    const combatCtx = document.getElementById('combat-data').getContext('2d');
    createRadarChart(combatCtx, radarGraphInfo.combat_graph.labels, radarGraphInfo.combat_graph.datasets, true);

    const objectiveCtx = document.getElementById('objective-data').getContext('2d');
    createRadarChart(objectiveCtx, radarGraphInfo.objective_graph.labels, radarGraphInfo.objective_graph.datasets, true);
});