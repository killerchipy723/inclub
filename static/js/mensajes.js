
  function actualizarReloj() {
    const ahora = new Date();

    const fecha = ahora.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });

    const hora = ahora.toLocaleTimeString('es-AR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    document.getElementById('reloj').innerHTML =
      `📅 ${fecha} ⏰ ${hora}`;
  }

  setInterval(actualizarReloj, 1000);
  actualizarReloj();

