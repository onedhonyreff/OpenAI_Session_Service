from flask import Flask, jsonify, request
import cloudscraper
import uuid
import asyncio

app = Flask(__name__)


def run_async(func):
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(func)


async def get_new_session():
    try:
        url = "https://chat.openai.com/backend-anon/sentinel/chat-requirements"
        new_device_id = str(uuid.uuid4())
        scraper = cloudscraper.create_scraper()
        headers = {
            'oai-device-id': new_device_id
        }
        response = scraper.post(
            url,
            headers=headers
        )

        if response.status_code != 200:
            return None, response.status_code

        session = response.json()
        session['deviceId'] = new_device_id
        return session, response.status_code
    except Exception as e:
        print(e)
        return None, 500


@app.route('/v1/new-openai-session')
def handle_new_session():
    session, status_code = run_async(get_new_session())

    if status_code == 200:
        return jsonify({
            'status': True,
            'data': session
        }), status_code
    elif status_code == 500:
        return jsonify({
            'status': False,
            'error': {
                'message': 'Internal Server Error',
            }
        }), 500
    else:
        return jsonify({
            'status': False,
            'error': {
                'message': 'An error occurred while connecting with OpenAI. Please try again.',
            }
        }), status_code


@app.route('/')
def health_check():
    return "OK", 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': False,
        'error': {
            'message': f'The requested endpoint ({request.method.upper()} {request.path}) was not found. Please make sure to use "http://localhost:8000/v1" as the base URL.',
            'type': 'invalid_request_error'
        }
    }), 404