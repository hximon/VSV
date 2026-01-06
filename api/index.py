from flask import Flask, jsonify, render_template, request
import psutil
import time
import requests
import logging
import os
import subprocess
import threading
from datetime import datetime
from collections import deque

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurations
URL_TO_PING = os.getenv("URL_TO_PING", "https://google.com")

# Global variable to store process info
start_sh_process = {
    "pid": None,
    "started_at": None,
    "status": "not_started",
    "process": None,
    "stdout_lines": deque(maxlen=500),  # Keep last 500 lines
    "stderr_lines": deque(maxlen=500),  # Keep last 500 error lines
    "exit_code": None
}

def read_stream(stream, line_queue, stream_name):
    """Read from a stream and store lines in queue."""
    try:
        for line in iter(stream.readline, b''):
            decoded_line = line.decode('utf-8', errors='replace').rstrip()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            line_queue.append(f"[{timestamp}] {decoded_line}")
            logger.info(f"{stream_name}: {decoded_line}")
        stream.close()
    except Exception as e:
        logger.error(f"Error reading {stream_name}: {e}")

def format_uptime(seconds):
    """Format uptime in human-readable format."""
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

def get_ping(url=URL_TO_PING):
    """Get ping response time."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # ms
        if response.status_code == 200:
            return f"{response_time:.0f} ms"
        else:
            return "Failed"
    except requests.RequestException as e:
        logger.error(f"Ping error: {e}")
        return "Failed"

def get_bandwidth_usage():
    """Get network bandwidth usage."""
    try:
        counters = psutil.net_io_counters()
        upload_bandwidth = round(counters.bytes_sent / (1024 ** 2), 2)  # MB
        download_bandwidth = round(counters.bytes_recv / (1024 ** 2), 2)  # MB
        
        return {
            "upload_bandwidth": upload_bandwidth,
            "download_bandwidth": download_bandwidth
        }
    except Exception as e:
        logger.error(f"Bandwidth error: {e}")
        return {
            "upload_bandwidth": 0,
            "download_bandwidth": 0
        }

def get_server_status():
    """Get comprehensive server status."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        # Use the current drive on Windows, or '/' on Linux/Mac
        disk_path = os.path.abspath(os.sep)
        disk = psutil.disk_usage(disk_path)

        disk_used = round(disk.used / (1024 ** 3), 2)  # GB
        disk_total = round(disk.total / (1024 ** 3), 2)
        disk_percent = disk.percent

        memory_total = round(memory.total / (1024 ** 3), 2)
        memory_used = round(memory.used / (1024 ** 3), 2)
        memory_percent = memory.percent

        uptime_seconds = time.time() - psutil.boot_time()
        uptime_human = format_uptime(uptime_seconds)

        current_tasks = len(list(psutil.process_iter()))
        ping_status = get_ping()

        bandwidth = get_bandwidth_usage()

        # SSH URL not available on Vercel serverless
        ssh_url = "SSH not available on Vercel (serverless environment)"

        return {
            "status": "ok",
            "uptime": uptime_human,
            "ping_status": ping_status,
            "current_tasks": current_tasks,
            "cpu_usage": cpu_usage,
            "memory_total": memory_total,
            "memory_used": memory_used,
            "memory_percent": memory_percent,
            "disk_total": disk_total,
            "disk_used": disk_used,
            "disk_percent": disk_percent,
            **bandwidth,
            "ssh_url": ssh_url,
        }
    except Exception as e:
        logger.error(f"Error fetching server status: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/regenerate', methods=['POST'])
def regenerate():
    """SSH regeneration not supported on Vercel serverless."""
    return jsonify({
        "status": "error",
        "message": "SSH access is not available on Vercel serverless environment. Consider using a VPS or container platform instead."
    }), 400 

@app.route('/start-shell', methods=['POST'])
def start_shell():
    """Start the start.sh script in background."""
    global start_sh_process
    
    try:
        # Check if script exists
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'start.sh')
        
        if not os.path.exists(script_path):
            return jsonify({
                "status": "error",
                "message": f"start.sh not found at {script_path}"
            }), 404
        
        # Check if already running
        if start_sh_process["pid"] and start_sh_process["process"]:
            try:
                proc = psutil.Process(start_sh_process["pid"])
                if proc.is_running():
                    return jsonify({
                        "status": "error",
                        "message": "start.sh is already running",
                        "pid": start_sh_process["pid"]
                    }), 400
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process doesn't exist anymore, can start new one
                pass
        
        # Clear previous logs
        start_sh_process["stdout_lines"].clear()
        start_sh_process["stderr_lines"].clear()
        start_sh_process["exit_code"] = None
        
        # Start the process
        process = subprocess.Popen(
            ['bash', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            cwd=os.path.dirname(script_path),
            preexec_fn=os.setpgrp if os.name != 'nt' else None
        )
        
        start_sh_process["pid"] = process.pid
        start_sh_process["started_at"] = datetime.now().isoformat()
        start_sh_process["status"] = "running"
        start_sh_process["process"] = process
        
        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(
            target=read_stream,
            args=(process.stdout, start_sh_process["stdout_lines"], "STDOUT"),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=read_stream,
            args=(process.stderr, start_sh_process["stderr_lines"], "STDERR"),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Monitor process exit in background
        def monitor_process():
            process.wait()
            start_sh_process["exit_code"] = process.returncode
            if process.returncode != 0:
                start_sh_process["status"] = "stopped_with_error"
            else:
                start_sh_process["status"] = "stopped"
            logger.info(f"Process exited with code: {process.returncode}")
        
        monitor_thread = threading.Thread(target=monitor_process, daemon=True)
        monitor_thread.start()
        
        logger.info(f"Started start.sh with PID: {process.pid}")
        
        return jsonify({
            "status": "success",
            "message": "start.sh started successfully",
            "pid": process.pid,
            "started_at": start_sh_process["started_at"]
        })
        
    except Exception as e:
        logger.error(f"Error starting start.sh: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/shell-stats', methods=['GET'])
def shell_stats():
    """Get stats of the running start.sh process."""
    global start_sh_process
    
    if not start_sh_process["pid"]:
        return jsonify({
            "status": "not_started",
            "message": "Process not started yet",
            "exit_code": None
        })
    
    try:
        proc = psutil.Process(start_sh_process["pid"])
        
        if not proc.is_running():
            return jsonify({
                "status": start_sh_process["status"],
                "message": "Process has stopped",
                "pid": start_sh_process["pid"],
                "exit_code": start_sh_process["exit_code"]
            })
        
        # Get process stats
        with proc.oneshot():
            cpu_percent = proc.cpu_percent(interval=0.1)
            memory_info = proc.memory_info()
            memory_mb = round(memory_info.rss / (1024 * 1024), 2)
            num_threads = proc.num_threads()
            create_time = proc.create_time()
            
            # Calculate uptime
            uptime_seconds = time.time() - create_time
            uptime_formatted = format_uptime(uptime_seconds)
            
            # Get process status
            status = proc.status()
            
            # Get child processes count
            children = proc.children(recursive=True)
            num_children = len(children)
        
        return jsonify({
            "status": "running",
            "pid": start_sh_process["pid"],
            "started_at": start_sh_process["started_at"],
            "uptime": uptime_formatted,
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "num_threads": num_threads,
            "process_status": status,
            "num_children": num_children,
            "exit_code": None
        })
        
    except psutil.NoSuchProcess:
        return jsonify({
            "status": start_sh_process["status"],
            "message": "Process no longer exists",
            "pid": start_sh_process["pid"],
            "exit_code": start_sh_process["exit_code"]
        })
    except Exception as e:
        logger.error(f"Error getting process stats: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "exit_code": None
        }), 500

@app.route('/shell-logs', methods=['GET'])
def shell_logs():
    """Get logs from the running start.sh process."""
    global start_sh_process
    
    # Get query parameters for filtering
    lines = request.args.get('lines', default=100, type=int)
    log_type = request.args.get('type', default='all', type=str)  # all, stdout, stderr
    
    # Limit max lines to prevent memory issues
    lines = min(lines, 500)
    
    stdout_logs = list(start_sh_process["stdout_lines"])[-lines:] if log_type in ['all', 'stdout'] else []
    stderr_logs = list(start_sh_process["stderr_lines"])[-lines:] if log_type in ['all', 'stderr'] else []
    
    return jsonify({
        "pid": start_sh_process["pid"],
        "status": start_sh_process["status"],
        "stdout": stdout_logs,
        "stderr": stderr_logs,
        "stdout_count": len(start_sh_process["stdout_lines"]),
        "stderr_count": len(start_sh_process["stderr_lines"]),
        "exit_code": start_sh_process["exit_code"]
    })

@app.route('/status', methods=['GET'])
def status():
    """Get server status endpoint."""
    return jsonify(get_server_status())

@app.route('/')
def home():
    """Home page."""
    return render_template("index.html")

# Vercel serverless handler
def handler(request):
    """Handler for Vercel serverless functions."""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

# For local development
if __name__ == "__main__":
    app.run(debug=True)
