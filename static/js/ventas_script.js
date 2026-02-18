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
   MODAL CONFIRMAR VENTA - CONFIGURACIÓN
===================================================== */
const modalConfirmarVentaEl = $("modalConfirmarVenta");
const modalConfirmarVenta = new bootstrap.Modal(modalConfirmarVentaEl);

// Cuando el modal se abre → foco automático en Confirmar
modalConfirmarVentaEl.addEventListener("shown.bs.modal", () => {
  $("btnConfirmarVenta").focus();
});

// ENTER confirma venta
modalConfirmarVentaEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    $("btnConfirmarVenta").click();
  }
});


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
   CONTROL VISUAL DE STOCK
===================================================== */
document.querySelectorAll(".producto-card").forEach(card => {
  const stock = parseInt(card.dataset.stock);
  const btn = card.querySelector(".agregar");

  if (!btn) return;

  btn.classList.remove("btn-success", "btn-warning", "btn-danger");

  if (stock === 0) {
    btn.classList.add("btn-danger");   // 🔴 sin stock
    btn.title = "Producto sin stock";
  }
  else if (stock > 0 && stock <= 10) {
    btn.classList.add("btn-warning");  // 🟡 bajo
    btn.title = "Stock bajo";
  }
  else {
    btn.classList.add("btn-success");  // 🟢 normal
    btn.title = "Stock disponible";
  }
});


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
    const stock = parseInt(card.dataset.stock) || 0;

    // 🚫 NO PERMITIR AGREGAR SI NO HAY STOCK
    if (stock <= 0) {
      alert("Este producto no tiene stock disponible.");
      return;
    }

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
        autorizado: "",
        stock: stock   // ⭐️ ESTA ES LA CLAVE
      });
    }

    actualizarCarrito();
  });
});

  /* =====================================================
     ACTUALIZAR STOCK
  ===================================================== */
async function refrescarStockDesdeServidor() {
  console.log("🔄 Refrescando stock...");

  const res = await fetch("/stock_productos");
  const productos = await res.json();

  productos.forEach(p => {

    const card = document.querySelector(`.producto-card[data-id="${p.idproductos}"]`);
    if (!card) return;

    // ✅ ACTUALIZA DATASET
    card.dataset.stock = p.stock;

    // ✅ ACTUALIZA TEXTO VISIBLE
    const stockText = card.querySelector(".stock-text");
    if (stockText) {
      stockText.textContent = "Stock: " + p.stock;
    }

    // ✅ CAMBIA COLOR DEL BOTÓN
    const btn = card.querySelector(".agregar");
    if (!btn) return;

    btn.className = "btn btn-sm agregar mt-1 w-100 fw-bold";

    if (p.stock === 0) {
      btn.classList.add("btn-danger");
      btn.title = "Sin stock";
    }
    else if (p.stock <= 10) {
      btn.classList.add("btn-warning");
      btn.title = "Stock bajo";
    }
    else {
      btn.classList.add("btn-success");
      btn.title = "Stock normal";
    }
  });
}




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
   MODAL PAGOS - INSTANCIA ÚNICA
===================================================== */
const modalPagosEl = $("modalPagos");
const modalPagos = new bootstrap.Modal(modalPagosEl);


/* =====================================================
   TOGGLE PAGO COMBINADO
===================================================== */
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


/* =====================================================
   ABRIR MODAL PAGO MIXTO
===================================================== */
function abrirPagoMixto() {

  $("pagosContainer").innerHTML = "";
  $("totalVentaModal").textContent = formatoMoneda(calcularTotal());

  agregarFilaPago();
  modalPagos.show();
}


/* =====================================================
   SI SE CIERRA EL MODAL SIN CONFIRMAR → APAGAR TOGGLE
===================================================== */
modalPagosEl.addEventListener("hidden.bs.modal", () => {

  if (!pagoMixtoConfirmado) {
    togglePagoCombinado.checked = false;
    togglePagoCombinado.dispatchEvent(new Event("change"));
  }

});


/* =====================================================
   AGREGAR FILA DE PAGO
===================================================== */
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


/* =====================================================
   CONFIRMAR PAGOS MIXTOS
===================================================== */
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
    alert("Los montos no coinciden con el total");
    return;
  }

  pagoMixtoConfirmado = true;
  modalPagos.hide();

  registrarVenta();
});


