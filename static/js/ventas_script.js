
    function formatoMoneda(valor) {
      return new Intl.NumberFormat('es-AR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(valor);
    }

// ====================== Carrito ======================
const carrito = [];

function actualizarCarrito() {
  const tbody = document.querySelector("#carritoTable tbody");
  tbody.innerHTML = "";
  let total = 0;

  carrito.forEach((item, index) => {
    const subtotal = item.precio * item.cantidad;
    total += subtotal;
    tbody.innerHTML += `
      <tr>
        <td>${item.nombre}</td>
        <td><input type="number" class="form-control form-control-sm cantidad" data-index="${index}" value="${item.cantidad}" min="1"></td>
        <td>${formatoMoneda(item.precio)}</td>
        <td>${formatoMoneda(subtotal)}</td>
        <td><input type="checkbox" class="cortesia" data-index="${index}" ${item.cortesia ? 'checked' : ''}></td>
        <td><button class="btn btn-danger btn-sm eliminar" data-index="${index}">X</button></td>
      </tr>
    `;
  });

  document.getElementById("total").textContent = formatoMoneda(total);

}

// ====================== Agregar productos ======================
document.querySelectorAll(".agregar").forEach(btn => {
  btn.addEventListener("click", e => {
    const card = e.target.closest(".producto-card");
    const id = card.dataset.id;
    const nombre = card.dataset.nombre;
    const precio = parseFloat(card.dataset.precio);

    const existing = carrito.find(p => p.id == id);
    if (existing) existing.cantidad++;
    else carrito.push({id, nombre, precio, cantidad:1, cortesia:false});

    actualizarCarrito();
  });
});

// ====================== Cambiar cantidad o cortesía ======================
document.querySelector("#carritoTable").addEventListener("input", e => {
  const index = e.target.dataset.index;
  if (e.target.classList.contains("cantidad")) carrito[index].cantidad = parseInt(e.target.value);
  if (e.target.classList.contains("cortesia")) carrito[index].cortesia = e.target.checked;
  actualizarCarrito();
});

// ====================== Eliminar producto ======================
document.querySelector("#carritoTable").addEventListener("click", e => {
  if(e.target.classList.contains("eliminar")) {
    carrito.splice(e.target.dataset.index,1);
    actualizarCarrito();
  }
});

// ====================== Procesar venta ======================
document.getElementById("procesarVenta").addEventListener("click", () => {
  if(carrito.length===0){ alert("Seleccione al menos un producto"); return; }

  const form = document.createElement("form");
  form.method="POST"; 
  form.action="/registrar_venta";

  // Cliente y Modo de Pago
  const clienteInput = document.createElement("input");
  clienteInput.name="cliente"; 
  clienteInput.value=document.getElementById("cliente").value;
  form.appendChild(clienteInput);

  const modopagoInput = document.createElement("input");
  modopagoInput.name="modopago"; 
  modopagoInput.value=document.getElementById("modopago").value;
  form.appendChild(modopagoInput);

  // Productos, Cantidades, Precios y Cortesias
  carrito.forEach(item => {
    const prod = document.createElement("input");
    prod.type = "hidden"; prod.name="productos[]"; prod.value=item.id; form.appendChild(prod);

    const cant = document.createElement("input");
    cant.type = "hidden"; cant.name="cantidades[]"; cant.value=item.cantidad; form.appendChild(cant);

    const precio = document.createElement("input");
    precio.type = "hidden"; precio.name="precios[]"; precio.value=item.precio; form.appendChild(precio);

    const cort = document.createElement("input");
    cort.type = "hidden"; cort.name="cortesias[]"; cort.value=item.cortesia; form.appendChild(cort);
  });

  // Total
  const totalInput = document.createElement("input");
  totalInput.name="total"; totalInput.value=document.getElementById("total").textContent;
  form.appendChild(totalInput);

  document.body.appendChild(form);
  form.submit();
});

      // ====================== Ocultar mensaje al interactuar ======================
    const mensaje = document.getElementById("mensaje-confirmacion");

    if (mensaje) {
      const ocultarMensaje = () => {
        mensaje.style.transition = "opacity 0.3s";
        mensaje.style.opacity = "0";
        setTimeout(() => mensaje.remove(), 300);
      };

      // Cualquier click en la pantalla
      document.addEventListener("click", ocultarMensaje, { once: true });

      // Cualquier tecla
      document.addEventListener("keydown", ocultarMensaje, { once: true });
    }

