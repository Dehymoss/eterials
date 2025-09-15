function obtenerSaludo() {
    let hora = new Date().getHours();
    if (hora >= 6 && hora < 12) return "Buenos días";
    if (hora >= 12 && hora < 18) return "Buenas tardes";
    return "Buenas noches";
}

function mostrarSaludo() {
    let saludo = obtenerSaludo();
    let numeroMesa = new URLSearchParams(window.location.search).get("mesa") || "Sin número";
    let nombreCliente = sessionStorage.getItem("nombreCliente") || "Invitado";
    let mensaje = `<span class="saludo-destacado">${saludo}</span><br>
    <span class="saludo-mensaje">
        ¡Bienvenido${nombreCliente !== "Invitado" ? `, <b>${nombreCliente}</b>` : ""}!<br>
        Es un placer atenderte en la mesa <b>${numeroMesa}</b>.
    </span>`;
    if (nombreCliente !== "Invitado") {
        document.getElementById("nombre-container").style.display = "none";
    } else {
        document.getElementById("nombre-container").style.display = "block";
    }
    document.getElementById("saludo").innerHTML = mensaje;
}

function actualizarEnlacesMenu() {
    const params = new URLSearchParams(window.location.search);
    const mesa = params.get("mesa") || sessionStorage.getItem("mesa") || 1;
    const nombreCliente = sessionStorage.getItem("nombreCliente") || "";
    
    // Construir parámetros de URL
    let parametros = `mesa=${mesa}`;
    if (nombreCliente && nombreCliente !== "Invitado") {
        parametros += `&nombre=${encodeURIComponent(nombreCliente)}`;
    }
    
    // Actualizar enlace del menú
    document.getElementById('btn-menu').href = `/menu/general?${parametros}`;
    
    // También actualizar otros enlaces que pueden necesitar el nombre
    const base = "/modulos";
    document.getElementById("btn-cancionero").href = `/modulos/cancionero/index.html?${parametros}`;
    document.getElementById("btn-mesero").href = `${base}/mesero/index.html?${parametros}`;
    document.getElementById("btn-karaoke").href = `${base}/karaoke/index.html?${parametros}`;
    document.getElementById("btn-opiniones").href = `${base}/opiniones/index.html?${parametros}`;
}

function guardarNombre() {
    let nombre = document.getElementById("nombre").value.trim();
    if (nombre !== "") {
        sessionStorage.setItem("nombreCliente", nombre);
        mostrarSaludo();
        actualizarEnlacesMenu(); // Actualizar enlaces cuando se guarda el nombre
        alert(`¡Gracias, ${nombre}! Ahora te llamaremos por tu nombre.`);
    } else {
        alert("Por favor, ingresa un nombre válido.");
    }
}

// --- Inactividad: cerrar sesión tras 10 minutos (600000 ms) ---
let inactividadTimeout;
function resetInactividad() {
    clearTimeout(inactividadTimeout);
    inactividadTimeout = setTimeout(() => {
        sessionStorage.clear();
        location.reload();
    }, 600000); // 10 minutos
}
["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(evt =>
    document.addEventListener(evt, resetInactividad)
);

// Estrellas de calificación
document.addEventListener('DOMContentLoaded', function () {
    mostrarSaludo();
    resetInactividad();
    actualizarEnlacesMenu(); // Actualizar enlaces al cargar la página

    const estrellas = document.querySelectorAll('.estrella');
    let calificacionSeleccionada = 0;

    estrellas.forEach(estrella => {
        estrella.addEventListener('mouseenter', function () {
            pintarEstrellas(this.dataset.valor);
        });
        estrella.addEventListener('mouseleave', function () {
            pintarEstrellas(calificacionSeleccionada);
        });
        estrella.addEventListener('click', function () {
            calificacionSeleccionada = this.dataset.valor;
            pintarEstrellas(calificacionSeleccionada);
        });
    });

    function pintarEstrellas(valor) {
        estrellas.forEach(estrella => {
            if (estrella.dataset.valor <= valor) {
                estrella.classList.add('seleccionada');
            } else {
                estrella.classList.remove('seleccionada');
            }
        });
    }

    window.enviarCalificacion = function () {
        if (calificacionSeleccionada > 0) {
            alert(`¡Gracias por tu calificación de ${calificacionSeleccionada} estrella(s)!`);
        } else {
            alert('Por favor, selecciona una calificación.');
        }
    }
});

function actualizarSaludo() {
    const h2Saludo = document.querySelector('.texto-iluminable:nth-of-type(2)');
    const hora = new Date().getHours();
    let saludo = "Buenas noches";
    if (hora >= 6 && hora < 12) {
        saludo = "Buenos días";
    } else if (hora >= 12 && hora < 20) {
        saludo = "Buenas tardes";
    }
    if (h2Saludo) {
        h2Saludo.textContent = saludo;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Chatbot cargado correctamente');
    actualizarSaludo();
    mostrarSaludo();
    actualizarEnlacesMenu();
});

// Guardar mesa en sessionStorage
document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);
    let mesa = params.get("mesa");
    if (mesa) {
        sessionStorage.setItem("mesa", mesa);
    }
});