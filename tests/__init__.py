import json


def first_ups_details(conf):
    ups_name = list(conf.keys())[0]
    address = conf[ups_name]['address']
    auth = (
        conf[ups_name]['user'],
        conf[ups_name]['password']
    )
    return address, auth, ups_name


def scrub_body():
    def before_record_request(request):
        try:
            body_json = json.loads(
                request.body.decode("utf-8").replace("'", '"')
            )
            body_json['username'] = 'username'
            body_json['password'] = 'password'
            request.body = str(body_json).replace("'", '"').encode('utf-8')
            return request
        except AttributeError:
            return request
    return before_record_request
