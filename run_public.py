import os
from pyngrok import ngrok
from app import create_app


def main():
    auth_token = os.getenv('NGROK_AUTH_TOKEN')
    if not auth_token:
        print('Please set NGROK_AUTH_TOKEN environment variable first.')
        print('Example (PowerShell):')
        print('  $env:NGROK_AUTH_TOKEN = "your_token_here"')
        print('  python run_public.py')
        print('Or configure ngrok with: ngrok authtoken YOUR_TOKEN')
        return

    ngrok.set_auth_token(auth_token)
    tunnel = ngrok.connect(5000, 'http')
    print(f'Public URL: {tunnel.public_url}')
    print('Running local Flask app on http://0.0.0.0:5000')

    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
