// static/js/dashboard_charts.js

// Guardamos las instancias de las gráficas para poder actualizarlas
let estadoChart;
let turnoChart;

function crearOActualizarGraficas(data) {
    // --- Gráfica de Estados ---
    const ctxEstado = document.getElementById('graficaEstadoTickets').getContext('2d');
    if (estadoChart) {
        // Si la gráfica ya existe, solo actualizamos sus datos
        estadoChart.data.labels = data.estado_labels;
        estadoChart.data.datasets[0].data = data.estado_data;
        estadoChart.update();
    } else {
        // Si no existe, la creamos
        estadoChart = new Chart(ctxEstado, {
            type: 'doughnut',
            data: {
                labels: data.estado_labels,
                datasets: [{
                    label: 'Tickets por Estado',
                    data: data.estado_data,
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'top' } } }
        });
    }

    // --- Gráfica de Turnos (puedes añadirla aquí) ---
    // ... Lógica similar para una segunda gráfica ...
}