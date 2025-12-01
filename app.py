import gradio as gr
import json
import time
from typing import Dict, Any, List, Tuple
import base64
from io import BytesIO
from PIL import Image
import os
import sys
import shutil

# ------------------------------------------------------------------
# Monkeypatch gradio_client to tolerate boolean JSON schemas (workaround)
# Some gradio/gradio_client versions raise TypeError when a schema is a
# boolean; patch `get_type` to handle that case gracefully.
try:
    import gradio_client.utils as _client_utils
    if hasattr(_client_utils, "get_type"):
        _orig_get_type = _client_utils.get_type
        def _patched_get_type(schema):
            try:
                if isinstance(schema, bool):
                    return "Any"
                return _orig_get_type(schema)
            except TypeError:
                return "Any"
        _client_utils.get_type = _patched_get_type
        # Also guard the top-level conversion function to avoid API schema parse errors
        if hasattr(_client_utils, "json_schema_to_python_type"):
            _orig_json_schema_to_python_type = _client_utils.json_schema_to_python_type
            def _patched_json_schema_to_python_type(schema):
                try:
                    return _orig_json_schema_to_python_type(schema)
                except Exception:
                    return "Any"
            _client_utils.json_schema_to_python_type = _patched_json_schema_to_python_type
except Exception:
    # If gradio_client isn't available or patching fails, continue normally
    pass
# ------------------------------------------------------------------

# ---------------------------------------------------------
# IMPORT AGENT SYSTEM
# Note: Ensure agent_system.py is in the same folder
# ---------------------------------------------------------
try:
    from agent_system import (
        MasterControllerUltimate,
        memory_bank,
        session_service,
        metrics_collector,
        eval_pipeline
    )
    # Initialize the system
    master_controller = MasterControllerUltimate()
    print("✅ Agent System Loaded Successfully")
except ImportError as e:
    print(f"❌ Error importing agent_system: {e}")
    print("Please make sure 'agent_system.py' is in the same folder.")
    sys.exit(1)

# ---------------------------------------------------------
# CUSTOM CSS (Tailwind Style)
# ---------------------------------------------------------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --dark-bg: #0f172a;
    --darker-bg: #0a0e1a;
    --card-bg: #1e293b;
    --border-color: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
}

* { font-family: 'Inter', sans-serif !important; }

/* --- 1. MAIN BACKGROUND (Dark) --- */
body, .gradio-container {
    background-color: var(--darker-bg) !important;
    color: var(--text-primary) !important;
}

/* --- 2. CONTAINERS (Blocks/Panels) --- */
/* Force all Gradio containers to be Dark Blue-Grey */
.block, .panel, .group, .box, .form {
    background-color: var(--card-bg) !important;
    border-color: var(--border-color) !important;
}

/* --- 3. TEXT VISIBILITY (White on Dark) --- */
/* Ensure all text inside dark blocks is white */
p, h1, h2, h3, h4, h5, h6, span, label, li, td, th, strong, em, .prose {
    color: var(--text-primary) !important;
}

/* --- 4. INPUTS (Dark Background, White Text) --- */
/* Explicitly style inputs to match the dark theme */
input, textarea, select, .gr-box, .gr-input {
    background-color: var(--darker-bg) !important;
    color: white !important;
    border: 1px solid var(--border-color) !important;
}
/* Placeholder text should be lighter gray */
::placeholder {
    color: var(--text-secondary) !important;
    opacity: 0.8;
}

/* --- 5. EXCEPTIONS (White Backgrounds) --- */
/* If any element specifically needs a white background (rare), force text to black */
.white-bg {
    background-color: white !important;
    color: black !important;
}

/* --- 6. BUTTONS --- */
button.primary {
    background: var(--primary-gradient) !important;
    color: white !important;
    border: none !important;
}

/* Header Styling */
.app-header {
    text-align: center;
    padding: 2rem 1rem;
    background: var(--primary-gradient);
    border-radius: 1rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
}

