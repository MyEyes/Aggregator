from flask import jsonify

def bad_request(error = "Unexpected Error", msg = "Unexpected Error"):
    return jsonify(
        {
            'status': 'Error',
            'error': error,
            'msg': msg
        })