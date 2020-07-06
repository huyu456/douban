from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


def custom_exception_handler(exc, context):
    """
    error_code : 10001, 验证码验证出错
    :param exc:
    :param context:
    :return:
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    return response


class CustomExection(APIException):
    status_code = status.HTTP_200_OK
    default_detail = _('A server is ok.')
    default_code = 'request ok'

    def __init__(self, detail=None, code='', error_code=None):
        assert detail, '必填字段'
        self.detail = {'msg': detail, 'code': code, 'error_code': error_code}

    def __str__(self):
        return str(self.detail)