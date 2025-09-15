from modulos.frontend.menu.routes import menu_bp

def init_menu_frontend(app):
    """Inicializar el módulo frontend del menú"""
    app.register_blueprint(menu_bp)
    
    # Configurar filtros de template personalizados
    @app.template_filter('format_precio')
    def format_precio(precio):
        """Formatear precio como moneda colombiana"""
        if not precio:
            return "Gratis"
        return f"${precio:,.0f}".replace(',', '.')
    
    @app.template_filter('truncate_words')
    def truncate_words(text, max_words=15):
        """Truncar texto a un número máximo de palabras"""
        if not text:
            return ""
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."
    
    @app.template_filter('get_saludo')
    def get_saludo():
        """Obtener saludo según la hora"""
        from datetime import datetime
        hora = datetime.now().hour
        if 6 <= hora < 12:
            return "Buenos días"
        elif 12 <= hora < 18:
            return "Buenas tardes"
        else:
            return "Buenas noches"
    
    return menu_bp