.app-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(to right, #ffffff, #f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.app-subtitle { font-size: 1.25rem; color: rgba(255, 255, 255, 0.9); }

/* Result Box Styling */
.result-box {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 0.75rem !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    backdrop-filter: blur(10px) !important;
}

.severity-high { border-left: 4px solid #ef4444 !important; background: rgba(239, 68, 68, 0.1) !important; }
.severity-medium { border-left: 4px solid #f59e0b !important; background: rgba(245, 158, 11, 0.1) !important; }
.severity-low { border-left: 4px solid #10b981 !important; background: rgba(16, 185, 129, 0.1) !important; }

/* Panic Button */
.panic-btn {
    background: var(--danger-gradient) !important;
    color: white !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    height: 150px !important;
    border-radius: 1rem !important;
    border: 2px solid rgba(255,255,255,0.2) !important;
    box-shadow: 0 0 30px rgba(245, 87, 108, 0.4) !important;
}
.panic-btn:hover { transform: scale(1.02); }

/* Inputs and Buttons */
.gr-button.primary { background: var(--primary-gradient) !important; border: none !important; }
.gr-textbox, .gr-dropdown { background: var(--card-bg) !important; border: 1px solid var(--border-color) !important; }

/* Badges */
.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 99px; font-weight: 600; font-size: 0.85rem; margin: 0.2rem; }
.badge-danger { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; }
.badge-warning { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid #f59e0b; }
.badge-success { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid #10b981; }
"""

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def format_analysis_result(results: Dict[str, Any]) -> str:
    """Format analysis results into HTML"""
    if not results: return "<p>No analysis results</p>"
    
    html = "<div class='result-box'>"
    
    # 1. Threat Detection
    if "threat" in results:
        threat = results["threat"]
        severity = threat.get("severity", 1)
        severity_class = "severity-high" if severity >= 4 else "severity-medium" if severity >= 2 else "severity-low"
        
        html += f"""
        <div class='{severity_class}' style='padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem;'>
            <h3 style='color: var(--text-primary); margin-bottom: 0.5rem;'>🚨 Threat Analysis</h3>
            <p><strong>Category:</strong> {threat.get('exact_threat_category', 'Unknown')}</p>
            <p><strong>Severity:</strong> <span class='badge badge-danger'>{severity}/5</span></p>
            <p><strong>Action:</strong> {threat.get('recommended_action', 'N/A')}</p>
        </div>
        """
    
    # 2. Manipulation
    if "manipulation" in results:
        manip = results["manipulation"]
        trust_score = manip.get("trust_score", 50)
        badge_class = "badge-danger" if trust_score < 30 else "badge-warning" if trust_score < 70 else "badge-success"
        
        html += f"""
        <div style='padding: 1rem; margin-bottom: 1rem; background: rgba(236, 72, 153, 0.1); border-radius: 0.5rem; border-left: 4px solid #ec4899;'>
            <h3 style='color: var(--text-primary); margin-bottom: 0.5rem;'>💔 Manipulation Analysis</h3>
            <p><strong>Trust Score:</strong> <span class='badge {badge_class}'>{trust_score}/100</span></p>
            <p><strong>Explanation:</strong> {manip.get('explanation', 'N/A')}</p>
        </div>
        """

    # 3. Red Flags
    if "redflag" in results:
        redflag = results["redflag"]
        html += f"""
        <div style='padding: 1rem; margin-bottom: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 0.5rem; border-left: 4px solid #ef4444;'>
            <h3 style='color: var(--text-primary); margin-bottom: 0.5rem;'>🚩 Red Flag Alert</h3>
            <p><strong>Level:</strong> {redflag.get('red_flag_level', 'Unknown')}</p>
            <p><strong>Intent Score:</strong> {redflag.get('lust_intent_score', 0)}/100</p>
        </div>
        """

    # 4. Legal Support
    if "legal" in results:
        legal = results["legal"]
        laws = legal.get('applicable_laws', [])
        steps = legal.get('complaint_steps', [])
        rights = legal.get('rights_of_the_victim', [])
        
        html += f"""
        <div style='padding: 1rem; margin-bottom: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 0.5rem; border-left: 4px solid #3b82f6;'>
            <h3 style='color: var(--text-primary); margin-bottom: 0.5rem;'>⚖️ Legal Guidance</h3>
            <p><strong>Applicable Laws:</strong> {', '.join(laws) if isinstance(laws, list) else laws}</p>
            <p><strong>Complaint Steps:</strong></p>
            <ul style='margin-left: 1.5rem; list-style-type: disc;'>
                {''.join([f'<li>{step}</li>' for step in steps]) if isinstance(steps, list) else f'<li>{steps}</li>'}
            </ul>
            <p style='margin-top: 0.5rem;'><strong>Police Contact:</strong> {legal.get('police_contact_structure', 'N/A')}</p>
            <p><strong>Your Rights:</strong> {', '.join(rights) if isinstance(rights, list) else rights}</p>
        </div>
        """

    # 5. System Intelligence (Memory & Internet)
    if "system_context" in results:
        sys_ctx = results["system_context"]
        html += f"""
        <div style='padding: 1rem; margin-bottom: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; border-left: 4px solid #6366f1;'>
            <h3 style='color: var(--text-primary); margin-bottom: 0.5rem;'>🧠 System Intelligence</h3>
            <p><strong>Memory:</strong> {sys_ctx.get('memory', 'N/A')}</p>
            <p><strong>Internet Check:</strong> {sys_ctx.get('internet', 'N/A')}</p>
        </div>
        """

    html += "</div>"
    return html

def analyze_text(text: str, session_id: str) -> Tuple[str, str]:
    if not text.strip(): return "Please enter text.", ""
    try:
        # Run Analysis
        results = master_controller.pipeline_ultimate(text)
        
        # Save History
        session_service.add_history(session_id, "user", text)
        session_service.add_history(session_id, "system", str(results))
        
        html = format_analysis_result(results)
        summary = f"**Threat:** {results.get('threat', {}).get('severity')}/5 | **Trust:** {results.get('manipulation', {}).get('trust_score')}/100"
        return html, summary
    except Exception as e:
        return f"<div class='result-box severity-high'>Error: {str(e)}</div>", "Analysis Failed"

def handle_file_upload(files, session_id: str) -> Tuple[str, str]:
    if not files: return "No files.", ""
    
    html = "<div class='result-box'><h3>📎 File Analysis</h3>"
    summary_text = ""
    
    for file in files:
        filename = os.path.basename(file.name) if hasattr(file, 'name') else str(file)
        
        # Simulate analysis by passing a description to the agent
        # In a real system, we would use Vision API here.
        description = f"Analyze this file: {filename}. It might contain evidence of harassment or threats."
        
        # Run Pipeline
        results = master_controller.pipeline_ultimate(description)
        
        # Save to History
        session_service.add_history(session_id, "user", f"[File Upload] {filename}")
        session_service.add_history(session_id, "system", str(results))
        
        threat_sev = results.get("threat", {}).get("severity", 0)
        status_icon = "🔴" if threat_sev >= 4 else "🟠" if threat_sev >= 2 else "🟢"
        
        html += f"""
        <div style='margin-bottom: 1rem; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem;'>
            <p><strong>{status_icon} {filename}</strong></p>
            <p style='font-size: 0.9rem; color: #cbd5e1;'>{results.get('system_context', {}).get('internet', 'Checked')}</p>
            <p style='font-size: 0.9rem;'>Threat Level: {threat_sev}/5</p>
        </div>
        """
        summary_text += f"{filename}: Level {threat_sev} | "
        
    html += "</div>"
    return html, summary_text

def save_evidence(text_evidence, file_evidence, session_id):
    if not text_evidence and not file_evidence:
        return "<div class='result-box'>⚠️ Please provide text or files to save.</div>"
        
    vault_dir = os.path.join("evidence_vault", str(session_id))
    os.makedirs(vault_dir, exist_ok=True)
    
    saved_items = []
    
    # Save Text
    if text_evidence and text_evidence.strip():
        timestamp = int(time.time())
        text_filename = f"evidence_text_{timestamp}.txt"
        text_path = os.path.join(vault_dir, text_filename)
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text_evidence)
        saved_items.append(f"📝 Text Note ({text_filename})")

    # Save Files
    if file_evidence:
        for file_obj in file_evidence:
            try:
                # Handle Gradio file object or path
                src_path = file_obj.name if hasattr(file_obj, 'name') else file_obj
                filename = os.path.basename(src_path)
                dest_path = os.path.join(vault_dir, filename)
                shutil.copy2(src_path, dest_path)
                saved_items.append(f"📎 {filename}")
            except Exception as e:
                saved_items.append(f"❌ Error saving file: {str(e)}")
            
    html = "<div class='result-box' style='border-left: 4px solid #4ade80; background: rgba(74, 222, 128, 0.1);'>"
    html += "<h3 style='color: #4ade80'>✅ Evidence Secured Successfully</h3>"
    html += f"<p><strong>Vault Location:</strong> <code>{os.path.abspath(vault_dir)}</code></p>"
    html += "<ul>"
    for item in saved_items:
        html += f"<li>{item}</li>"
    html += "</ul></div>"
    return html

def get_dashboard() -> str:
    return f"<div class='result-box'><pre>{metrics_collector.get_dashboard()}</pre></div>"

def get_legal_support(country, situation, session_id):
    return analyze_text(f"Location: {country}. Legal Help needed for: {situation}", session_id)

# ---------------------------------------------------------
# GRADIO INTERFACE CONSTRUCTION
# ---------------------------------------------------------
with gr.Blocks(css=CUSTOM_CSS, title="SHAKTI SHIELD") as demo:
    
    # Create a real session id value (call the factory once)
    session_id = gr.State(value=session_service.create_session())

    # Header
    gr.HTML("""
        <div class='app-header'>
            <h1 class='app-title'>👑 SHAKTI SHIELD</h1>
            <p class='app-subtitle'>AI-Powered Women's Safety Guardian</p>
        </div>
    """)

    with gr.Tabs():
        
        # Tab 1: Chat
        with gr.Tab("💬 Analysis"):
            with gr.Row():
                with gr.Column():
                    txt_in = gr.Textbox(label="Message/Chat", lines=5, placeholder="Paste suspicious text here...")
                    btn_analyze = gr.Button("🔍 Analyze", variant="primary")
                    out_summary = gr.Markdown(label="Summary")
                with gr.Column():
                    out_html = gr.HTML(label="Detailed Report")
            
            btn_analyze.click(analyze_text, [txt_in, session_id], [out_html, out_summary])

        # Tab 2: Files
        with gr.Tab("📁 Media"):
            file_in = gr.File(file_count="multiple", label="Upload Images/Audio/Video")
            btn_upload = gr.Button("📤 Analyze Files", variant="primary")
            out_file = gr.HTML()
            out_file_md = gr.Markdown(label="Files Summary")
            btn_upload.click(handle_file_upload, [file_in, session_id], [out_file, out_file_md])

        # Tab 3: Evidence Vault
        with gr.Tab("🗄️ Evidence Vault"):
            gr.Markdown("### 🔒 Secure Evidence Locker")
            gr.Markdown("Upload screenshots, recordings, or paste chat logs here. They will be saved locally for legal use.")
            
            with gr.Row():
                with gr.Column():
                    txt_evidence = gr.Textbox(label="Paste Chat Logs / Notes", lines=8, placeholder="Paste conversation history or notes here...")
                with gr.Column():
                    file_evidence = gr.File(label="Upload Media Evidence", file_count="multiple")
            
            btn_save = gr.Button("💾 Save to Vault", variant="primary")
            out_save = gr.HTML()
            
            btn_save.click(save_evidence, [txt_evidence, file_evidence, session_id], [out_save])

        # Tab 4: Legal
        with gr.Tab("⚖️ Legal"):
            with gr.Row():
                dd_country = gr.Dropdown(["India", "USA", "UK", "Other"], label="Country", value="India")
                txt_situation = gr.Textbox(label="Describe Situation")
            btn_legal = gr.Button("Get Legal Help", variant="primary")
            out_legal = gr.HTML()
            out_legal_md = gr.Markdown(label="Legal Summary")
            btn_legal.click(get_legal_support, [dd_country, txt_situation, session_id], [out_legal, out_legal_md])

        # Tab 5: Metrics
        with gr.Tab("📊 System"):
            out_metrics = gr.HTML()
            btn_refresh = gr.Button("Refresh")
            btn_refresh.click(get_dashboard, None, [out_metrics])
            demo.load(get_dashboard, None, [out_metrics])

# ---------------------------------------------------------
# LAUNCH CONFIGURATION (UPDATED FIX)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Shakti Shield AI...")
    print("👉 Please wait for the local URL to appear below.")
    
    # Queue enable karne se heavy traffic handle hota hai
    demo.queue() 
    
    try:
        demo.launch(
            server_name="127.0.0.1",  # Localhost
            share=False,              # No public link (Safe mode)
            inbrowser=True,           # Auto-open browser
            show_api=False,           # <--- CRITICAL FIX: Disables the buggy API page
            show_error=True           # Shows errors in console
        )
    except Exception as e:
        print(f"❌ Launch Error: {e}")
        print("💡 TIP: If the port is busy, close the terminal and try again.")