function imprimirTicket(idventa) {

    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.right = "0";
    iframe.style.bottom = "0";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "0";
    iframe.src = `/ticket_entrada/${idventa}`;

    document.body.appendChild(iframe);

    iframe.onload = () => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();

        // limpiar iframe después
        setTimeout(() => {
            document.body.removeChild(iframe);
        }, 1000);
    };
}
