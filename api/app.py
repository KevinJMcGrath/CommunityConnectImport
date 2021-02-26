import asyncio
import logging

from quart import Quart, request, abort, jsonify, make_response

import api.single as single
import api.bulk as bulk
import api.validate as validate
import config



app = Quart(__name__)
app.config['DEBUG'] = True

# TODO: Add API Key header
@app.route('/api/v1/status', methods=['GET'])
async def root():
    return { "success": True }


@app.route('/api/v1/user/import', methods=['POST'])
async def single_user():
    if not validate.validate_api_key(api_request=request):
        return {"success": False, "message": "Invalid API Key"}, 401

    user = await validate.validate_single_payload(api_request=request)

    if not user:
        err_msg = 'Unable to create user on Community Connect Service. Please contact support. CODE: 153-22'
        return {"success": False, "message": err_msg}, 400

    if not single.check_sponsor_name(user):
        return {"success": False, "message": "Your sponsor id was invalid. Please contact support. CODE: 830-18"}

    sym_id, err_msg = single.add_comcon_user(user)

    if sym_id:
        asyncio.get_running_loop().run_in_executor(None, single.finalize_user, user, sym_id)
        return {'success': True}
    else:
        return {"success": False, "message": err_msg}, 500



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
        return{"success": False, "message": err}, 500
    else:
        return {"success": True}


@app.route('/api/v1/bulk/signup', methods=['POST'])
async def mass_signup():
    api_key = request.headers.get('X-SYM-COMCON')

    if not api_key or api_key.lower() != config.api_key.lower():
        logging.error('Invalid API Key')
        return {"success": False, "message": "Invalid API Key"}, 401

    payload = request.get_json()

    if not payload:
        abort(400)

    return {"success": True}

def start_app():
    app.run()