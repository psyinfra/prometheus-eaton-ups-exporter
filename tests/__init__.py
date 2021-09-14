import os
import json

CASSETTE_DIR = os.path.join(
    os.getcwd(), "tests", "fixtures", "cassettes"
)


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
