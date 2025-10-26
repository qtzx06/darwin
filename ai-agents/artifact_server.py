"""
Darwin Artifact Viewer
Renders agent deliverables visually in the browser
"""
from flask import Flask, jsonify, Response
from flask_cors import CORS
from pathlib import Path
import threading
import re

app = Flask(__name__)
CORS(app)

# Path to artifacts directory
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"

def extract_html_css_js(agent_dir):
    """Extract HTML, CSS, and JS from agent deliverables."""
    html_content = ""
    css_content = ""
    js_content = ""
    
    for file_path in agent_dir.glob("*"):
        if not file_path.is_file():
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract from React/TSX files
            if file_path.suffix in ['.tsx', '.jsx', '.js', '.ts']:
                # Try to find JSX/HTML content
                jsx_matches = re.findall(r'return\s*\(([\s\S]*?)\);', content)
                for match in jsx_matches:
                    if '<' in match and '>' in match:
                        html_content += match
                
                # Extract CSS from styled components or inline styles
                style_matches = re.findall(r'style=\{\{([^}]+)\}\}', content)
                for match in style_matches:
                    css_content += match
            
            # Direct HTML files
            elif file_path.suffix in ['.html', '.htm']:
                html_content += content
            
            # Direct CSS files
            elif file_path.suffix == '.css':
                css_content += content
                
        except:
            continue
    
    return html_content, css_content, js_content

@app.route('/')
def index():
    """Main viewer page with live previews."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Darwin Live Deliverables</title>
    <script src="https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: white;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            padding: 30px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .agent-card {
            background: #1a1f3a;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
        }
        
        .agent-card:hover {
            transform: translateY(-5px);
        }
        
        .agent-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .agent-icon {
            font-size: 2.5em;
        }
        
        .agent-info h2 {
            font-size: 1.5em;
            margin-bottom: 5px;
        }
        
        .agent-info p {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        .preview-container {
            width: 100%;
            height: 500px;
            background: white;
            border: none;
            display: block;
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
            font-size: 1.5em;
        }
        
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .empty-state {
            text-align: center;
            padding: 100px 20px;
        }
        
        .empty-state h2 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        
        .empty-state p {
            font-size: 1.2em;
            opacity: 0.7;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧬 Darwin Live Deliverables</h1>
        <p>Visual rendering of agent work</p>
    </div>
    
    <div id="content" class="loading">
        <div class="spinner"></div>
        <div>Loading deliverables...</div>
    </div>
    
    <button class="refresh-btn" onclick="loadArtifacts()">🔄 Refresh</button>
    
    <script>
        async function loadArtifacts() {
            try {
                const response = await fetch('/api/renders');
                const artifacts = await response.json();
                
                const contentDiv = document.getElementById('content');
                
                if (artifacts.length === 0) {
                    contentDiv.innerHTML = `
                        <div class="empty-state">
                            <h2>🎨 No Deliverables Yet</h2>
                            <p>Start Darwin and agents will create visual deliverables here!</p>
                        </div>
                    `;
                    return;
                }
                
                const agentIcons = ['🔥', '👔', '😈', '🤓'];
                const agentsHTML = artifacts.map((agent, index) => `
                    <div class="agent-card">
                        <div class="agent-header">
                            <div class="agent-icon">${agentIcons[index % 4]}</div>
                            <div class="agent-info">
                                <h2>Agent ${index + 1}</h2>
                                <p>${agent.file_count} file(s)</p>
                            </div>
                        </div>
                        <iframe 
                            class="preview-container" 
                            src="/api/render/${agent.agent_name}"
                            sandbox="allow-scripts allow-same-origin"
                        ></iframe>
                    </div>
                `).join('');
                
                contentDiv.innerHTML = `<div class="agents-grid">${agentsHTML}</div>`;
            } catch (error) {
                document.getElementById('content').innerHTML = `
                    <div class="empty-state">
                        <h2>⚠️ Error Loading</h2>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        
        // Load on page load
        loadArtifacts();
        
        // Auto-refresh every 3 seconds
        setInterval(loadArtifacts, 3000);
    </script>
</body>
</html>"""

@app.route('/api/renders')
def get_renders():
    """Get list of all agent deliverables that can be rendered."""
    artifacts = []
    
    if not ARTIFACTS_DIR.exists():
        return jsonify([])
    
    for agent_dir in ARTIFACTS_DIR.glob("agent_*"):
        if not agent_dir.is_dir():
            continue
        
        files = list(agent_dir.glob("*"))
        if files:
            artifacts.append({
                'agent_name': agent_dir.name,
                'file_count': len(files)
            })
    
    return jsonify(artifacts)

