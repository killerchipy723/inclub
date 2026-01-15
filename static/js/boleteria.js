document.addEventListener("DOMContentLoaded", () => {

    const clienteInput = document.getElementById("cliente");
    const clienteList = document.getElementById("clientes-list");
    const sectorSelect = document.getElementById("sector");
    const precioInput = document.getElementById("precio");

    // ================= AUTOCOMPLETE CLIENTES =================
    clienteInput.addEventListener("keyup", async () => {

        const q = clienteInput.value.trim();
        if (q.length < 2) {
            clienteList.innerHTML = "";
            return;
        }

        const res = await fetch(`/api/clientes?q=${q}`);
        const data = await res.json();

        clienteList.innerHTML = "";

        data.forEach(c => {
            const item = document.createElement("div");
            item.classList.add("list-group-item", "list-group-item-action");
            item.textContent = `${c.nombre} - DNI ${c.dni}`;
            item.onclick = () => {
                clienteInput.value = c.nombre;
                clienteList.innerHTML = "";
            };
            clienteList.appendChild(item);
        });
    });

    // ================= SECTOR → PRECIO =================
    sectorSelect.addEventListener("change", () => {
        const option = sectorSelect.options[sectorSelect.selectedIndex];
        const precio = option.dataset.precio || 0;
        precioInput.value = precio;
    });

});

// ================= AUTOCOMPLETE CLIENTES =================
  const clienteInput = document.getElementById("clienteInput");
  const listaClientes = document.getElementById("listaClientes");
  const idclienteInput = document.getElementById("idcliente");

  clienteInput.addEventListener("input", async () => {
    const q = clienteInput.value.trim();
    listaClientes.innerHTML = "";
    idclienteInput.value = "1";

    if (q.length < 2) return;

    const res = await fetch(`/buscar_clientes?q=${q}`);
    const clientes = await res.json();

    clientes.forEach(c => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "list-group-item list-group-item-action";
      btn.textContent = `${c.apenomb} – DNI ${c.dni}`;
      btn.onclick = () => {
        clienteInput.value = c.apenomb;
        idclienteInput.value = c.idclientes;
        listaClientes.innerHTML = "";
      };
      listaClientes.appendChild(btn);
    });
  });

// VENTA DE ENTRADAS
document.addEventListener("DOMContentLoaded", () => {

    const sectorSelect = document.getElementById("sector");
    const cantidadInput = document.getElementById("cantidad");
    const totalSpan = document.getElementById("total");
    const btnVender = document.getElementById("venderEntrada");

    // ===============================
    // CALCULAR TOTAL
    // ===============================
    function calcularTotal() {
        const option = sectorSelect.options[sectorSelect.selectedIndex];
        const precio = option ? parseFloat(option.dataset.precio || 0) : 0;
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

        const idcliente = document.getElementById("idcliente").value;
        const idsector = sectorSelect.value;
        const cantidad = cantidadInput.value;
        const idjornada = document.getElementById("idjornada").value;
        const total = calcularTotal();

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
                alert("🎟 Venta registrada correctamente");
                location.reload();
            } else {
                alert("❌ " + resp.msg);
            }
        })
        .catch(err => {
            console.error(err);
            alert("❌ Error al registrar la venta");
        });
    });

});
