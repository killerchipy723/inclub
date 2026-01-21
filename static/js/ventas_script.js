document.addEventListener("DOMContentLoaded", () => {

  // ================= FORMATO MONEDA =================
  function formatoMoneda(valor) {
    return new Intl.NumberFormat("es-AR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(valor);
  }

  // ================= CARRITO =================
  let carrito = [];

  function actualizarCarrito() {
    const tbody = document.querySelector("#carritoTable tbody");
    tbody.innerHTML = "";

    let total = 0;

    carrito.forEach((item, index) => {
      const subtotal = item.cortesia ? 0 : item.precio * item.cantidad;
      total += subtotal;

      tbody.innerHTML += `
        <tr>
          <td>${item.nombre}</td>

          <td>
            <input type="number"
                   class="form-control form-control-sm cantidad"
                   data-index="${index}"
                   value="${item.cantidad}"
                   min="1">
          </td>

          <td class="text-end">$ ${formatoMoneda(item.precio)}</td>

          <td class="text-end">$ ${formatoMoneda(subtotal)}</td>

          <td class="text-center">
            <input type="checkbox"
                   class="form-check-input cortesia"
                   data-index="${index}"
                   ${item.cortesia ? "checked" : ""}>
          </td>

          <td>
            <button class="btn btn-danger btn-sm eliminar"
                    data-index="${index}">
              ✕
            </button>
          </td>
        </tr>
      `;
    });

    document.getElementById("total").textContent = formatoMoneda(total);
  }

  // ================= AGREGAR PRODUCTOS =================
  document.querySelectorAll(".agregar").forEach(btn => {
    btn.addEventListener("click", e => {
      const card = e.target.closest(".producto-card");

      const id = card.dataset.id;
      const nombre = card.dataset.nombre;
      const precio = parseFloat(card.dataset.precio);

      const existente = carrito.find(p => p.id == id);

      if (existente) {
        existente.cantidad++;
      } else {
        carrito.push({
          id: id,
          nombre: nombre,
          precio: precio,
          cantidad: 1,
          cortesia: false
        });
      }

      actualizarCarrito();
    });
  });

  // ================= CAMBIOS EN CARRITO =================
  document.querySelector("#carritoTable").addEventListener("input", e => {
    const index = e.target.dataset.index;

    if (e.target.classList.contains("cantidad")) {
      carrito[index].cantidad = parseInt(e.target.value) || 1;
    }

    if (e.target.classList.contains("cortesia")) {
      carrito[index].cortesia = e.target.checked;
    }

    actualizarCarrito();
  });

  document.querySelector("#carritoTable").addEventListener("click", e => {
    if (e.target.classList.contains("eliminar")) {
      carrito.splice(e.target.dataset.index, 1);
      actualizarCarrito();
    }
  });

  // ================= COBRAR =================
  document.getElementById("procesarVenta").addEventListener("click", async () => {

    if (carrito.length === 0) {
      alert("Debe agregar al menos un producto");
      return;
    }

    let idcliente = document.getElementById("idcliente").value || "1";

    const formData = new FormData();
    formData.append("cliente", idcliente);
    formData.append("modopago", document.getElementById("modopago").value);
    formData.append("total", document.getElementById("total").textContent);

    carrito.forEach(p => {
      formData.append("productos[]", p.id);
      formData.append("cantidades[]", p.cantidad);
      formData.append("precios[]", p.precio);

      // 🔹 IMPORTANTE: enviar cortesía como 1 / 0
      formData.append("cortesias[]", p.cortesia ? "1" : "0");
    });

    const res = await fetch("/registrar_venta", {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (!data.success) {
      alert("Error al registrar la venta");
      return;
    }

    imprimirTicket(data.idventa);
    resetearVenta();
    actualizarRecaudacionCaja()

  });

  // ================= IMPRIMIR =================
  function imprimirTicket(idventa) {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = `/ticket/${idventa}`;
    document.body.appendChild(iframe);
  }

  // ================= RESET VENTA =================
  function resetearVenta() {
    carrito = [];
    actualizarCarrito();

    document.getElementById("clienteInput").value = "Consumidor Final";
    document.getElementById("idcliente").value = "1";
    document.getElementById("modopago").selectedIndex = 0;
    document.getElementById("listaClientes").innerHTML = "";
  }

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

});

// Actualiza recaudacion por punto de ventas
async function actualizarRecaudacionCaja() {
  const res = await fetch("/recaudacion_actual");
  const data = await res.json();

  const total = new Intl.NumberFormat("es-AR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(data.total);

  const div = document.getElementById("recaudacionCaja");
  if (div) {
    div.innerHTML = `💰 Recaudación Parcial: $ ${total}`;
  }
}

document.getElementById("cerrarCaja").addEventListener("click", async () => {

    if (!confirm("¿Confirmar cierre de caja?")) return;

    const res = await fetch("/cerrar_caja", { method: "POST" });
    const data = await res.json();

    if (data.ok) {
        alert("✅ Caja cerrada correctamente\nTotal: $" + data.total);
        location.reload();
    } else {
        alert("❌ " + data.msg);
    }
});