@app.route('/api/render/<agent_name>')
def render_agent(agent_name):
    """Render the deliverable from an agent."""
    agent_dir = ARTIFACTS_DIR / agent_name
    
    if not agent_dir.exists():
        return "<html><body><h1>Agent not found</h1></body></html>"
    
    # Collect all code files
    html_parts = []
    css_parts = []
    js_parts = []
    react_code = []
    
    def clean_content(content):
        """Remove markdown code blocks and .txt artifacts."""
        # Remove markdown code fences
        content = re.sub(r'^```[\w]*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```[\w]*', '', content, flags=re.MULTILINE)
        content = re.sub(r'```$', '', content, flags=re.MULTILINE)
        return content.strip()
    
    for file_path in sorted(agent_dir.glob("*")):
        if not file_path.is_file():
            continue
        
        # Skip README files
        if 'README' in file_path.name.upper():
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            content = clean_content(content)
            
            # Determine actual file type (strip .txt if present)
            actual_name = file_path.name.replace('.txt', '')
            actual_ext = Path(actual_name).suffix.lower()
            
            # HTML files
            if actual_ext in ['.html', '.htm']:
                html_parts.append(content)
            
            # CSS files
            elif actual_ext == '.css':
                css_parts.append(content)
            
            # JavaScript files
            elif actual_ext == '.js' and 'three' not in actual_name.lower():
                js_parts.append(content)
            
            # React/TSX files - try to render with Babel
            elif actual_ext in ['.tsx', '.jsx']:
                react_code.append({
                    'name': actual_name,
                    'content': content
                })
        except:
            continue
    
    # If we have React components, create a React app
    if react_code:
        app_component = None
        scene_component = None
        
        for component in react_code:
            if 'App' in component['name'] or 'app' in component['name'].lower():
                app_component = component['content']
            elif 'Scene' in component['name'] or 'scene' in component['name'].lower():
                scene_component = component['content']
        
        # Use the most relevant component
        main_component = app_component or scene_component or (react_code[0]['content'] if react_code else '')
        
        # Extract CSS if embedded
        embedded_css = '\n'.join(css_parts)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/three@0.158.0/build/three.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        {embedded_css}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        {main_component}
        
        // Render the main component
        const root = ReactDOM.createRoot(document.getElementById('root'));
        const componentName = {main_component}.match(/(?:function|const)\\s+(\\w+)|export\\s+default\\s+(\\w+)/)?.[1] || 
                              {main_component}.match(/export\\s+default\\s+(\\w+)/)?.[1];
        
        if (typeof App !== 'undefined') {{
            root.render(<App />);
        }} else if (typeof ThreeScene !== 'undefined') {{
            root.render(<ThreeScene />);
        }} else if (typeof ThreeCubeScene !== 'undefined') {{
            root.render(<ThreeCubeScene />);
        }} else {{
            root.render(<div style={{{{padding: '20px', fontFamily: 'monospace'}}}}><h2>Component loaded but unable to render</h2><p>Check console for errors</p></div>);
        }}
    </script>
</body>
</html>"""
    
    # If we have plain HTML/CSS/JS
    elif html_parts or css_parts or js_parts:
        combined_html = '\n'.join(html_parts)
        combined_css = '\n'.join(css_parts)
        combined_js = '\n'.join(js_parts)
        
        # If HTML is complete (has doctype), use it as-is
        if '<!DOCTYPE' in combined_html or '<html' in combined_html:
            return combined_html
        
        # Otherwise, wrap it
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        {combined_css}
    </style>
</head>
<body>
    {combined_html}
    <script>
        {combined_js}
    </script>
</body>
</html>"""
    
    # No renderable content found
    return """<html>
<body style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: monospace; background: #1a1a2e; color: white;">
    <div style="text-align: center;">
        <h2>📄 No Renderable Content</h2>
        <p>Agent hasn't created visual deliverables yet</p>
    </div>
</body>
</html>"""

def start_server(port=5000):
    """Start the Flask server."""
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_background_server(port=5000):
    """Start the server in a background thread."""
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    return server_thread

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎨 DARWIN ARTIFACT VIEWER")
    print("="*70)
    print(f"\n📦 Serving from: {ARTIFACTS_DIR.absolute()}")
    print(f"\n🌐 Open in browser:")
    print(f"   → http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
