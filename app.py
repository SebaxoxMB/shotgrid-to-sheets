import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "python-api"))

from flask import Flask, request, jsonify
from shotgun_api3.shotgun import Shotgun
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/shotgrid_estado", methods=["POST"])
def shotgrid_estado():
    try:
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
        campos = ['code', 'sg_status_list', 'sg_cut_duration', 'sg_cut_in', 'sg_cut_out']

        shots = sg.find("Shot", filtros, campos)

        resultado = {}

        for shot in shots:
            code = shot['code']
            resultado[code] = {
                "shot_status": shot.get('sg_status_list', ''),
                "cut_duration": shot.get('sg_cut_duration'),
                "cut_in": shot.get('sg_cut_in'),
                "cut_out": shot.get('sg_cut_out')
            }

            task_filters = [['entity', 'is', {'type': 'Shot', 'id': shot["id"]}]]
            task_fields = ['step.Step.short_name', 'sg_status_list', 'start_date', 'due_date', 'task_assignees']

            tasks = sg.find("Task", task_filters, task_fields)

            task_statuses = {}
            for task in tasks:
                step = task.get('step.Step.short_name')
                if step == "CMP":
                    task_statuses["task_status"] = task.get("sg_status_list")

                    asignado = ""
                    if task.get("task_assignees"):
                        nombre = task["task_assignees"][0]["name"]
                        asignado = nombre.split()[0]

                    task_statuses["assigned_to"] = asignado
                    task_statuses["start_date"] = task.get("start_date")
                    task_statuses["due_date"] = task.get("due_date")

            resultado[code]["task_comp"] = task_statuses

        return jsonify(resultado)

    except Exception as e:
        print("❌ Error en el servidor:", str(e))
        return jsonify({"error": str(e)}), 500
