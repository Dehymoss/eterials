window.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('particulas-logo');
    const ctx = canvas.getContext('2d');
    const colores = [
        '#ffe066', '#fffbe7', '#baffb3', '#7ecfff', '#ffb3e6',
        '#ffd166', '#b2f2bb', '#a5d8ff', '#e599f7'
    ];
    const cx = canvas.width / 2, cy = canvas.height / 2;
    const cantidad = 44; // Más partículas
    const radioMin = 38;
    const radioMax = 62;

    // Luciérnagas pequeñas y numerosas
    let luciernagas = [];
    for (let i = 0; i < cantidad; i++) {
        luciernagas.push({
            baseAngle: Math.random() * 2 * Math.PI,
            speed: 0.00012 + Math.random() * 0.00012,
            radio: radioMin + Math.random() * (radioMax - radioMin),
            color: colores[Math.floor(Math.random() * colores.length)],
            r: 0.7 + Math.random() * 1.1, // Más pequeñas
            brilloBase: 0.7 + Math.random() * 0.5,
            pulso: 1.5 + Math.random() * 1.5,
            desfase: Math.random() * Math.PI * 2
        });
    }

    function dibujarLuciernagas(t) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        luciernagas.forEach((luci, i) => {
            // Órbita suave y lenta
            const angle = luci.baseAngle + t * luci.speed;
            const x = cx + Math.cos(angle) * luci.radio;
            const y = cy + Math.sin(angle) * luci.radio;
            // Brillo pulsante
            const pulso = Math.sin(t * 0.001 * luci.pulso + luci.desfase) * 0.5 + 0.5;
            const alpha = 0.16 + luci.brilloBase * pulso;
            ctx.save();
            ctx.beginPath();
            ctx.arc(x, y, luci.r + pulso * 0.7, 0, 2 * Math.PI);
            ctx.globalAlpha = alpha;
            ctx.shadowColor = luci.color;
            ctx.shadowBlur = 22 + 10 * pulso;
            ctx.fillStyle = luci.color;
            ctx.fill();
            ctx.restore();
        });
    }

    function animar(ts) {
        dibujarLuciernagas(ts);
        requestAnimationFrame(animar);
    }
    requestAnimationFrame(animar);

    // Oculta el logo de carga y muestra el menú después de 2.5s
    setTimeout(function() {
        document.getElementById('logo-carga-menu').style.opacity = '0';
        setTimeout(function() {
            document.getElementById('logo-carga-menu').style.display = 'none';
            // Mostrar el contenido del menú
            document.getElementById('contenido-menu').style.display = 'block';
        }, 700);
    }, 2500);
});