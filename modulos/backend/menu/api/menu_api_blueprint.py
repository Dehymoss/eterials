from flask import Blueprint, jsonify, request, render_template, redirect, url_for, send_from_directory
import json
import os

menu_api_bp = Blueprint(
    'menu_api',
    __name__,
    static_folder='../static',
    template_folder='../templates'
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OPCIONES_FILE = os.path.join(BASE_DIR, 'opciones-menu.json')
MENU_DIA_FILE = os.path.join(BASE_DIR, 'menu-dia.json')

def leer_json(ruta, default):
    if os.path.exists(ruta):
        with open(ruta, encoding='utf-8') as f:
            return json.load(f)
    return default

def guardar_json(ruta, data):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@menu_api_bp.route('/api/opciones-menu')
def api_opciones_menu():
    return jsonify(leer_json(OPCIONES_FILE, {}))

@menu_api_bp.route('/api/menu-dia', methods=['GET', 'POST'])
def api_menu_dia():
    if request.method == 'POST':
        data = request.json
        guardar_json(MENU_DIA_FILE, data)
        return jsonify({"ok": True})
    return jsonify(leer_json(MENU_DIA_FILE, {}))

@menu_api_bp.route('/admin/menu', methods=['GET', 'POST'])
def admin_menu():
    opciones = leer_json(OPCIONES_FILE, {})
    print("Opciones cargadas:", opciones)
    menu_default = {
        "desayuno": {"sopas": ["", "", ""], "platos": ["", "", ""], "bebidas": ["", "", ""]},
        "almuerzo": {"sopas": ["", "", ""], "platos": ["", "", ""], "proteinas": ["", "", ""], "bebidas": ["", "", ""]}
    }
    menu = leer_json(MENU_DIA_FILE, menu_default)
    for k in menu_default:
        if k not in menu:
            menu[k] = menu_default[k]
        else:
            for subk in menu_default[k]:
                if subk not in menu[k]:
                    menu[k][subk] = menu_default[k][subk]
    if request.method == 'POST':
        desayuno_sopas = [request.form.get(f'desayuno_sopa_{i}', '') for i in range(1, 4)]
        desayuno_platos = [request.form.get(f'desayuno_plato_{i}', '') for i in range(1, 4)]
        desayuno_bebidas = [request.form.get(f'desayuno_bebida_{i}', '') for i in range(1, 4)]
        almuerzo_sopas = [request.form.get(f'almuerzo_sopa_{i}', '') for i in range(1, 4)]
        almuerzo_platos = [request.form.get(f'almuerzo_plato_{i}', '') for i in range(1, 4)]
        almuerzo_proteinas = [request.form.get(f'almuerzo_proteina_{i}', '') for i in range(1, 4)]
        almuerzo_bebidas = [request.form.get(f'almuerzo_bebida_{i}', '') for i in range(1, 4)]
        menu = {
            "desayuno": {
                "sopas": desayuno_sopas,
                "platos": desayuno_platos,
                "bebidas": desayuno_bebidas
            },
            "almuerzo": {
                "sopas": almuerzo_sopas,
                "platos": almuerzo_platos,
                "proteinas": almuerzo_proteinas,
                "bebidas": almuerzo_bebidas
            }
        }
        guardar_json(MENU_DIA_FILE, menu)
    return render_template('admin_menu.html', opciones=opciones, menu=menu)

@menu_api_bp.route('/admin/items-menu', methods=['GET', 'POST'], endpoint='admin_items_menu')
def admin_items_menu():
    opciones = leer_json(OPCIONES_FILE, {})
    mensaje = ''
    if request.method == 'POST':
        archivo = request.files.get('archivo')
        if archivo:
            uploads_dir = os.path.join(BASE_DIR, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            ruta_archivo = os.path.join(uploads_dir, archivo.filename)
            archivo.save(ruta_archivo)
            mensaje = "Archivo subido con éxito"
        else:
            mensaje = "No se recibió ningún archivo"
    return render_template('admin_items_menu.html', opciones=opciones, mensaje=mensaje)

@menu_api_bp.route('/admin/eliminar-opcion', methods=['POST'])
def eliminar_opcion():
    opciones = leer_json(OPCIONES_FILE, {})
    clave = request.form.get('clave')
    if clave and clave in opciones:
        del opciones[clave]
        guardar_json(OPCIONES_FILE, opciones)
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Opción no encontrada"}), 404

@menu_api_bp.route('/admin/editar-opcion', methods=['POST'])
def editar_opcion():
    opciones = leer_json(OPCIONES_FILE, {})
    comida = request.form.get('comida')
    categoria = request.form.get('categoria')
    original_item = request.form.get('original_item')
    nuevo_item = request.form.get('nuevo_item')
    if comida and categoria and original_item and nuevo_item:
        items = opciones.get(comida, {}).get(categoria, [])
        try:
            idx = items.index(original_item)
            items[idx] = nuevo_item
            guardar_json(OPCIONES_FILE, opciones)
            return redirect(url_for('menu_api.admin_items_menu'))
        except ValueError:
            pass
    return redirect(url_for('menu_api.admin_items_menu'))

@menu_api_bp.route('/')
def index():
    return render_template('index.html')

@menu_api_bp.route('/menu')
def menu():
    return render_template('menu.html', opciones=leer_json(OPCIONES_FILE, {}))

@menu_api_bp.route('/admin')
def admin():
    return render_template('admin.html')

@menu_api_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    return send_from_directory(uploads_dir, filename)

