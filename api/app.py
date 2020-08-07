from flask import Flask, request, abort, jsonify, make_response

import api.single as single
import api.bulk as bulk

app = Flask(__name__)
app.config['DEBUG'] = True

# TODO: Add API Key header
@app.route('/', methods=['GET'])
def root():
    result = { "success": True }
    return jsonify(result)


@app.route('/api/v1/user/import', methods=['POST'])
def single_user():
    if not request.json:
        abort(400)

    is_success, err = single.import_single_user(request.json)

    if not is_success:
        return make_response(jsonify({'success': False, 'message': f'Error: {err}'}), 400)
    else:
        return jsonify({'success': True}), 201


@app.route('/api/v1/bulk/import', methods=['POST'])
def mass_import():
    if not request.json:
        abort(400)

    # This will actually take a CSV, not JSON.
    is_success, err = bulk.bulk_import_users(request.json)

    if not is_success:
        return make_response(jsonify({'success': False, 'message': f'Error: {err}'}), 400)
    else:
        return jsonify({'success': True}), 201

def start_app():
    app.run()