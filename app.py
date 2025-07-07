from flask import Flask, request, jsonify
from shotgun_api3.shotgun import Shotgun
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Para que Google Sheets pueda hacer peticiones

@app.route("/shotgrid_estado", methods=["POST"])
def shotgrid_estado():
    data = request.get_json()
    shot_codes = data.get("shot_codes", [])
    script_name = data["script_name"]
    script_key = data["script_key"]

    sg = Shotgun(
        "https://garagevfx.shotgrid.autodesk.com",
        script_name,
        script_key
    )

    filtros = [['code', 'in', shot_codes]]
    campos = ['code', 'sg_status_list']
    shots = sg.find("Shot", filtros, campos)

    resultado = {shot['code']: shot['sg_status_list'] for shot in shots}
    return jsonify(resultado)
