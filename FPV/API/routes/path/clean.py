from quart import Blueprint, request, jsonify
import importlib

clean_bp = Blueprint('clean', __name__)

@clean_bp.route('/clean', methods=['POST'])
async def clean_path():
    data = await request.get_json()
    service = data.get('service', '').lower()
    path = data.get('path')
    relative = data.get('relative', True)
    file_added = data.get('file_added', False)
    sep = data.get('sep', None)

    service_mapping = {
        "windows": "FPV_Windows",
        "macos": "FPV_MacOS",
        "linux": "FPV_Linux",
        "dropbox": "FPV_Dropbox",
        "box": "FPV_Box",
        "egnyte": "FPV_Egnyte",
        "onedrive": "FPV_OneDrive",
        "sharepoint": "FPV_SharePoint",
        "sharefile": "FPV_ShareFile"
    }

    if service not in service_mapping:
        return jsonify({"success": False, "cleaned_path": "", "logs": {}, "error": f"Unsupported service: {service}"}), 400

    fpv_module = importlib.import_module("FPV.Helpers")
    fpv_class = getattr(fpv_module, service_mapping[service])
    kwargs = {"auto_clean": False, "auto_validate": False, "relative": relative, "file_added": file_added}
    if sep:
        kwargs["sep"] = sep
    try:
        validator = fpv_class(path, **kwargs)
        cleaned_path = validator.clean()
        logs = validator.get_logs()
        return jsonify({
            "success": True,
            "cleaned_path": cleaned_path,
            "logs": logs,
            "error": None
        })
    except Exception as e:
        return jsonify({"success": False, "cleaned_path": "", "logs": {}, "error": str(e)}), 500
