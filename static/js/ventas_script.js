document.addEventListener("DOMContentLoaded", () => {

  /* =====================================================
     UTILIDADES
  ===================================================== */
  const $ = id => document.getElementById(id);

  function formatoMoneda(valor) {
    return new Intl.NumberFormat("es-AR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(valor || 0);
  }

  /* =====================================================
     ESTADO DE CAJA
  ===================================================== */
  async function verificarEstadoCaja() {
    const badge = $("estadoCaja");
    const btnCobrar = $("procesarVenta");
    if (!badge) return;

    try {
      const res = await fetch("/estado_caja");
      const data = await res.json();

      if (data.estado === "abierto") {
        badge.textContent = "Caja Abierta";
        badge.className = "badge bg-success ms-2";
        if (btnCobrar) btnCobrar.disabled = false;
      } else {
        badge.textContent = "Caja Cerrada";
        badge.className = "badge bg-danger ms-2";
        if (btnCobrar) btnCobrar.disabled = true;
      }
    } catch {
      badge.textContent = "Caja Cerrada";
      badge.className = "badge bg-danger ms-2";
      if (btnCobrar) btnCobrar.disabled = true;
    }
  }

  verificarEstadoCaja();

  /* =====================================================
     CARRITO
  ===================================================== */
  let carrito = [];
  let pagosMixtos = [];

  function calcularTotal() {
    return carrito.reduce((acc, p) =>
      acc + (p.cortesia ? 0 : p.precio * p.cantidad), 0
    );
  }

  function actualizarCarrito() {
    const tbody = document.querySelector("#carritoTable tbody");
    const inputsOcultos = $("inputsOcultos");
    if (!tbody) return;

    tbody.innerHTML = "";
    if (inputsOcultos) inputsOcultos.innerHTML = "";

    carrito.forEach((p, i) => {
      const subtotal = p.cortesia ? 0 : p.precio * p.cantidad;

      tbody.insertAdjacentHTML("beforeend", `
        <tr>
          <td>${p.nombre}</td>
          <td>
            <input type="number"
                   class="form-control form-control-sm cantidad"
                   data-index="${i}"
                   min="1"
                   value="${p.cantidad}">
          </td>
          <td class="text-end">$ ${formatoMoneda(p.precio)}</td>
          <td class="text-end">$ ${formatoMoneda(subtotal)}</td>
          <td class="text-center">
            <input type="checkbox"
                   class="form-check-input cortesia"
                   data-index="${i}"
                   ${p.cortesia ? "checked" : ""}>
          </td>
          <td>
            <button class="btn btn-danger btn-sm eliminar"
                    data-index="${i}">✕</button>
          </td>
        </tr>
      `);

      if (inputsOcultos) {
        inputsOcultos.insertAdjacentHTML("beforeend", `
          <input type="hidden" name="cortesias[]" value="${p.cortesia ? 1 : 0}">
          <input type="hidden" name="autorizados[]" value="${p.autorizado || ""}">
        `);
      }
    });

    if ($("total")) $("total").textContent = formatoMoneda(calcularTotal());
  }

  /* =====================================================
     AGREGAR PRODUCTOS
  ===================================================== */
  document.querySelectorAll(".agregar").forEach(btn => {
    btn.addEventListener("click", e => {
      const card = e.target.closest(".producto-card");
      if (!card) return;

      const id = card.dataset.id;
      let prod = carrito.find(p => p.id == id);

      if (prod) {
        prod.cantidad++;
      } else {
        carrito.push({
          id,
          nombre: card.dataset.nombre,
          precio: parseFloat(card.dataset.precio),
          cantidad: 1,
          cortesia: false,
          autorizado: ""
        });
      }

      actualizarCarrito();
    });
  });

  /* =====================================================
     EVENTOS CARRITO
  ===================================================== */
  $("carritoTable")?.addEventListener("input", e => {
    const i = e.target.dataset.index;
    if (i === undefined) return;

    if (e.target.classList.contains("cantidad")) {
      carrito[i].cantidad = parseInt(e.target.value) || 1;
    }

    if (e.target.classList.contains("cortesia")) {
      carrito[i].cortesia = e.target.checked;

      if (e.target.checked && $("modalCortesia")) {
        $("guardarAutorizacion").dataset.index = i;
        new bootstrap.Modal($("modalCortesia")).show();
      } else {
        carrito[i].autorizado = "";
      }
    }

    actualizarCarrito();
  });

  $("carritoTable")?.addEventListener("click", e => {
    if (e.target.classList.contains("eliminar")) {
      carrito.splice(e.target.dataset.index, 1);
      actualizarCarrito();
    }
  });

  /* =====================================================
     AUTOCOMPLETE CLIENTES
  ===================================================== */
  const clienteInput = $("clienteInput");
  const listaClientes = $("listaClientes");
  const idclienteInput = $("idcliente");

  clienteInput?.addEventListener("input", async () => {
    const q = clienteInput.value.trim();

    listaClientes.innerHTML = "";
    idclienteInput.value = "1";

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
          idclienteInput.value = c.idclientes;
          listaClientes.innerHTML = "";
        };

        listaClientes.appendChild(btn);
      });
    } catch (err) {
      console.error("Error buscando clientes:", err);
    }
  });

  /* =====================================================
     AUTORIZACION CORTESIA
  ===================================================== */
  $("guardarAutorizacion")?.addEventListener("click", () => {
    const i = $("guardarAutorizacion").dataset.index;
    const nombre = $("autorizadoInput")?.value.trim();

    if (!nombre) {
      alert("Ingrese nombre");
      return;
    }

    carrito[i].autorizado = nombre;
    $("autorizadoInput").value = "";
    bootstrap.Modal.getInstance($("modalCortesia"))?.hide();
    actualizarCarrito();
  });

  // ================= ACTUALIZAR RECAUDACION =================
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

  /* =====================================================
     COBRAR
  ===================================================== */
  $("procesarVenta")?.addEventListener("click", () => {
    if (!carrito.length) {
      alert("Debe agregar productos");
      return;
    }

    const modo = $("modopago")?.selectedOptions[0]?.text.toUpperCase();

    if (modo === "MIXTO") {
      abrirPagoMixto();
    } else {
      registrarVenta(new FormData());
      actualizarRecaudacionCaja() 
    }
  });

  /* =====================================================
     PAGO MIXTO
  ===================================================== */
  function abrirPagoMixto() {
    const modal = $("modalPagos");
    const cont = $("pagosContainer");
    const totalSpan = $("totalVentaModal");

    if (!modal || !cont || !totalSpan) {
      alert("Error en modal de pago mixto");
      return;
    }

    cont.innerHTML = "";
    totalSpan.textContent = formatoMoneda(calcularTotal());

    agregarFilaPago();
    new bootstrap.Modal(modal).show();
  }

  function agregarFilaPago() {
    const cont = $("pagosContainer");
    const selectBase = $("modopago");
    if (!cont || !selectBase) return;

    const div = document.createElement("div");
    div.className = "row g-2 mb-2";
    div.innerHTML = `
      <div class="col-7">
        <select class="form-select form-select-sm medioPago">
          ${selectBase.innerHTML}
        </select>
      </div>
      <div class="col-5">
        <input type="number"
               class="form-control form-control-sm montoPago"
               min="0">
      </div>
    `;
    cont.appendChild(div);
  }

  $("btnAgregarPago")?.addEventListener("click", agregarFilaPago);

  $("confirmarPagos")?.addEventListener("click", () => {
    let suma = 0;
    let pagos = [];

    document.querySelectorAll("#pagosContainer .row").forEach(r => {
      const medio = r.querySelector(".medioPago").value;
      const monto = parseFloat(r.querySelector(".montoPago").value || 0);

      if (monto > 0) {
        suma += monto;
        pagos.push({ medio, monto });
      }
    });

    if (suma !== calcularTotal()) {
      alert("Los montos no coinciden con el total");
      return;
    }

    const fd = new FormData();
    fd.append("pagos_mixtos", JSON.stringify(pagos));

    bootstrap.Modal.getInstance($("modalPagos"))?.hide();
    registrarVenta(fd);
  });

  /* =====================================================
     REGISTRAR VENTA
  ===================================================== */
  async function registrarVenta(fd) {
    fd.append("cliente", $("idcliente")?.value || 1);
    fd.append("modopago", $("modopago")?.value);
    fd.append("total", calcularTotal());

    carrito.forEach(p => {
      fd.append("productos[]", p.id);
      fd.append("cantidades[]", p.cantidad);
      fd.append("precios[]", p.precio);
      fd.append("cortesias[]", p.cortesia ? 1 : 0);
      fd.append("autorizados[]", p.autorizado || "");
    });

    const res = await fetch("/registrar_venta", {
      method: "POST",
      body: fd
    });

    const data = await res.json();
    if (!data.success) {
      alert(data.msg);
      return;
    }

    imprimirTicket(data.idventa);
    actualizarRecaudacionCaja(); 
    resetearVenta();
  }

  function imprimirTicket(id) {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = `/ticket/${id}`;
    document.body.appendChild(iframe);
    iframe.onload = () => iframe.contentWindow.print();
  }

  function resetearVenta() {
    carrito = [];
    pagosMixtos = [];

    actualizarCarrito();

    if ($("clienteInput")) $("clienteInput").value = "Consumidor Final";
    if ($("idcliente")) $("idcliente").value = "1";
    if ($("modopago")) $("modopago").selectedIndex = 0;

    if ($("pagosContainer")) $("pagosContainer").innerHTML = "";
    if ($("totalVentaModal")) $("totalVentaModal").textContent = "0";
  }

    /* =====================================================
     CERRAR CAJA
  ===================================================== */
    window.cerrarCaja = async function cerrarCaja() {
    if (!confirm("¿Confirmar cierre de caja?")) return;

    try {
      const res = await fetch("/cerrar_caja", { method: "POST" });
      const data = await res.json();

      if (!data.ok) {
        alert(data.msg || "Error al cerrar caja");
        return;
      }

      imprimirCierreCaja();
      verificarEstadoCaja();

    } catch (error) {
      console.error("Error cerrando caja:", error);
      alert("Error de comunicación con el servidor");
    }
  };


  function imprimirCierreCaja() {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = "/ticket_cierre_caja";
    document.body.appendChild(iframe);
    iframe.onload = () => iframe.contentWindow.print();
  }


});


