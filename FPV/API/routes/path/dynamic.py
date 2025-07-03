from quart import Blueprint, request, jsonify
import importlib

dynamic_bp = Blueprint('dynamic', __name__)
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

@dynamic_bp.route('/path/add', methods=['POST'])
async def add_path_part():
    data = await request.get_json()
    service = data.get('service', '').lower()
    base_path = data.get('base_path', '')
    parts_to_add = data.get('parts', [])
    existing_errors = data.get('errors', [])
    validate = data.get('validate', True)
    relative = data.get('relative', True)
    file_added = data.get('file_added', False)
    sep = data.get('sep', None)

    if service not in service_mapping:
        return jsonify({
            "success": False, 
            "updated_path": "", 
            "new_errors": [], 
            "all_errors": [],
            "error": f"Unsupported service: {service}"
        }), 400

    if not parts_to_add:
        return jsonify({
            "success": False,
            "updated_path": base_path,
            "new_errors": [],
            "all_errors": existing_errors,
            "error": "No parts provided to add"
        }), 400

    try:
        fpv_module = importlib.import_module("FPV.Helpers")
        fpv_class = getattr(fpv_module, service_mapping[service])
        
        # Create validator from existing state to avoid revalidation
        kwargs = {"relative": relative, "file_added": file_added}
        if sep:
            kwargs["sep"] = sep
            
        validator = fpv_class.from_state(base_path, existing_errors=existing_errors, **kwargs)
        
        # Add parts one by one with incremental validation
        new_errors = []
        for i, part in enumerate(parts_to_add):
            is_file = file_added and i == len(parts_to_add) - 1
            validator.add_part(part, is_file=is_file, validate_new_only=True)
            
            if validate:
                # Get validation issues for the newly added part only
                part_issues = validator.get_issues_for_part(len(validator._path_helper.parts) - 1)
                new_errors.extend(part_issues)
        
        # Get all errors (existing + new)
        all_errors = validator.get_logs()["issues"]
        
        return jsonify({
            "success": True,
            "updated_path": validator.get_full_path(),
            "new_errors": new_errors,
            "all_errors": all_errors,
            "path_parts": [part["part"] for part in validator._path_helper.parts],
            "error": None
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "updated_path": "",
            "new_errors": [],
            "all_errors": existing_errors,
            "error": str(e)
        }), 500

@dynamic_bp.route('/path/remove', methods=['POST'])
async def remove_path_part():
    data = await request.get_json()
    service = data.get('service', '').lower()
    base_path = data.get('base_path', '')
    part_index = data.get('part_index')
    existing_errors = data.get('errors', [])
    relative = data.get('relative', True)
    file_added = data.get('file_added', False)
    sep = data.get('sep', None)

    if service not in service_mapping:
        return jsonify({
            "success": False,
            "updated_path": "",
            "remaining_errors": [],
            "error": f"Unsupported service: {service}"
        }), 400

    if part_index is None:
        return jsonify({
            "success": False,
            "updated_path": base_path,
            "remaining_errors": existing_errors,
            "error": "part_index is required"
        }), 400

    try:
        fpv_module = importlib.import_module("FPV.Helpers")
        fpv_class = getattr(fpv_module, service_mapping[service])
        
        # Create validator from existing state
        kwargs = {"relative": relative, "file_added": file_added}
        if sep:
            kwargs["sep"] = sep
            
        validator = fpv_class.from_state(base_path, existing_errors=existing_errors, **kwargs)
        
        # Remove the specified part with automatic error cleanup
        if part_index < len(validator._path_helper.parts):
            removed_part = validator._path_helper.parts[part_index]["part"]
            validator.remove_part(part_index, remove_related_errors=True)
            remaining_errors = validator.get_logs()["issues"]
        else:
            remaining_errors = existing_errors
            removed_part = None

        return jsonify({
            "success": True,
            "updated_path": validator.get_full_path(),
            "remaining_errors": remaining_errors,
            "removed_part": removed_part,
            "path_parts": [part["part"] for part in validator._path_helper.parts],
            "error": None
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "updated_path": "",
            "remaining_errors": existing_errors,
            "error": str(e)
        }), 500

@dynamic_bp.route('/path/build', methods=['POST'])
async def build_path_incrementally():
    """
    Build a path incrementally with full validation tracking.
    This is useful for building paths step by step while maintaining error state.
    """
    data = await request.get_json()
    service = data.get('service', '').lower()
    root_path = data.get('root_path', '')
    path_parts = data.get('path_parts', [])
    relative = data.get('relative', True)
    file_added = data.get('file_added', False)
    sep = data.get('sep', None)

    if service not in service_mapping:
        return jsonify({
            "success": False,
            "final_path": "",
            "all_errors": [],
            "step_errors": [],
            "error": f"Unsupported service: {service}"
        }), 400

    try:
        fpv_module = importlib.import_module("FPV.Helpers")
        fpv_class = getattr(fpv_module, service_mapping[service])
        
        # Create validator with root path
        kwargs = {"relative": relative, "file_added": file_added}
        if sep:
            kwargs["sep"] = sep
            
        validator = fpv_class.from_state(root_path, **kwargs)
        
        step_errors = []
        all_errors = []
        
        # Build path step by step with incremental validation
        for i, part in enumerate(path_parts):
            is_file = file_added and i == len(path_parts) - 1
            validator.add_part(part, is_file=is_file, validate_new_only=True)
            
            # Get validation issues for this step only
            step_issues = validator.get_issues_for_part(len(validator._path_helper.parts) - 1)
            step_errors.append({
                "step": i + 1,
                "part": part,
                "issues": step_issues
            })
            all_errors.extend(step_issues)

        return jsonify({
            "success": True,
            "final_path": validator.get_full_path(),
            "all_errors": all_errors,
            "step_errors": step_errors,
            "path_parts": [part["part"] for part in validator._path_helper.parts],
            "error": None
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "final_path": "",
            "all_errors": [],
            "step_errors": [],
            "error": str(e)
        }), 500 