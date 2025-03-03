from flask import Flask, jsonify, request
from main_project import script

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def call_script():
    result = script.tua_funzione()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)