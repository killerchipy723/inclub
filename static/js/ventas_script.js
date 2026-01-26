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
     REFERENCIAS
  ===================================================== */
  const togglePagoCombinado = $("togglePagoCombinado");
  const selectModoPago = $("modopago");

  let carrito = [];
  let pagosMixtos = [];
  let pagoMixtoConfirmado = false;

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
        btnCobrar.disabled = false;
      } else {
        badge.textContent = "Caja Cerrada";
        badge.className = "badge bg-danger ms-2";
        btnCobrar.disabled = true;
      }
    } catch {
      badge.textContent = "Caja Cerrada";
      badge.className = "badge bg-danger ms-2";
      btnCobrar.disabled = true;
    }
  }

  verificarEstadoCaja();

  /* =====================================================
     CARRITO
  ===================================================== */
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
            <input type="number" class="form-control form-control-sm cantidad"
                   data-index="${i}" min="1" value="${p.cantidad}">
          </td>
          <td class="text-end">$ ${formatoMoneda(p.precio)}</td>
          <td class="text-end">$ ${formatoMoneda(subtotal)}</td>
          <td class="text-center">
            <input type="checkbox" class="form-check-input cortesia"
                   data-index="${i}" ${p.cortesia ? "checked" : ""}>
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

    $("total").textContent = formatoMoneda(calcularTotal());
  }

  /* =====================================================
     AGREGAR PRODUCTOS
  ===================================================== */
  document.querySelectorAll(".agregar").forEach(btn => {
    btn.addEventListener("click", e => {
      const card = e.target.closest(".producto-card");
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

      if (e.target.checked) {
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
     TOGGLE PAGO COMBINADO
  ===================================================== */
  togglePagoCombinado?.addEventListener("change", () => {
    if (togglePagoCombinado.checked) {
      selectModoPago.disabled = true;
      abrirPagoMixto();
    } else {
      selectModoPago.disabled = false;
      pagoMixtoConfirmado = false;
    }
  });

  /* =====================================================
     COBRAR
  ===================================================== */
  $("procesarVenta")?.addEventListener("click", () => {
    if (!carrito.length) {
      alert("Debe agregar productos");
      return;
    }

    if (togglePagoCombinado?.checked && !pagoMixtoConfirmado) {
      abrirPagoMixto();
      return;
    }

    registrarVenta(new FormData());
  });

  /* =====================================================
     PAGO MIXTO
  ===================================================== */
  function abrirPagoMixto() {
    $("pagosContainer").innerHTML = "";
    $("totalVentaModal").textContent = formatoMoneda(calcularTotal());
    agregarFilaPago();
    new bootstrap.Modal($("modalPagos")).show();
  }

  function agregarFilaPago() {
    const div = document.createElement("div");
    div.className = "row g-2 mb-2";
    div.innerHTML = `
      <div class="col-7">
        <select class="form-select form-select-sm medioPago">
          ${selectModoPago.innerHTML}
        </select>
      </div>
      <div class="col-5">
        <input type="number" class="form-control form-control-sm montoPago" min="0">
      </div>
    `;
    $("pagosContainer").appendChild(div);
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

    pagoMixtoConfirmado = true;
    bootstrap.Modal.getInstance($("modalPagos")).hide();
    registrarVenta(fd);
  });

  /* =====================================================
     REGISTRAR VENTA
  ===================================================== */
  async function registrarVenta(fd) {
    fd.append("cliente", $("idcliente").value);
    fd.append("modopago", selectModoPago.value);
    fd.append("total", calcularTotal());

    carrito.forEach(p => {
      fd.append("productos[]", p.id);
      fd.append("cantidades[]", p.cantidad);
      fd.append("precios[]", p.precio);
      fd.append("cortesias[]", p.cortesia ? 1 : 0);
      fd.append("autorizados[]", p.autorizado || "");
    });

    const res = await fetch("/registrar_venta", { method: "POST", body: fd });
    const data = await res.json();

    if (!data.success) {
      alert(data.msg);
      return;
    }

    imprimirTicket(data.idventa);
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
    pagoMixtoConfirmado = false;

    actualizarCarrito();
    $("clienteInput").value = "Consumidor Final";
    $("idcliente").value = "1";
    selectModoPago.selectedIndex = 0;
    selectModoPago.disabled = false;
    togglePagoCombinado.checked = false;

    $("pagosContainer").innerHTML = "";
    $("totalVentaModal").textContent = "0";
  }

});
