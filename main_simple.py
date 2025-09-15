from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "¡Hola! Sistema Eterials Restaurant funcionando en Render.com 🎉"

@app.route('/test')
def test():
    return "Test endpoint funcionando correctamente ✅"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
