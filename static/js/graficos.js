document.addEventListener("DOMContentLoaded", function () {

    let chart = null;

    function cargarGrafico(idjornada = "", idpunto = "") {

        let url = "/ventas_por_punto";

        if (idjornada) {
            url += "?idjornada=" + idjornada;
        }

        console.log("Consultando:", url);

        fetch(url)
            .then(response => response.json())
            .then(data => {

                console.log("Datos recibidos:", data);

                const labels = data.map(d => d.punto);
                const valores = data.map(d => Number(d.total));

                const canvas = document.getElementById("graficoVentas");
                if (!canvas) {
                    console.error("No se encontró el canvas");
                    return;
                }

                const ctx = canvas.getContext("2d");

                if (chart) {
                    chart.destroy();
                }

                chart = new Chart(ctx, {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Total vendido ($)",
                            data: valores,
                            backgroundColor: "#198754"
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });

                // ===================== RESUMEN =====================
                const total = valores.reduce((a, b) => a + b, 0);
                document.getElementById("totalVendido").innerText =
                    "$ " + total.toFixed(2);

                document.getElementById("cantidadVentas").innerText =
                    valores.length;

                if (valores.length > 0) {
                    const max = Math.max(...valores);
                    const index = valores.indexOf(max);
                    document.getElementById("mejorPunto").innerText =
                        labels[index];
                } else {
                    document.getElementById("mejorPunto").innerText = "-";
                }

            })
            .catch(err => {
                console.error("Error cargando gráfico:", err);
            });
    }

    // ===================== BOTÓN FILTRAR =====================
    const btn = document.getElementById("btnFiltrar");

    if (btn) {
        btn.addEventListener("click", function () {
            const jornada = document.getElementById("filtroJornada").value;
            const punto = document.getElementById("filtroPunto").value;

            console.log("Filtro aplicado:", jornada, punto);
            cargarGrafico(jornada, punto);
        });
    } else {
        console.error("No se encontró el botón Filtrar");
    }

    // ===================== CARGA INICIAL =====================
    cargarGrafico();

});
