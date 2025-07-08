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
    shot_codes = data.get("shot_codes", [])
    script_name = data["script_name"]
    script_key = data["script_key"]

    sg = Shotgun(
        "https://garagevfx.shotgrid.autodesk.com",
        script_name,
        script_key
    )

    filtros = [['code', 'in', shot_codes]]
    campos = ['id', 'code', 'sg_status_list']  # ← se agregó 'id'

    shots = sg.find("Shot", filtros, campos)
    resultado = {}

    for shot in shots:
        code = shot['code']
        resultado[code] = {
            "shot_status": shot.get('sg_status_list', '')
        }

        # Usamos el ID correcto para relacionar tareas
        task_filters = [['entity', 'is', {'type': 'Shot', 'id': shot['id']}]]
        task_fields = ['step.Step.short_name', 'sg_status_list']
        tasks = sg.find("Task", task_filters, task_fields)

        task_statuses = {}
        for task in tasks:
            step = task.get('step.Step.short_name')
            status = task.get('sg_status_list')
            if step and status:
                task_statuses[step] = status

        resultado[code]["task_status"] = task_statuses

    return jsonify(resultado)

    except Exception as e:
        print("❌ Error en el servidor:", str(e))
        return jsonify({"error": str(e)}), 500
