from flask import Flask, render_template, request, jsonify
from scripts.scraper import scrape_property_data
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    block = request.form.get('block', '')
    lot = request.form.get('lot', '')
    qualifier = request.form.get('qualifier', '')
    location = request.form.get('location', '')

    try:
        properties = scrape_property_data(block, lot, qualifier, location)
        return jsonify({"success": True, "data": properties})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"success": False, "error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)