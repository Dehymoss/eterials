from flask import Blueprint, render_template

# Solo definimos el blueprint, no una nueva app Flask
chatbot_bp = Blueprint(
    'chatbot',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@chatbot_bp.route('/')
def chatbot():
    return render_template('chatbot.html')

@chatbot_bp.route('/test')
def chatbot_test():
    """Template simplificado para debugging"""
    return render_template('chatbot_simple.html')

@chatbot_bp.route('/debug2')
def chatbot_debug2():
    """Template con CSS simplificado"""
    return render_template('chatbot_debug.html')

@chatbot_bp.route('/debug')
def chatbot_debug():
    """Página de debugging simple"""
    return """
    <html>
    <head><title>Debug Chatbot</title></head>
    <body style="font-family: Arial; padding: 20px; background: #333; color: white;">
        <h1>🔧 Debug del Chatbot</h1>
        <p>✅ El blueprint del chatbot está funcionando correctamente</p>
        <p>📍 URL actual: /chatbot/debug</p>
        <p>🔗 <a href="/chatbot" style="color: #FFD700;">Ir al chatbot principal</a></p>
        <p>🌐 <a href="/admin" style="color: #FFD700;">Ir al panel admin</a></p>
        <p>🍽️ <a href="/menu" style="color: #FFD700;">Ir al menú</a></p>
    </body>
    </html>
    """