/* =====================================================
   COBRAR → ABRIR MODAL
===================================================== */
$("procesarVenta")?.addEventListener("click", () => {

  if (!carrito.length) {
    alert("Debe agregar productos");
    return;
  }

  const sinStock = carrito.find(p => p.stock <= 0);
  if (sinStock) {
    alert("Hay productos sin stock. Pedir reposición al administrador.");
    return;
  }

  if (togglePagoCombinado.checked && !pagoMixtoConfirmado) {
    abrirPagoMixto();
    return;
  }

  prepararModalConfirmacion();
  modalConfirmarVenta.show();
});

/* =====================================================
   ATAJO TECLADO - BOTÓN COBRAR
===================================================== */

document.addEventListener("keydown", function (e) {

  // No activar si estás escribiendo en un input
  const tag = document.activeElement.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

  // Tecla + (fila superior)
  if (e.key === "1") {
    e.preventDefault();
    document.getElementById("procesarVenta")?.click();
  }

});



/* =====================================================
   CANCELAR VENTA
===================================================== */
$("btnCancelarVenta")?.addEventListener("click", () => {
  modalConfirmarVenta.hide();
});


/* =====================================================
   ARMAR MODAL CONFIRMACIÓN
===================================================== */
function prepararModalConfirmacion() {

  const tbody = $("tablaConfirmacion").querySelector("tbody");
  tbody.innerHTML = "";

  carrito.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.nombre}</td>
      <td class="text-center">${p.cantidad}</td>
      <td class="text-end">$ ${formatoMoneda(p.precio)}</td>
      <td class="text-end">$ ${formatoMoneda(p.cantidad * p.precio)}</td>
    `;
    tbody.appendChild(tr);
  });

  $("totalConfirmacion").textContent = formatoMoneda(calcularTotal());

  const pagosUl = $("confirmacionPagos");
  pagosUl.innerHTML = "";

  if (togglePagoCombinado.checked) {
    pagosMixtos.forEach(p => {
      const li = document.createElement("li");
      li.textContent = `${obtenerNombreModoPago(p.medio)}: $ ${formatoMoneda(p.monto)}`;
      pagosUl.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = `${selectModoPago.options[selectModoPago.selectedIndex].text}: $ ${formatoMoneda(calcularTotal())}`;
    pagosUl.appendChild(li);
  }
}


/* =====================================================
   CONFIRMAR VENTA
===================================================== */
$("btnConfirmarVenta")?.addEventListener("click", async () => {
  modalConfirmarVenta.hide();
  await registrarVenta();
});


/* =====================================================
   REGISTRAR VENTA
===================================================== */
async function registrarVenta() {

  const fd = new FormData();

  fd.append("cliente", $("idcliente").value);
  fd.append("total", calcularTotal());

  if (togglePagoCombinado.checked) {
    fd.append("pagos_mixtos", JSON.stringify(pagosMixtos));
  } else {
    fd.append("modopago", selectModoPago.value);
  }

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
    alert(data.error || "Error al registrar venta");
    return;
  }

  imprimirTicket(data.idventa);
  actualizarRecaudacionCaja();
  await refrescarStockDesdeServidor();
  resetearVenta();
}


/* =====================================================
   IMPRIMIR
===================================================== */
function imprimirTicket(id) {
  const iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = `/ticket/${id}`;
  document.body.appendChild(iframe);
  iframe.onload = () => iframe.contentWindow.print();
}


/* =====================================================
   RESET VENTA
===================================================== */
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
  togglePagoCombinado.dispatchEvent(new Event("change"));

  $("pagosContainer").innerHTML = "";
  $("totalVentaModal").textContent = "0";
}

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
   AUTOCOMPLETE CLIENTES
===================================================== */
const clienteInput   = $("clienteInput");
const listaClientes  = $("listaClientes");
const idclienteInput = $("idcliente");

clienteInput?.addEventListener("input", async () => {
  const q = clienteInput.value.trim();

  listaClientes.innerHTML = "";
  idclienteInput.value = "1"; // Consumidor Final por defecto

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

  bootstrap.Modal
    .getInstance($("modalCortesia"))
    ?.hide();

  actualizarCarrito();
});


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


 

