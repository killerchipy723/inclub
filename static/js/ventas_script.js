document.addEventListener("DOMContentLoaded", () => {

  console.log("JS VENTAS CARGADO");

  // ================= FORMATO MONEDA =================
  function formatoMoneda(valor) {
    return new Intl.NumberFormat('es-AR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(valor);
  }

  // ================= CARRITO =================
  const carrito = [];
  const tbody = document.querySelector("#carritoTable tbody");
  const totalSpan = document.getElementById("total");

  function actualizarCarrito() {
    tbody.innerHTML = "";
    let total = 0;

    carrito.forEach((item, index) => {
      const subtotal = item.cortesia ? 0 : item.precio * item.cantidad;
      total += subtotal;

      tbody.innerHTML += `
        <tr>
          <td>${item.nombre}</td>
          <td>
            <input type="number" class="form-control form-control-sm cantidad"
              data-index="${index}" value="${item.cantidad}" min="1">
          </td>
          <td>${formatoMoneda(item.precio)}</td>
          <td>${formatoMoneda(subtotal)}</td>
          <td>
            <input type="checkbox" class="cortesia"
              data-index="${index}" ${item.cortesia ? "checked" : ""}>
          </td>
          <td>
            <button class="btn btn-danger btn-sm eliminar" data-index="${index}">X</button>
          </td>
        </tr>
      `;
    });

    totalSpan.textContent = formatoMoneda(total);
  }

  // ================= AGREGAR PRODUCTO =================
  document.querySelectorAll(".agregar").forEach(btn => {
    btn.addEventListener("click", e => {
      const card = e.target.closest(".producto-card");
      const id = card.dataset.id;
      const nombre = card.dataset.nombre;
      const precio = parseFloat(card.dataset.precio);

      const existente = carrito.find(p => p.id === id);
      if (existente) {
        existente.cantidad++;
      } else {
        carrito.push({ id, nombre, precio, cantidad: 1, cortesia: false });
      }

      actualizarCarrito();
    });
  });

  // ================= CAMBIOS EN TABLA =================
  document.getElementById("carritoTable").addEventListener("input", e => {
    const index = e.target.dataset.index;
    if (e.target.classList.contains("cantidad")) {
      carrito[index].cantidad = parseInt(e.target.value);
    }
    if (e.target.classList.contains("cortesia")) {
      carrito[index].cortesia = e.target.checked;
    }
    actualizarCarrito();
  });

  document.getElementById("carritoTable").addEventListener("click", e => {
    if (e.target.classList.contains("eliminar")) {
      carrito.splice(e.target.dataset.index, 1);
      actualizarCarrito();
    }
  });

  // ================= COBRAR =================
  const btnCobrar = document.getElementById("procesarVenta");

  btnCobrar.addEventListener("click", async () => {

    if (carrito.length === 0) {
      alert("Seleccione al menos un producto");
      return;
    }

    const formData = new FormData();
    formData.append("cliente", document.getElementById("idcliente").value || 1);
    formData.append("modopago", document.getElementById("modopago").value);
    formData.append("total", totalSpan.textContent);

    carrito.forEach(item => {
      formData.append("productos[]", item.id);
      formData.append("cantidades[]", item.cantidad);
      formData.append("precios[]", item.precio);
      formData.append("cortesias[]", item.cortesia);
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

    // imprimir ticket
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = `/ticket/${data.idventa}`;
    document.body.appendChild(iframe);

    iframe.onload = () => {
      iframe.contentWindow.print();
      setTimeout(() => iframe.remove(), 1500);
    };

    carrito.length = 0;
    actualizarCarrito();
  });

  // ================= BUSCAR CLIENTES =================
  const clienteInput = document.getElementById("clienteInput");
  const listaClientes = document.getElementById("listaClientes");
  const idclienteInput = document.getElementById("idcliente");

  clienteInput.addEventListener("input", async () => {
    const q = clienteInput.value.trim();
    listaClientes.innerHTML = "";
    idclienteInput.value = 0;
    if (q.length < 2) return;

    const res = await fetch(`/buscar_clientes?q=${q}`);
    const clientes = await res.json();

    clientes.forEach(c => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "list-group-item list-group-item-action";
      btn.textContent = c.apenomb;
      btn.onclick = () => {
        clienteInput.value = c.apenomb;
        idclienteInput.value = c.idclientes;
        listaClientes.innerHTML = "";
      };
      listaClientes.appendChild(btn);
    });
  });

});
