"""At the core of jsonrpcserver is the dispatcher, which processes JSON-RPC
requests and passes them to your functions.
"""
import logging
import json

from six import string_types

from jsonrpcserver.response import NotificationResponse, ExceptionResponse, \
    BatchResponse
from jsonrpcserver.request import Request
from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest
from jsonrpcserver.status import HTTP_STATUS_CODES

logger = logging.getLogger(__name__)
request_log = logging.getLogger(__name__+'.request')
response_log = logging.getLogger(__name__+'.response')


def _string_to_dict(request):
    """Convert a JSON-RPC request string, to a dictionary.

    :param request: The JSON-RPC request string.
    :raises ValueError: If the string cannot be parsed to JSON.
    :returns: The same request in dict form.
    """
    try:
        return json.loads(request)
    except ValueError:
        raise ParseError()


def dispatch(methods, request):
    """Process a JSON-RPC request, calling the requested method.

    .. code-block:: python

        >>> from jsonrpcserver import dispatch
        >>> response = dispatch([cube], {'jsonrpc': '2.0', 'method': 'cube', 'params': {'num': 3}, 'id': 1})

    :param methods:
        Collection of methods to dispatch to. Can be a ``list`` of functions, a
        ``dict`` of name:method pairs, or a :class:`~methods.Methods` object.
    :param request:
        A JSON-RPC request. Can be a JSON-serializable object, or a string.
        (Strings must be valid JSON - use double quotes!)
    :returns:
        A :mod:`response` object.
    """
    # Process the request
    response = None
    try:
        # Log the request
        request_log.info(request)
        # If the request is a string, convert it to a dict first
        if isinstance(request, string_types):
            request = _string_to_dict(request)
        # Batch requests
        if isinstance(request, list):
            # An empty list is invalid
            if len(request) == 0:
                raise InvalidRequest()
            # Process each request
            response = BatchResponse()
            for r in request:
                try:
                    req = Request(r)
                except InvalidRequest as e:
                    resp = ExceptionResponse(e, None)
                else:
                    resp = req.process(methods)
                response.append(resp)
            # Remove Notification responses
            response = BatchResponse(
                [r for r in response if not isinstance(
                    r, NotificationResponse)])
            # "Nothing is returned for all notification batches"
            if not response:
                response = NotificationResponse() # pylint: disable=redefined-variable-type
        # Single request
        else:
            response = Request(request).process(methods)
    except JsonRpcServerError as e:
        response = ExceptionResponse(e, None)
    # Batch requests can have mixed results, just return 200
    http_status = 200 if isinstance(request, list) else response.http_status
    # Log the response
    response_log.info(str(response), extra={
        'http_code': http_status,
        'http_reason': HTTP_STATUS_CODES[http_status]})
    return response
