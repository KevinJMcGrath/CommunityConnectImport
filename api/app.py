from quart import Quart, request, abort, jsonify, make_response

import api.single as single
import api.bulk as bulk
import api.validate as validate

app = Quart(__name__)
app.config['DEBUG'] = True

# TODO: Add API Key header
@app.route('/', methods=['GET'])
async def root():
    result = { "success": True }
    return jsonify(result)


@app.route('/api/v1/user/import', methods=['POST'])
async def single_user():
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
        return make_response(jsonify({'success': False, 'message': err}), 400)
    else:
        return jsonify({'success': True}), 201


@app.route('/api/v1/bulk/import', methods=['POST'])
async def mass_import():
    payload = request.get_json()

    if not payload:
        abort(400)

    # This will actually take a CSV, not JSON.
    is_success, err = bulk.bulk_import_users(payload)

    if not is_success:
        return make_response(jsonify({'success': False, 'message': f'Error: {err}'}), 400)
    else:
        return jsonify({'success': True}), 201

def start_app():
    app.run()