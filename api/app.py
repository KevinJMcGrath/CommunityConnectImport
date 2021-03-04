import asyncio

from quart import Quart, request

import api.single as single
import api.bulk as bulk
import api.parse as parse
import api.validate as validate


app = Quart(__name__)
app.config['DEBUG'] = True

# TODO: Add API Key header
@app.route('/api/v1/status', methods=['GET'])
async def root():
    return { "success": True }


@app.route('/api/v1/sponsor/validate', methods=['GET'])
async def validate_sponsor_code():
    if not validate.validate_api_key(api_request=request):
        return {"success": False, "message": "Invalid API Key"}, 401

    sponsor_code = request.args.get('sponsor_code')

    if not sponsor_code:
        return {"success": False, "message": "Missing sponsor code"}, 400

    success, result = single.lookup_sponsor_code(sponsor_code)

    if success:
        return {"success": True, "account_id": result}
    else:
        return {"success": False, "message": result}, 500


@app.route('/api/v1/user/import', methods=['POST'])
async def single_user():
    if not validate.validate_api_key(api_request=request):
        return {"success": False, "message": "Invalid API Key"}, 401

    payload_dict = await validate.validate_single_payload(api_request=request)

    if not payload_dict:
        err_msg = 'Unable to create user on Community Connect Service. Please contact support. CODE: 153-22'
        return {"success": False, "message": err_msg}, 500

    user = parse.parse_single_user(payload_dict)

    success, sponsor_result = single.lookup_sponsor_code(sponsor_code=user.sponsor_code)

    if not success:
        return {"success": False, "message": "Your sponsor code was invalid. Please contact support. CODE: 830-18"}, 500
    else:
        user.sponsor_sfdc_id = sponsor_result

    sym_id, err_msg = single.add_comcon_user(user)

    if sym_id:
        asyncio.get_running_loop().run_in_executor(None, single.finalize_user, user, sym_id)
        return {'success': True}
    else:
        return {"success": False, "message": err_msg}, 500



@app.route('/api/v1/bulk/import', methods=['POST'])
async def mass_import():
    if not validate.validate_api_key(api_request=request):
        return {"success": False, "message": "Invalid API Key"}, 401

    payload, err_msg = await validate.validate_bulk_payload(api_request=request)

    if not payload:
        return {"success": False, "message": err_msg}, 500

    user_list = parse.parse_bulk_users(payload)

    asyncio.get_running_loop().run_in_executor(None, bulk.bulk_import_users, user_list)
    return {'success': True}


@app.route('/api/v1/bulk/signup', methods=['POST'])
async def mass_signup():
    if not validate.validate_api_key(api_request=request):
        return {"success": False, "message": "Invalid API Key"}, 401

    payload, err_msg = await validate.validate_bulk_payload(api_request=request)

    if not payload:
        return {"success": False, "message": err_msg}, 500

    user_list = parse.parse_bulk_users(payload)

    asyncio.get_running_loop().run_in_executor(None, bulk.bulk_signup_users, user_list)
    return {'success': True}

def start_app():
    app.run()