// ======================================================
// BOLETERIA.JS – VERSIÓN FINAL LIMPIA Y FUNCIONAL
// Pago simple / combinado + impresión + UI en vivo
// ======================================================

document.addEventListener("DOMContentLoaded", () => {

  /* =========================
     UTILIDADES
  ========================= */
  const $ = id => document.getElementById(id);

  const formatoMoneda = v =>
    new Intl.NumberFormat("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v || 0);

  /* =========================
     REFERENCIAS
  ========================= */
  const clienteInput   = $("clienteInput");
  const listaClientes  = $("listaClientes");
  const idclienteInput = $("idcliente");

  const sectorSelect   = $("sector");
  const cantidadInput  = $("cantidad");
  const totalSpan      = $("total");
  const btnVender      = $("venderEntrada");
  const idjornadaInput = $("idjornada");

  const selectModoPago      = $("modopago");
  const togglePagoCombinado = $("togglePagoCombinado");

  const recaudacionSpan = $("recaudacionActual");
  const entradasSpan    = $("entradasVendidas");

  let pagosMixtos = [];
  let pagoMixtoConfirmado = false;
  let modalPagosInstance = null;

  /* ===============================
     AUTOCOMPLETE CLIENTES
  =============================== */
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
      console.error("Error clientes:", err);
    }
  });

  /* ===============================
     CALCULAR TOTAL
  =============================== */
  function calcularTotal() {
    const option   = sectorSelect.options[sectorSelect.selectedIndex];
    const precio   = option ? parseFloat(option.dataset.precio || 0) : 0;
    const cantidad = parseInt(cantidadInput.value || 0);
    const total = precio * cantidad;
    totalSpan.textContent = formatoMoneda(total);
    return total;
  }

  sectorSelect.addEventListener("change", calcularTotal);
  cantidadInput.addEventListener("input", calcularTotal);

  /* ===============================
     TOGGLE PAGO COMBINADO
  =============================== */
  togglePagoCombinado?.addEventListener("change", () => {
    selectModoPago.disabled = togglePagoCombinado.checked;
    pagosMixtos = [];
    pagoMixtoConfirmado = false;
    $("pagosContainer").innerHTML = "";
    $("totalPagos") && ($("totalPagos").textContent = formatoMoneda(0));

    if (togglePagoCombinado.checked) abrirPagoMixto();
  });

  /* ===============================
     BOTÓN VENDER
  =============================== */
  btnVender.addEventListener("click", () => {

    if (!sectorSelect.value) return alert("⚠️ Seleccione un sector");
    if (cantidadInput.value <= 0) return alert("⚠️ Cantidad inválida");

    if (togglePagoCombinado.checked && !pagoMixtoConfirmado) {
      return alert("⚠️ Complete el pago combinado en el modal");
    }

    registrarVenta();
  });

  /* ===============================
     PAGO COMBINADO (MODAL)
  =============================== */
  function abrirPagoMixto() {
    const container = $("pagosContainer");
    container.innerHTML = "";
    agregarFilaPago();
    $("totalVentaModal").textContent = formatoMoneda(calcularTotal());

    if (!modalPagosInstance) modalPagosInstance = new bootstrap.Modal($("modalPagos"));
    modalPagosInstance.show();
  }

  function agregarFilaPago() {
    const container = $("pagosContainer");

    const div = document.createElement("div");
    div.className = "row g-2 mb-2";

    div.innerHTML = `
      <div class="col-7">
        <select class="form-select form-select-sm medioPago">
          ${selectModoPago.innerHTML}
        </select>
      </div>
      <div class="col-5">
        <input type="number"
               class="form-control form-control-sm montoPago"
               min="0"
               value="0">
      </div>
    `;
    container.appendChild(div);

    div.querySelector(".montoPago").addEventListener("input", actualizarTotalPagos);
  }

  $("btnAgregarPago")?.addEventListener("click", agregarFilaPago);

  function actualizarTotalPagos() {
    const montos = document.querySelectorAll("#pagosContainer .montoPago");
    let suma = 0;
    montos.forEach(m => suma += parseFloat(m.value || 0));
    $("totalPagos").textContent = formatoMoneda(suma);
  }

  $("confirmarPagos")?.addEventListener("click", () => {
    pagosMixtos = [];
    let suma = 0;

    document.querySelectorAll("#pagosContainer .row").forEach(r => {
      const medio = r.querySelector(".medioPago").value;
      const monto = parseFloat(r.querySelector(".montoPago").value || 0);
      if (monto > 0) {
        pagosMixtos.push({ medio, monto });
        suma += monto;
      }
    });

    const totalVenta = calcularTotal();
    if (Math.round(suma * 100) / 100 !== Math.round(totalVenta * 100) / 100) {
      return alert("❌ Los montos no coinciden con el total");
    }

    pagoMixtoConfirmado = true;

    // ✅ Solo cerrar modal, no registrar venta
    modalPagosInstance.hide();
  });

  /* ===============================
     REGISTRAR VENTA
  =============================== */
  async function registrarVenta() {
    btnVender.disabled = true;

    const totalVenta = calcularTotal();
    const payload = {
      idcliente: idclienteInput.value,
      idsector: sectorSelect.value,
      cantidad: parseInt(cantidadInput.value),
      total: totalVenta,
      idjornada: idjornadaInput.value
    };

    if (togglePagoCombinado.checked) payload.pagos_mixtos = pagosMixtos;
    else payload.modopago = selectModoPago.value;

    try {
      const res = await fetch("/registrar_venta_entrada", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!data.ok) {
        alert("❌ " + data.msg);
        btnVender.disabled = false;
        return;
      }

      // ========================
      // Actualizar resumen en vivo
      // ========================
      const actualRecaudacion = parseFloat(
        recaudacionSpan.textContent.replace(/\./g, "").replace(",", ".")
      ) || 0;

      recaudacionSpan.textContent = formatoMoneda(actualRecaudacion + totalVenta);

      const actualEntradas = parseInt(entradasSpan.textContent.replace(/\D/g, "")) || 0;
      entradasSpan.textContent = actualEntradas + payload.cantidad;

      await imprimirTicket(data.idventa);
      actualizarRecaudacion(payload.total);
      resetearFormulario();
    } catch (err) {
      console.error("Error venta:", err);
      alert("❌ Error al registrar la venta");
    }

    btnVender.disabled = false;
  }

  /* ===============================
     RESET FORMULARIO
  =============================== */
  function resetearFormulario() {
    sectorSelect.selectedIndex = 0;
    cantidadInput.value = 1;
    calcularTotal();

    clienteInput.value = "";
    idclienteInput.value = "1";
    listaClientes.innerHTML = "";

    selectModoPago.selectedIndex = 0;
    selectModoPago.disabled = false;
    togglePagoCombinado.checked = false;

    pagosMixtos = [];
    pagoMixtoConfirmado = false;

    $("pagosContainer").innerHTML = "";
    $("totalPagos") && ($("totalPagos").textContent = formatoMoneda(0));
  }

});

/* ===============================
   IMPRIMIR TICKET
=============================== */
function imprimirTicket(idventa) {
  return new Promise(resolve => {
    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "0";
    iframe.src = `/ticket_entrada/${idventa}`;
    document.body.appendChild(iframe);

    iframe.onload = () => {
      // ✅ Solo imprimir una vez, sin focus
      iframe.contentWindow.print();

      setTimeout(() => {
        document.body.removeChild(iframe);
        resolve();
      }, 500);
    };
  });
}

/* ===============================
   ACTUALIZAR RECAUDACION
=============================== */
function actualizarRecaudacion(monto) {
  const span = document.getElementById("recaudacionParcial");
  if (!span) return;
  const actual = parseFloat(span.dataset.valor || 0);
  const nuevoTotal = actual + monto;
  span.dataset.valor = nuevoTotal;
  span.textContent = new Intl.NumberFormat("es-AR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(nuevoTotal);
}
