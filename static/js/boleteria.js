// ======================================================
// BOLETERIA.JS – VERSION FINAL ESTABLE
// Pago simple / combinado + impresión + UI en vivo
// ======================================================

document.addEventListener("DOMContentLoaded", () => {

  /* =========================
     UTILIDADES
  ========================= */
  const $ = id => document.getElementById(id);

  const formatoMoneda = v =>
    new Intl.NumberFormat("es-AR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(v || 0);

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
  const entradasSpan   = $("entradasVendidas");

  let pagosMixtos = [];
  let pagoMixtoConfirmado = false;

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
    if (togglePagoCombinado.checked) {
      selectModoPago.disabled = true;
      abrirPagoMixto();
    } else {
      selectModoPago.disabled = false;
      pagosMixtos = [];
      pagoMixtoConfirmado = false;
    }
  });

  /* ===============================
     BOTÓN VENDER
  =============================== */
  btnVender.addEventListener("click", () => {

    if (!sectorSelect.value) {
      alert("⚠️ Seleccione un sector");
      return;
    }

    if (cantidadInput.value <= 0) {
      alert("⚠️ Cantidad inválida");
      return;
    }

    if (togglePagoCombinado.checked && !pagoMixtoConfirmado) {
      abrirPagoMixto();
      return;
    }

    registrarVenta();
  });

  /* ===============================
     PAGO COMBINADO (MODAL)
  =============================== */
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
        <input type="number"
               class="form-control form-control-sm montoPago"
               min="0">
      </div>
    `;
    $("pagosContainer").appendChild(div);
  }

  $("btnAgregarPago")?.addEventListener("click", agregarFilaPago);

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

    if (suma !== calcularTotal()) {
      alert("❌ Los montos no coinciden con el total");
      return;
    }

    pagoMixtoConfirmado = true;
    bootstrap.Modal.getInstance($("modalPagos")).hide();
    registrarVenta();
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

    if (togglePagoCombinado.checked) {
      payload.pagos_mixtos = pagosMixtos;
    } else {
      payload.modopago = selectModoPago.value;
    }

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

      // 🔄 ACTUALIZAR RESUMEN EN VIVO
      recaudacionSpan.textContent =
        formatoMoneda(
          parseFloat(recaudacionSpan.textContent.replace(/\./g, "").replace(",", ".")) + totalVenta
        );

      entradasSpan.textContent =
        parseInt(entradasSpan.textContent) + payload.cantidad;

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
  }

});

/* ===============================
   IMPRIMIR TICKET (SEGURO)
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
      iframe.contentWindow.focus();
      iframe.contentWindow.print();

      setTimeout(() => {
        document.body.removeChild(iframe);
        resolve();
      }, 800);
    };
  });
}
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
