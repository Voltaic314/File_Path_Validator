from quart import Quart, jsonify
from FPV.API.routes.path.clean import clean_bp
from FPV.API.routes.path.isValid import isvalid_bp
from FPV.API.routes.path.dynamic import dynamic_bp

app = Quart(__name__)

# Register blueprints
app.register_blueprint(clean_bp, url_prefix="/api/v1")
app.register_blueprint(isvalid_bp, url_prefix="/api/v1")
app.register_blueprint(dynamic_bp, url_prefix="/api/v1")

@app.route("/")
async def root():
    return jsonify({
        "message": "File Path Validator API (Quart)",
        "version": "1.0.0",
        "endpoints": {
            "clean": "/api/v1/clean",
            "validate": "/api/v1/isValid",
            "dynamic": {
                "add_part": "/api/v1/path/add",
                "remove_part": "/api/v1/path/remove",
                "build_path": "/api/v1/path/build"
            }
        },
        "supported_services": [
            "windows", "macos", "linux", 
            "dropbox", "box", "egnyte", 
            "onedrive", "sharepoint", "sharefile"
        ]
    })

@app.route("/health")
async def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
