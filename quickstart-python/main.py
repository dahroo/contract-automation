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
                board_id = '6770440366'  
                group_id = 'topics'
                result = create_monday_item(MONDAY_API_KEY,board_id, group_id, item_name, posted_date, sol_num, item_link, deadline)
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
        <body>
            <h1>Create Solicitation Item on Monday.com</h1>
            <form action="/" method="post">
                <label for="solicitation_number">Solicitation Number:</label>
                <input type="text" id="solicitation_number" name="solicitation_number"><br><br>
                <label for="postedFrom">Posted From:</label>
                <input type="date" id="postedFrom" name="postedFrom"><br><br>
                <label for="postedTo">Posted To:</label>
                <input type="date" id="postedTo" name="postedTo"><br><br>
                <input type="submit" value="Create Solicitation">
            </form>
        </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
