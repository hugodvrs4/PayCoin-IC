from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet
from xrpl.account import get_next_valid_seq_number
import io
import base64
from PIL import Image
from pyzbar import pyzbar
from urllib.parse import urlparse, parse_qs
import qrcode

app = Flask(__name__)
CORS(app)

# Configuration du client XRPL (Testnet)
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Génération d'un portefeuille aléatoire (DÉCONSEILLÉ POUR UNE APPLICATION RÉELLE)
wallet = Wallet.create()
print(f"Adresse du portefeuille (exemple) : {wallet.address}")
print(f"Phrase de départ (exemple - NE PAS UTILISER EN PRODUCTION) : {wallet.seed}")

@app.route('/api/generate_qr_code', methods=['POST'])
def generate_qr_code():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400

    try:
        recipient_address = data.get('recipient_address')
        amount = str(data.get('amount'))

        if not recipient_address:
            return jsonify({'error': 'Recipient address is required'}), 400
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400

        qr_data = f"xrpl:{recipient_address}?amount={amount}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        response = make_response(img_bytes.getvalue())
        response.headers['Content-Type'] = 'image/png'

        return response
    except Exception as e:
        print(f"Erreur lors de la génération du QR code : {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400

    try:
        qr_code_base64 = data.get('qr_code')
        if not qr_code_base64:
            return jsonify({'error': 'QR code data is missing'}), 400

        try:
            img_bytes = base64.b64decode(qr_code_base64)
            img = Image.open(io.BytesIO(img_bytes))

            decoded_objects = pyzbar.decode(img)
            if not decoded_objects:
                return jsonify({'error': 'No QR code found in the image'}), 400

            qr_data = decoded_objects[0].data.decode("utf-8")
        except (ValueError, OSError, IndexError) as e:
            return jsonify({'error': f'Error decoding QR code: {e}'}), 400

        try:
            parsed_url = urlparse(qr_data)
            if parsed_url.scheme != "xrpl":
                raise ValueError("Invalid QR code scheme")

            query_params = parse_qs(parsed_url.query)
            recipient_address = parsed_url.path[1:]
            amount_str = query_params.get("amount", [None])[0]

            if not recipient_address or not amount_str:
                raise ValueError("Recipient address or amount missing")
        except ValueError as e:
            return jsonify({'error': f'Invalid QR code format: {e}'}), 400

        try:
            sequence_number = get_next_valid_seq_number(wallet.address, client)
            payment = Payment(
                account=wallet.address,
                destination=recipient_address,
                amount=str(amount_str),
                sequence=sequence_number,
            )

            signed_tx = wallet.sign(payment)
            response = client.submit(signed_tx)

            print(response.result)
            return jsonify({'status': 'success', 'message': 'Payment processed'}), 200
        except Exception as e:
            print(f"Error submitting transaction: {e}")
            return jsonify({'status': 'error', 'message': f'Transaction failed: {e}'}), 500
    except Exception as e:
        print(f"Error processing payment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)