// static/js/dashboard_charts.js

// Guardamos las instancias para evitar que las gráficas se redibujen unas sobre otras
let estadoChartInstance = null;
let turnoChartInstance = null;

document.addEventListener('DOMContentLoaded', function () {
    const dataContainer = document.getElementById('graficas-data');
    if (!dataContainer) return;

    // Parseamos el string JSON que nos pasó la vista de Django
    const data = JSON.parse(dataContainer.dataset.json);

    // --- GRÁFICA DE ESTADOS (DONA) ---
    const canvasEstado = document.getElementById('graficaEstadoTickets');
    if (canvasEstado) {
        // Si ya existe una gráfica en este canvas, la destruimos primero
        if (estadoChartInstance) {
            estadoChartInstance.destroy();
        }
        estadoChartInstance = new Chart(canvasEstado.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: data.estado_labels,
                datasets: [{ 
                    data: data.estado_data, 
                    backgroundColor: data.estado_colors, 
                    borderWidth: 1 
                }]
            },
            options: { 
                responsive: true, 
                plugins: { legend: { display: true, position: 'bottom' } }, 
                cutout: '70%'
                // La función de click se podría añadir aquí si se necesita
            }
        });
    }

    // --- GRÁFICA DE TURNOS (BARRAS APILADAS) ---
    const canvasTurno = document.getElementById('graficaTurnoTickets');
    if (canvasTurno) {
        // Destruimos la instancia anterior si existe
        if (turnoChartInstance) {
            turnoChartInstance.destroy();
        }
        turnoChartInstance = new Chart(canvasTurno.getContext('2d'), {
            type: 'bar',
            data: {
                labels: data.stacked_bar_labels,
                datasets: data.stacked_bar_datasets
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'top' } },
                scales: { x: { stacked: true }, y: { stacked: true } }
                // La función de click se podría añadir aquí
            }
        });
    }
});