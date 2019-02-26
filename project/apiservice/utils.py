import django_rq
from .tasks import render_to_pdf

CHECK_TYPES = {
    'kitchen': 'kitchen_check.html',
    'client': 'client_check.html'
}


def get_template(check_type: str):
    template = CHECK_TYPES.get(check_type.lower())
    return template


def generate_pdf(data):
    queue = django_rq.get_queue()

    data['template'] = get_template(data.get('type'))
    data['check_type'] = data.pop('type')

    queue.enqueue(render_to_pdf, data)
    return
