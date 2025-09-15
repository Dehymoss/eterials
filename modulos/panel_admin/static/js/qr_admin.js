// qr_admin.js
// Script para el generador QR usando POST y base64
console.log('qr_admin.js cargado correctamente');

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('qr-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const mesa = document.getElementById('mesa').value;
        fetch('/admin/api/generate-qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ table_number: mesa })
        })
        .then(response => response.json())
        .then(data => {
            if (data.qr_base64) {
                document.getElementById('qr-result').innerHTML = `<img src='data:image/png;base64,${data.qr_base64}' alt='QR Mesa ${mesa}' />`;
            } else {
                document.getElementById('qr-result').innerHTML = `<span style='color:red'>Error generando QR</span>`;
            }
        })
        .catch(err => {
            document.getElementById('qr-result').innerHTML = `<span style='color:red'>Error de conexión</span>`;
        });
    });
});
