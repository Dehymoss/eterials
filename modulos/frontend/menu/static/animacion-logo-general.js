document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('particulas-logo');
    const ctx = canvas.getContext('2d');
    
    // Configurar el canvas para pantalla completa
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Arreglo de partículas
    const particulas = [];

    // Crear partículas
    for (let i = 0; i < 50; i++) {
        particulas.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            alpha: Math.random() * 0.3 + 0.1
        });
    }

    // Animar partículas
    function animarParticulas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particulas.forEach(particula => {
            // Actualizar posición
            particula.x += particula.vx;
            particula.y += particula.vy;
            
            // Rebotar en los bordes
            if (particula.x < 0 || particula.x > canvas.width) particula.vx *= -1;
            if (particula.y < 0 || particula.y > canvas.height) particula.vy *= -1;
            
            // Dibujar partícula
            ctx.beginPath();
            ctx.arc(particula.x, particula.y, 2, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 224, 102, ${particula.alpha})`;
            ctx.fill();
        });
        
        requestAnimationFrame(animarParticulas);
    }

    // Iniciar animación
    animarParticulas();

    // Redimensionar canvas cuando cambie el tamaño de ventana
    window.addEventListener('resize', function() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    // Oculta el logo de carga y muestra el menú después de 2.5s
    setTimeout(function() {
        document.getElementById('logo-carga-menu').style.opacity = '0';
        setTimeout(function() {
            document.getElementById('logo-carga-menu').style.display = 'none';
            // Mostrar el contenido del menú general (NO redirigir a Treinta)
            document.getElementById('contenido-menu').style.display = 'block';
        }, 700);
    }, 2500);
});
