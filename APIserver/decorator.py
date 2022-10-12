from APIserver.helper import sha256
import json
import os
""" check if apikey  """
def apiValidate(view):
    def wrap(params):
        key = sha256(params['apikey'])
        apikey = os.environ['apikey']
        if key == apikey:
            return view()
        else:
            return json.dumps({'errorMessage' : 'invalid authorization'})
    return wrap

# useful decorator
