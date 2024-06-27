import os

SAM_GOV_API_KEY = os.getenv('SAM_GOV_API_KEY')
MONDAY_API_KEY = os.getenv('MONDAY_API_KEY')

from services.samgov_service import get_opportunities
from services.monday_service import create_monday_item

from datetime import datetime

from flask import Flask, jsonify
from flask import request
from werkzeug.exceptions import HTTPException

from errors import handle_monday_code_api_error, handle_general_http_exception, \
    MondayCodeAPIError, handle_base_error, BaseError
from routes import worker_queue_bp, mail_bp, auth_bp

app = Flask(__name__)
app.register_blueprint(worker_queue_bp)
app.register_blueprint(mail_bp, url_prefix="/mail")
app.register_blueprint(auth_bp, url_prefix="/auth")

app.register_error_handler(HTTPException, handle_general_http_exception)
app.register_error_handler(BaseError, handle_base_error)
app.register_error_handler(MondayCodeAPIError, handle_monday_code_api_error)

@app.route("/", methods=["POST"])
def create_solicitation():
    try:
        solicitation_number = request.form['solicitation_number']
        print(solicitation_number)
        posted_from = request.form['postedFrom']
        posted_to = request.form['postedTo']
        posted_from_formatted = datetime.strptime(posted_from, '%Y-%m-%d').strftime('%m/%d/%Y')
        posted_to_formatted = datetime.strptime(posted_to, '%Y-%m-%d').strftime('%m/%d/%Y')
        opportunities = get_opportunities(SAM_GOV_API_KEY, solicitation_number, posted_from_formatted, posted_to_formatted)
        
        
        if opportunities:
            for item in opportunities['opportunitiesData']:
                item_name = item['title']
                sol_num = item['solicitationNumber']
                posted_date = item['postedDate']
                deadline = item.get('responseDeadLine', 'N/A')
                item_link = item['uiLink']
                naics = str(item['naicsCode'])
                board_id = '6763054292'  
                group_id = 'topics'
                result = create_monday_item(MONDAY_API_KEY,board_id, group_id, item_name, posted_date, sol_num, item_link, deadline, naics)
                return jsonify(result), 200
        else:
            return jsonify({"error": "No opportunities found or bad data received."}), 404
    except KeyError as e:
        return jsonify({'error': 'Missing form data: ' + str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/create_solicitation", methods=["GET"])
def display_form():
    return '''
    <html>
    <head>
        <style>
            body {
                background-color: #333;
                color: #ccc;
                font-family: 'Arial', sans-serif;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            form {
                background-color: #222;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
            }
            label {
                margin-bottom: 10px;
                display: block;
            }
            input[type="text"], input[type="date"] {
                width: 100%;
                padding: 8px;
                margin-bottom: 20px;
                border-radius: 4px;
                border: none;
                background-color: #555;
                color: #ddd;
            }
            input[type="submit"] {
                width: 100%;
                padding: 10px;
                border-radius: 5px;
                border: none;
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <form action="/" method="post">
            <h1 style="color: #fff;">Import a Contract into Monday</h1>
            <label for="solicitation_number">Solicitation Number:</label>
            <input type="text" id="solicitation_number" name="solicitation_number"><br>
            <label for="postedFrom">Posted From:</label>
            <input type="date" id="postedFrom" name="postedFrom"><br>
            <label for="postedTo">Posted To:</label>
            <input type="date" id="postedTo" name="postedTo"><br>
            <input type="submit" value="Create Solicitation">
        </form>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
