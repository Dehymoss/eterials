function toggleTipoQR(tipo) {
    document.getElementById('panel-mesas').style.display = tipo === 'mesa' ? '' : 'none';
    document.getElementById('panel-barra').style.display = tipo === 'barra' ? '' : 'none';
    document.getElementById('qrContainer').innerHTML = '';
}

async function generarQRCodes() {
    let container = document.getElementById("qrContainer");
    container.innerHTML = "";
    let cantidadMesas = document.getElementById("cantidad").value;
    if (!cantidadMesas || cantidadMesas < 1 || cantidadMesas % 1 !== 0) {
        alert("Por favor ingresa una cantidad válida de mesas.");
        return;
    }
    
    // Obtener IP local dinámicamente
    let baseUrl = 'http://192.168.1.23:8080'; // Fallback
    try {
        const response = await fetch('/admin/api/get-local-ip');
        const data = await response.json();
        if (data.success) {
            baseUrl = data.base_url;
        }
    } catch (e) {
        console.log('Usando IP fallback:', baseUrl);
    }
    
    for (let i = 1; i <= cantidadMesas; i++) {
        let div = document.createElement("div");
        div.className = "qr-box";
        div.innerHTML = `
            <div class='qr-arte-mesa'>Mesa ${i}</div>
            <div id="qr-${i}"></div>
            <button onclick="descargarQR(${i}, 'mesa')">Descargar QR</button>
        `;
        container.appendChild(div);
        let url = `${baseUrl}/chatbot?mesa=${i}`;
        new QRCode(document.getElementById(`qr-${i}`), {
            text: url,
            width: 150,
            height: 150
        });
    }
}

async function generarQRBarra() {
    let container = document.getElementById("qrContainer");
    container.innerHTML = "";
    
    // Obtener IP local dinámicamente
    let baseUrl = 'http://192.168.1.23:8080'; // Fallback
    try {
        const response = await fetch('/admin/api/get-local-ip');
        const data = await response.json();
        if (data.success) {
            baseUrl = data.base_url;
        }
    } catch (e) {
        console.log('Usando IP fallback:', baseUrl);
    }
    
    let div = document.createElement("div");
    div.className = "qr-box";
    div.innerHTML = `
        <div class='qr-arte-mesa'>Barra</div>
        <div id="qr-barra"></div>
        <button onclick="descargarQR('barra', 'barra')">Descargar QR</button>
    `;
    container.appendChild(div);
    let url = `${baseUrl}/chatbot?mesa=barra`;
    new QRCode(document.getElementById(`qr-barra`), {
        text: url,
        width: 150,
        height: 150
    });
}

function descargarQR(id, tipo) {
    let qrCanvas = document.querySelector(`#qr-${id} canvas`);
    let nombre = tipo === 'barra' ? 'QR_Barra.png' : `QR_Mesa_${id}.png`;
    // Crear canvas personalizado
    let finalCanvas = document.createElement('canvas');
    finalCanvas.width = 350;
    finalCanvas.height = 420;
    let ctx = finalCanvas.getContext('2d');
    // Fondo blanco
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, finalCanvas.width, finalCanvas.height);
    // Nombre establecimiento centrado y dentro de la imagen
    ctx.font = 'bold 36px Caveat, cursive';
    ctx.fillStyle = '#FFD700';
    ctx.textAlign = 'center';
    ctx.fillText('Eterials Gastro Café', finalCanvas.width/2, 60);
    // Mesa/barra estilizado
    ctx.font = 'bold 32px Caveat, cursive';
    ctx.fillStyle = '#1e3c72';
    let texto = tipo === 'barra' ? 'Barra' : `Mesa ${id}`;
    ctx.fillText(texto, finalCanvas.width/2, 110);
    // QR
    ctx.drawImage(qrCanvas, (finalCanvas.width-150)/2, 130, 150, 150);
    // Pie de página
    ctx.font = '16px Segoe UI, Tahoma, Geneva, Verdana, sans-serif';
    ctx.fillStyle = '#888';
    ctx.fillText('Eterials Gastro-Café © 2025', finalCanvas.width/2, 400);
    // Descargar
    let link = document.createElement("a");
    link.href = finalCanvas.toDataURL("image/png");
    link.download = nombre;
    link.click();
}
