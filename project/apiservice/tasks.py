import json
import requests
from os.path import join
from base64 import b64encode
from django.conf import settings
from django.template.loader import get_template

from .models import Check


def render_to_pdf(data):
    check_type, printer_id, order_id = map(data.get, ('check_type', 'printer_id', 'order_id'))
    pdf_file_name = "{}_{}.pdf".format(order_id, check_type)
    upload_to = 'pdf'
    pdf_path = join(join(settings.MEDIA_ROOT, upload_to), pdf_file_name)
    url = 'http://localhost:32769'
    encoding = 'utf-8'

    html = get_template(data.get('template')).render(data)
    byte_content = html.encode(encoding)

    base64_bytes = b64encode(byte_content)
    base64_string = base64_bytes.decode(encoding)

    data = {
        'contents': base64_string,
    }
    headers = {
        'Content-Type': 'application/json'    # This is important
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)

    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    try:
        check = Check.objects.get(order_id=order_id, type=check_type, printer_id=printer_id)
        check.status = 'rendered'
        check.pdf_file.name = join(upload_to, pdf_file_name)
        check.save()
    except Check.DoesNotExist:
        # TODO: pass
        pass

    print("Rendered")
