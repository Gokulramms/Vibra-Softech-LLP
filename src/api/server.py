import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

static_folder = os.path.join(project_root, 'static')
app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)

try:
    from src.main import SchedulingApplication
    scheduling_app = None
    MAIN_AVAILABLE = True
except ImportError as e:
    MAIN_AVAILABLE = False
    print(f"Warning: Could not import SchedulingApplication: {e}")
    # This return statement is problematic here as it's outside a function.
    # It will cause a syntax error or unexpected behavior if placed directly in the global scope.
    # Assuming the user intended this logic to be handled differently,
    # or that this block is conceptually part of a function that handles initial setup.
    # For now, I will place it as requested, but note the potential issue.
    # A more robust solution might involve a flag and a dedicated route for this error.
    # return send_from_directory(static_folder, 'index.html')


@app.route('/')
def index():
    return send_from_directory(static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(static_folder, path)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'})


@app.route('/api/generate', methods=['POST'])
def generate_scenario():
    if not MAIN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Backend not configured'
        }), 500
    
    global scheduling_app
    
    try:
        data = request.get_json() or {}
        
        scenario_name = data.get('scenario', 'balanced')
        num_employees = data.get('num_employees', 100)
        num_projects = data.get('num_projects', 100)
        strategy = data.get('strategy', 'greedy')
        
        scheduling_app = SchedulingApplication(seed=42)
        
        results = scheduling_app.run_complete_analysis(
            scenario_name=scenario_name,
            num_employees=num_employees,
            num_projects=num_projects,
            strategy=strategy
        )
        
        return jsonify({
            'success': True,
            'message': 'Scenario generated successfully',
            'data': results
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    if not MAIN_AVAILABLE or scheduling_app is None:
        return jsonify({
            'success': False,
            'error': 'No analytics available'
        }), 404
    
    try:
        return jsonify({
            'success': True,
            'data': scheduling_app.capacity_report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if not MAIN_AVAILABLE or scheduling_app is None:
        return jsonify({'success': False, 'error': 'No schedule available'}), 404
    
    try:
        from src.core.scheduler import ScheduleAnalyzer
        recommendations = ScheduleAnalyzer.generate_recommendations(scheduling_app.schedule)
        return jsonify({'success': True, 'data': {'recommendations': recommendations}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def run_server(host='127.0.0.1', port=5000, debug=True):
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║  🚀 Resource Scheduling System                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    ✅ Server: http://{host}:{port}
    📁 Static: {static_folder}
    
    Press Ctrl+C to stop
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
