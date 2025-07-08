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
    try:
        data = request.get_json()
        print("📥 JSON recibido:", data)  # <-- VERIFICAR qué llega

        shot_codes = data.get("shot_codes", [])
        script_name = data["script_name"]
        script_key = data["script_key"]

        print("✅ Script name:", script_name)
        print("✅ Shot codes:", shot_codes)

        sg = Shotgun(
            "https://garagevfx.shotgrid.autodesk.com",
            script_name,
            script_key
        )

        filtros = [['code', 'in', shot_codes]]
        campos = ['code', 'sg_status_list']
        shots = sg.find("Shot", filtros, campos)

        print("🔍 Resultados:", shots)

        resultado = {shot['code']: shot['sg_status_list'] for shot in shots}
        return jsonify(resultado)

    except Exception as e:
        print("❌ Error en el servidor:", str(e))
        return jsonify({"error": str(e)}), 500
