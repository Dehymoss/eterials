import requests
import time

BASE = 'http://127.0.0.1:5001'
UPLOAD = BASE + '/menu-admin/subir-imagen'
CREATE = BASE + '/menu-admin/api/productos'
LIST = BASE + '/menu-admin/api/productos'

# Archivo pequeño para enviar como multipart
filename = 'test_capu.jpg'
# Crear un pequeño contenido de imagen (no real) - el endpoint validará extensión
with open(filename, 'wb') as f:
    f.write(b'\xff\xd8\xff\xd9')  # archivo JPEG mínimo

print('1) Intentando subir imagen...')
files = {'file': (filename, open(filename, 'rb'), 'image/jpeg')}
try:
    r = requests.post(UPLOAD, files=files, timeout=10)
    print('UPLOAD status:', r.status_code)
    print('UPLOAD body:', r.text)
    data = r.json()
    if not data.get('success'):
        print('Upload failed:', data)
    else:
        image_url = data.get('url')
        print('Image URL:', image_url)
        print('2) Intentando crear producto con esa imagen...')
        payload = {
            'nombre': 'Capuccino E2E',
            'precio': '4.50',
            'descripcion': 'Creado en test e2e',
            'imagen_url': image_url,
            'categoria_id': '',
            'disponible': 'true',
            'tipo_producto': 'simple'
        }
        r2 = requests.post(CREATE, data=payload, timeout=10)
        print('CREATE status:', r2.status_code)
        print('CREATE body:', r2.text)

        print('\n3) Listando productos...')
        r3 = requests.get(LIST, timeout=10)
        print('LIST status:', r3.status_code)
        print('LIST body:', r3.text)
except Exception as e:
    print('Exception:', e)
finally:
    try:
        import os
        os.remove(filename)
    except:
        pass
