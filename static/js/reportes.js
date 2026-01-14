async function exportarPDF() {

    const response = await fetch("/reporte-json");
    const data = await response.json();

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    /* ==========================
       ENCABEZADO
    ========================== */
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("TicketJets", 14, 20);

    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    doc.text(`Reporte de Ventas`, 14, 28);

    doc.setFontSize(10);
    doc.text(`Jornada: ${data.jornada}`, 14, 36);
    doc.text(`Fecha de emisión: ${data.fecha_emision}`, 14, 42);
    doc.text(`Hora: ${data.hora_emision}`, 14, 48);

    /* ==========================
       TABLA RECAUDACIÓN
    ========================== */
    const filas = data.puntos.map(p => [
        p.punto,
        `$ ${p.total.toLocaleString("es-AR")}`
    ]);

    doc.autoTable({
        startY: 55,
        head: [["Punto de Venta", "Recaudación"]],
        body: filas,
        styles: {
            fontSize: 10,
            halign: "center"
        },
        headStyles: {
            fillColor: [33, 37, 41],
            textColor: 255
        }
    });

    /* ==========================
       TOTAL JORNADA
    ========================== */
    let yFinal = doc.lastAutoTable.finalY + 10;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.text(
        `Total Recaudación Jornada: $ ${data.total_jornada.toLocaleString("es-AR")}`,
        14,
        yFinal
    );

    /* ==========================
       PIE DE PÁGINA
    ========================== */
    doc.setFontSize(9);
    doc.setFont("helvetica", "italic");
    doc.text(
        "Sistema de Gestión TicketJets",
        14,
        285
    );

    doc.save(`reporte_${data.jornada}.pdf`);
}
