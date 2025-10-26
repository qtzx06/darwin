"""
Simple HTTP server to serve Darwin artifacts
"""
import http.server
import socketserver
import threading
import json
from pathlib import Path


class ArtifactHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve artifacts with proper CORS headers"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()
    
    def log_message(self, format, *args):
        """Suppress request logging"""
        pass


class ArtifactServer:
    """Simple HTTP server for viewing artifacts"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self):
        """Start the HTTP server in a background thread"""
        try:
            # Change to ai-agents directory to serve files (parent of src)
            import os
            ai_agents_dir = Path(__file__).parent.parent
            os.chdir(ai_agents_dir)
            
            print(f"📁 Serving from: {os.getcwd()}")
            
            self.server = socketserver.TCPServer(("", self.port), ArtifactHTTPHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            print(f"\n🌐 Artifact Viewer: http://localhost:{self.port}/artifact_viewer.html")
            print(f"   Artifacts directory: http://localhost:{self.port}/artifacts/\n")
            
            return True
        except Exception as e:
            print(f"⚠️  Could not start artifact server: {e}")
            return False
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()


def start_artifact_server(port=8080):
    """Start the artifact server"""
    server = ArtifactServer(port)
    if server.start():
        return server
    return None


if __name__ == "__main__":
    # Test the server
    server = start_artifact_server()
    if server:
        print("Press Ctrl+C to stop...")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")
            server.stop()
