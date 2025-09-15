from flask import Flask
import os

print("🚀 Iniciando aplicación Flask...")

# Crear la app Flask principal
app = Flask(__name__)

@app.route('/')
def index():
    return """
    <h1>🎉 ¡Sistema Eterials Restaurant FUNCIONANDO!</h1>
    <p>Deployment exitoso en Render.com</p>
    <ul>
        <li><a href="/chatbot">Chatbot</a></li>
        <li><a href="/admin">Panel Admin</a></li>
        <li><a href="/menu">Menú</a></li>
        <li><a href="/test">Test</a></li>
    </ul>
    """

@app.route('/test')
def test():
    return "✅ Test endpoint funcionando correctamente"

@app.route('/chatbot')
def chatbot():
    return "🤖 Chatbot - Sistema funcionando (versión simple)"

@app.route('/admin')
def admin():
    return "⚙️ Panel Admin - Sistema funcionando (versión simple)"

@app.route('/menu')
def menu():
    return "🍽️ Menú - Sistema funcionando (versión simple)"

if __name__ == "__main__":
    print("🚀 Iniciando servidor Eterials...")
    
    # Configuración para producción/desarrollo
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Servidor iniciando en puerto {port}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
