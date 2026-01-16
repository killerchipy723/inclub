// ======================================================
// BOLETERIA.JS – VERSION LIMPIA Y FUNCIONAL
// ======================================================

document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // ELEMENTOS
    // =========================
    const clienteInput   = document.getElementById("clienteInput");
    const listaClientes  = document.getElementById("listaClientes");
    const idclienteInput = document.getElementById("idcliente");

    const sectorSelect   = document.getElementById("sector");
    const cantidadInput  = document.getElementById("cantidad");
    const totalSpan      = document.getElementById("total");
    const btnVender      = document.getElementById("venderEntrada");

    // ===============================
    // AUTOCOMPLETE CLIENTES
    // ===============================
    clienteInput.addEventListener("input", async () => {

        const q = clienteInput.value.trim();
        listaClientes.innerHTML = "";

        // Si borra el texto → vuelve a Consumidor Final
        if (q.length === 0) {
            idclienteInput.value = "1";
            return;
        }

        if (q.length < 2) return;

        try {
            const res = await fetch(`/buscar_clientes?q=${q}`);
            const clientes = await res.json();

            clientes.forEach(c => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "list-group-item list-group-item-action";
                btn.textContent = `${c.apenomb} – DNI ${c.dni}`;

                btn.onclick = () => {
                    clienteInput.value = c.apenomb;
                    idclienteInput.value = c.idclientes; // ✅ ID REAL
                    listaClientes.innerHTML = "";
                };

                listaClientes.appendChild(btn);
            });

        } catch (error) {
            console.error("Error buscando clientes:", error);
        }
    });

    // ===============================
    // CALCULAR TOTAL
    // ===============================
    function calcularTotal() {
        const option   = sectorSelect.options[sectorSelect.selectedIndex];
        const precio   = option ? parseFloat(option.dataset.precio || 0) : 0;
        const cantidad = parseInt(cantidadInput.value || 0);

        const total = precio * cantidad;

        totalSpan.textContent = total.toLocaleString("es-AR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        return total;
    }

    sectorSelect.addEventListener("change", calcularTotal);
    cantidadInput.addEventListener("input", calcularTotal);

    // ===============================
    // REGISTRAR VENTA
    // ===============================
    btnVender.addEventListener("click", () => {

        const idcliente = idclienteInput.value;
        const idsector  = sectorSelect.value;
        const cantidad  = cantidadInput.value;
        const idjornada = document.getElementById("idjornada").value;
        const total     = calcularTotal();

        // VALIDACIONES
        if (!idsector) {
            alert("⚠️ Seleccione un sector");
            return;
        }

        if (cantidad <= 0) {
            alert("⚠️ Cantidad inválida");
            return;
        }

        const data = {
            idcliente: idcliente,
            idsector: idsector,
            cantidad: cantidad,
            total: total,
            idjornada: idjornada
        };

        console.log("VENTA ENVIADA:", data); // 🧪 DEBUG

        fetch("/registrar_venta_entrada", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(resp => {

            if (resp.ok) {

                // MENSAJE
                alert("🎟 Venta registrada correctamente");

                // IMPRIMIR TICKET
                imprimirTicket(resp.idventa);

                // LIMPIAR FORMULARIO
                sectorSelect.selectedIndex = 0;
                cantidadInput.value = 1;
                calcularTotal();

                clienteInput.value = "";
                idclienteInput.value = "1";
                listaClientes.innerHTML = "";

            } else {
                alert("❌ " + resp.msg);
            }
        })
        .catch(err => {
            console.error("Error venta:", err);
            alert("❌ Error al registrar la venta");
        });
    });
});

// ===============================
// IMPRIMIR TICKET
// ===============================
function imprimirTicket(idventa) {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = "/ticket_entrada/" + idventa;
    document.body.appendChild(iframe);
}
