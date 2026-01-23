
// Filtrado de tabla de productos mientras escribís
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('filterProducto');
    const table = document.querySelector('.table tbody'); // tbody de la tabla
    const rows = Array.from(table.querySelectorAll('tr'));

    input.addEventListener('input', () => {
        const filter = input.value.toUpperCase();

        rows.forEach(row => {
            const productName = row.cells[1].textContent.toUpperCase(); // columna Producto
            if (productName.includes(filter)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
});

