import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.renderers import BaseRenderer, JSONRenderer

from .models import Check, Printer
from .serializers import CheckSerializer
from .utils import generate_pdf


GET_CHECK_ERROR_MESSAGE = dict(error='При создании чеков произошла одна из ошибок: '
                                     'Данного чека не существует Для данного чека не сгенерирован '
                                     'PDF-файл')

CREATE_CHECK_ERROR_MESSAGE = dict(error='При создании чеков произошла одна из ошибок:'
                                        ' 1. Для данного заказа уже созданы чеки'
                                        ' 2. Для данной точки не настроено ни одного принтера')

API_KEY_ERROR_MESSAGE = {"error": "Ошибка авторизации"}


class PDFRenderer(BaseRenderer):
  media_type = 'application/pdf'
  format = 'pdf'
  charset = None
  render_style = 'binary'

  def render(self, data, media_type=None, renderer_context=None):
    if isinstance(data, bytes):
      return data
    if renderer_context.get('response'):
      resp = renderer_context.get('response')
      if resp.status_code == 400 or resp.status_code == 401:
        accepted_media_type = 'application/json'
        new_response = JSONRenderer().render(resp.data, accepted_media_type, renderer_context)
        return new_response
    data_to_response = json.dumps(data)
    return bytes(data_to_response.encode('utf-8'))


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_checks_list(request):
  api_key = request.query_params.get('api_key')
  if not api_key:
    return Response(API_KEY_ERROR_MESSAGE, status=status.HTTP_401_UNAUTHORIZED)
  try:
    printer = Printer.objects.get(api_key=api_key)
  except Printer.DoesNotExist:
    return Response(API_KEY_ERROR_MESSAGE, status=status.HTTP_401_UNAUTHORIZED)
  checks = Check.objects.filter(printer_id=printer.pk, status='rendered')
  serializer = CheckSerializer(checks, many=True, fields=('id',), context={'request': request})
  return Response({'checks': serializer.data})


@api_view(['GET'])
@renderer_classes((PDFRenderer, ))
@permission_classes((AllowAny,))
def get_check(request):
  api_key = request.query_params.get('api_key')
  check_id = request.query_params.get('check_id')
  if not api_key or not check_id:
    return Response(API_KEY_ERROR_MESSAGE, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
  try:
    printer = Printer.objects.get(api_key=api_key)
    check = Check.objects.get(pk=check_id, status='rendered')
  except Printer.DoesNotExist:
    return Response(API_KEY_ERROR_MESSAGE, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
  except Check.DoesNotExist:
    return Response(GET_CHECK_ERROR_MESSAGE, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

  with open(check.pdf_file.path, 'rb') as pdf_file:
    # check.status = 'printed'
    # check.save()
    return Response(pdf_file.read(),
                    headers={'Content-Disposition': 'attachment; filename={}'.format(check.filename())},
                    content_type='application/pdf')


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_checks(request):
  point_id = request.data.get('point_id')
  order_id = request.data.get('id')
  printer_query = Printer.objects.filter(point_id=point_id)
  check_query = Check.objects.filter(order_id=order_id)
  if check_query or not printer_query:
    return Response(CREATE_CHECK_ERROR_MESSAGE, status=status.HTTP_400_BAD_REQUEST)
  for printer in printer_query:
    check_data = {"type": printer.check_type,
                  "order": request.data,
                  "printer_id": printer.pk,
                  "order_id": order_id}
    serializer = CheckSerializer(data=check_data)
    if serializer.is_valid():
      serializer.save()
      total_amount = 0
      for x in request.data['items']:
        total_amount += x.get('unit_price') * x.get('quantity')
      check_data['total_amount'] = total_amount
      generate_pdf(check_data)
      return Response({'ok': 'Чеки успешно созданы'})
  return Response(CREATE_CHECK_ERROR_MESSAGE, status=status.HTTP_400_BAD_REQUEST)
