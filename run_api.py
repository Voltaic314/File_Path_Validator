#!/usr/bin/env python3
"""
Simple script to run the File Path Validator API server using Quart.
"""

from FPV.API.api import app

if __name__ == "__main__":
    print("Starting File Path Validator API server (Quart)...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host="0.0.0.0", 
        port=8000,
        debug=True  # Enable debug mode for development
    ) 