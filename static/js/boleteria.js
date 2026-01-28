// ======================================================
// BOLETERIA.JS – ESTABLE + CONTROL DE CAJA
// ======================================================

document.addEventListener("DOMContentLoaded", () => {

  const $ = id => document.getElementById(id);
 

  const formatoMoneda = v =>
    new Intl.NumberFormat("es-AR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(v || 0);

  /* =========================
     REFERENCIAS
  ========================= */
  const clienteInput = $("clienteInput");
  const listaClientes = $("listaClientes");
  const idclienteInput = $("idcliente");

  const sectorSelect = $("sector");
  const cantidadInput = $("cantidad");
  const totalSpan = $("total");
  const btnVender = $("venderEntrada");
  const idjornadaInput = $("idjornada");

  const selectModoPago = $("modopago");
  const togglePagoCombinado = $("togglePagoCombinado");

  let pagosMixtos = [];
  let pagoMixtoConfirmado = false;

  /* =========================
     ESTADO DE CAJA
  ========================= */
  async function verificarEstadoBoleteria() {
    const badge = $("estadoCaja");
    const btnCobrar = $("venderEntrada");
    if (!badge) return;

    try {
      const res = await fetch("/estado_caja");
      const data = await res.json();

      if (data.estado === "abierto") {
        badge.textContent = "Boleteria Abierta";
        badge.className = "badge bg-success ms-2";
        btnCobrar.disabled = false;
      } else {
        badge.textContent = "Caja Cerrada";
        badge.className = "badge bg-danger ms-2";
        btnCobrar.disabled = true;
      }
    } catch {
      badge.textContent = "Boleteria Cerrada";
      badge.className = "badge bg-danger ms-2";
      btnCobrar.disabled = true;
    }
  }

  verificarEstadoBoleteria();


  /* =========================
     AUTOCOMPLETE CLIENTES
  ========================= */
  clienteInput?.addEventListener("input", async () => {
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

  /* =========================
     TOTAL
  ========================= */
  function calcularTotal() {
    const opt = sectorSelect.options[sectorSelect.selectedIndex];
    const precio = opt ? parseFloat(opt.dataset.precio || 0) : 0;
    const cantidad = parseInt(cantidadInput.value || 0);
    const total = precio * cantidad;
    totalSpan.textContent = formatoMoneda(total);
    return total;
  }

  sectorSelect.addEventListener("change", calcularTotal);
  cantidadInput.addEventListener("input", calcularTotal);

  /* =========================
     BOTÓN VENDER
  ========================= */
  btnVender.addEventListener("click", () => {

    if (btnVender.disabled) {
      alert("❌ La caja está cerrada");
      return;
    }

    if (!sectorSelect.value) {
      alert("Seleccione un sector");
      return;
    }

    if (togglePagoCombinado.checked && !pagoMixtoConfirmado) {
      abrirPagoMixto();
      return;
    }

    registrarVenta();
  });

  /* =========================
     PAGO MIXTO
  ========================= */
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
        <input type="number" class="form-control form-control-sm montoPago">
      </div>
    `;
    $("pagosContainer").appendChild(div);
  }

  $("btnAgregarPago")?.addEventListener("click", agregarFilaPago);

  $("confirmarPagos")?.addEventListener("click", () => {
    pagosMixtos = [];
    let suma = 0;

    document.querySelectorAll(".montoPago").forEach((i, idx) => {
      const monto = parseFloat(i.value || 0);
      if (monto > 0) {
        pagosMixtos.push({
          medio: document.querySelectorAll(".medioPago")[idx].value,
          monto
        });
        suma += monto;
      }
    });

    if (suma !== calcularTotal()) {
      alert("Los montos no coinciden");
      return;
    }

    pagoMixtoConfirmado = true;
    bootstrap.Modal.getInstance($("modalPagos")).hide();
    registrarVenta();
  });

  /* =========================
     REGISTRAR VENTA
  ========================= */
  async function registrarVenta() {
    btnVender.disabled = true;

    const payload = {
      idcliente: idclienteInput.value,
      idsector: sectorSelect.value,
      cantidad: cantidadInput.value,
      total: calcularTotal(),
      idjornada: idjornadaInput.value,
      modopago: selectModoPago.value,
      pagos_mixtos: pagosMixtos
    };

    const res = await fetch("/registrar_venta_entrada", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!data.ok) {
      alert(data.msg);
      btnVender.disabled = false;
      return;
    }

    await imprimirTicket(data.idventa);
    resetearFormulario();
    verificarEstadoBoleteria();
  }

  function resetearFormulario() {
    sectorSelect.selectedIndex = 0;
    cantidadInput.value = 1;
    calcularTotal();
    pagosMixtos = [];
    pagoMixtoConfirmado = false;
    btnVender.disabled = false;
  }
});

/* =========================
   CERRAR CAJA
========================= */
async function cerrarCaja() {
  const res = await fetch("/cerrar_caja", { method: "POST" });
  const data = await res.json();

  if (!data.ok) {
    alert(data.msg || "Error");
    return;
  }

  alert("Caja cerrada");
  document.getElementById("venderEntrada").disabled = true;
  document.getElementById("estadoCaja").textContent = "Caja Cerrada";
  document.getElementById("estadoCaja").className = "badge bg-danger";
}

/* =========================
   IMPRIMIR TICKET
========================= */
function imprimirTicket(idventa) {
  return new Promise(resolve => {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = `/ticket_entrada/${idventa}`;
    document.body.appendChild(iframe);
    iframe.onload = () => {
      iframe.contentWindow.print();
      setTimeout(() => {
        document.body.removeChild(iframe);
        resolve();
      }, 800);
    };
  });
}
