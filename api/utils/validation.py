from rest_framework.views import exception_handler
from rest_framework.utils.serializer_helpers import ReturnList

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Update the structure of the response data.
    if response is not None:
        customized_response = {}
        customized_response['validations'] = {}

        errors = []
        if isinstance(response.data, ReturnList):
            errors = response.data
        else:
            errors.append(response.data)

        for error in errors:
            for key, value in error.items():
                if key ==  'detail':
                    if isinstance(value, list):
                        customized_response['detail']= ". ".join(value)
                    else:
                        customized_response['detail']= value

                else:
                    if type(value) is dict:
                        if key not in customized_response['validations']:
                            customized_response['validations'][key] = {}

                        for k,v in value.items():
                            if type(v) is list:
                                customized_response['validations'][key][k] = " ".join(v)
                            else:
                                customized_response['validations'][key][k] = v

                    elif type(value) is list:
                        customized_response['validations'][key] = {}
                        for inner_val in value:
                            if type(inner_val) is dict:
                                for k,v in inner_val.items():
                                    customized_response['validations'][key][k] = v
                            else:
                                error = ''.join(value)
                                customized_response['validations'][key]= error
                    else:
                        error = ''.join(value)
                        customized_response['validations'][key]= error

        response.data = customized_response

    return response