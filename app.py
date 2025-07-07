import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "python-api"))

from flask import Flask, request, jsonify
from shotgun_api3.shotgun import Shotgun
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Para que Google Sheets pueda hacer peticiones

@app.route("/shotgrid_estado", methods=["POST"])
def shotgrid_estado():
    data = request.get_json()
    shot_ids = data.get("shot_ids", [])
    script_name = data["script_name"]
    script_key = data["script_key"]

    sg = Shotgun(
        "https://garagevfx.shotgrid.autodesk.com",
        script_name,
        script_key
    )

    filtros = [['id', 'in', shot_ids]]
    campos = ['id', 'code', 'sg_status_list']
    shots = sg.find("Shot", filtros, campos)

    resultado = {
        str(shot['id']): {
            "code": shot["code"],
            "estado": shot["sg_status_list"]
        } for shot in shots
    }
    return jsonify(resultado)
