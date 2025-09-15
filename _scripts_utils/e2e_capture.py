import requests, json, traceback, os
from io import BytesIO
OUT='g:/Mi unidad/eterials-chatbot/_scripts_utils/e2e_capture_output.txt'
BASE='http://127.0.0.1:5001'
lines=[]

try:
    lines.append('GET /menu-admin/api/productos')
    r = requests.get(BASE + '/menu-admin/api/productos', timeout=5)
    lines.append(f'STATUS {r.status_code}')
    lines.append(r.text)
except Exception as e:
    lines.append('GET error: ' + str(e))
    lines.append(traceback.format_exc())

bio_template = BytesIO(b'\xff\xd8\xff\xd9')
file_keys = ['file', 'imagen', 'image', 'foto', 'file0', 'archivo']
upload_success = False
upload_response = None
upload_attempts = []

try:
    lines.append('\nPOST /menu-admin/subir-imagen (intentando varias claves de archivo)')
    for key in file_keys:
        # reset buffer for each attempt
        bio_template.seek(0)
        files = {key: ('capu_test.jpg', bio_template, 'image/jpeg')}
        lines.append(f'-- Intentando clave de archivo: "{key}"')
        try:
            r2 = requests.post(BASE + '/menu-admin/subir-imagen', files=files, timeout=15)
            lines.append(f'STATUS {r2.status_code}')
            lines.append(r2.text)
            upload_attempts.append({'key': key, 'status': r2.status_code, 'text': r2.text})
            try:
                j = r2.json()
            except:
                j = None
            if j and j.get('success'):
                upload_success = True
                upload_response = j
                lines.append('UPLOAD OK with key: ' + key)
                break
        except Exception as ex:
            lines.append('REQUEST ERROR for key ' + key + ': ' + str(ex))
            lines.append(traceback.format_exc())

    if upload_success and upload_response:
        image_url = upload_response.get('url')
        lines.append('IMAGE_URL: ' + str(image_url))
        lines.append('\nPOST /menu-admin/api/productos (create)')
        payload = {
            'nombre': 'Capuccino_CAPTURE',
            'precio': '6.00',
            'descripcion': 'Creado por capture script',
            'imagen_url': image_url,
            'categoria_id': '',
            'disponible': 'true',
            'tipo_producto': 'simple'
        }
        try:
            rc = requests.post(BASE + '/menu-admin/api/productos', data=payload, timeout=15)
            lines.append(f'CREATE STATUS {rc.status_code}')
            lines.append(rc.text)
        except Exception as ex:
            lines.append('CREATE request failed: ' + str(ex))
            lines.append(traceback.format_exc())

        try:
            rg = requests.get(BASE + '/menu-admin/api/productos', timeout=5)
            lines.append('\nLIST STATUS ' + str(rg.status_code))
            lines.append(rg.text)
        except Exception as ex:
            lines.append('LIST request failed: ' + str(ex))
            lines.append(traceback.format_exc())
    else:
        lines.append('Upload attempts finished without success. Attempts:')
        for a in upload_attempts:
            lines.append(str(a))
        lines.append('Endpoint did not accept any attempted file field keys.')
except Exception as e:
    lines.append('UPLOAD/CREATE error: ' + str(e))
    lines.append(traceback.format_exc())

# Write output
try:
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('WROTE', OUT)
except Exception as e:
    print('Failed to write output file:', e)
    print('\n'.join(lines))
