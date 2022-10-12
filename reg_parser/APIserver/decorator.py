from database.connect import USERDB
from APIserver.helper import sha256
import json

""" check if apikey and user grade is valid """
def apiValidate(grade, required, option=None):
    def wrap2(view):
        def wrap1(params, *args, **kwargs):
            keys = list(params.keys())
            if set(required) <= set(keys):
                key = sha256(params['apikey'])
                db = USERDB()
                db.startSession()
                user_table = db.Base.classes.user
                user = db.session.query(user_table.id, user_table.grade).filter(user_table.apikey == key).first()
                db.session.close()
                db.dispose()
                if user and user.grade >= grade:
                    result = view(params, *args, **kwargs)
                    if type(result) != dict or not result.get('errorMessage'):
                        result = {'result' : result}
                    return json.dumps(result, ensure_ascii=False).encode('utf8')
                else:
                    return json.dumps({'errorMessage' : 'invalid authorization'})
            return json.dumps({'errorMessage' : 'Not enough parameter'})
        return wrap1
    return wrap2

# useful decorator
