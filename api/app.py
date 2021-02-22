import logging

from quart import Quart, request, abort, jsonify, make_response

import api.single as single
import api.bulk as bulk
import api.validate as validate

import config

app = Quart(__name__)
app.config['DEBUG'] = True

# TODO: Add API Key header
@app.route('/', methods=['GET'])
async def root():
    result = { "success": True }
    return jsonify(result)


@app.route('/api/v1/user/import', methods=['POST'])
async def single_user():
    api_key = request.headers.get('X-SYM-COMCON')

    if not api_key or api_key.lower() != config.api_key.lower():
        logging.error('Invalid API Key')
        return {"success": False, "message": "Invalid API Key"}, 401

    payload = await request.get_json()

    if not payload:
        abort(400)

    success, error_list = validate.validate_payload(payload)

    if not success:
        return make_response(jsonify(
            {
                "success": False,
                "errors": error_list
            }
        ), 400)

    is_success, err = single.import_single_user(payload)

    if not is_success:
        return{"success": False, "message": err}, 400
    else:
        return {'success': True}


@app.route('/api/v1/bulk/import', methods=['POST'])
async def mass_import():
    api_key = request.headers.get('X-SYM-COMCON')

    if not api_key or api_key.lower() != config.api_key.lower():
        logging.error('Invalid API Key')
        return {"success": False, "message": "Invalid API Key"}, 401

    payload = request.get_json()

    if not payload:
        abort(400)

    # This will actually take a CSV, not JSON.
    is_success, err = bulk.bulk_import_users(payload)

    if not is_success:
        return{"success": False, "message": err}, 400
    else:
        return {"success": True}

def start_app():
    app.run()