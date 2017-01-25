"""Import ``config`` to configure, for example:

::

    from jsonrpcserver import config
    config.debug = True
"""
#pylint:disable=invalid-name

#: Validate requests against the JSON-RPC schema. Disable to speed up
#: processing.
schema_validation = True

#: Include more information in error messages.
debug = False

#: Convert any camelCase keys in a request to under_score before processing.
#: Saves time by cleaning up key names for you. *Recommended*
convert_camel_case = False

#: Log requests
log_requests = True

#: Log responses
log_responses = True
