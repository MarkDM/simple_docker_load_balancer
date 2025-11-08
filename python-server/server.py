from flask import Flask, Response, stream_with_context
import threading
import time
import sys
import os
import argparse
from datetime import datetime
import json

app = Flask(__name__)

# Global counter for tracking requests
request_counter = 0
current_rps = 0
counter_lock = threading.Lock()

def calculate_rps():
    """Background thread that calculates and prints RPS every second"""
    global request_counter, current_rps
    
    while True:
        time.sleep(1)
        
        with counter_lock:
            current_rps = request_counter
            request_counter = 0
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Current RPS: {current_rps}")

@app.route('/')
def index():
    """Main endpoint that increments the request counter"""
    global request_counter
    
    with counter_lock:
        request_counter += 1

    print("Current RPS:", current_rps)
    
    return {
        "status": "ok",
        "message": "Request received",
        "current_rps": current_rps
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "rps": current_rps}

@app.route('/rps')
def rps_stream():
    """Server-Sent Events endpoint that streams RPS data"""
    def generate():
        """Generator function that yields RPS data every second"""
        while True:
            # Send current RPS as SSE
            data = json.dumps({
                "rps": current_rps,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            yield f"data: {data}\n\n"
            time.sleep(1)
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/rps-display')
def rps_display():
    """HTML page that displays streaming RPS data"""
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPS Monitor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            min-width: 400px;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .rps-display {
            font-size: 5em;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .label {
            font-size: 1.2em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .timestamp {
            margin-top: 20px;
            color: #999;
            font-size: 0.9em;
        }
        .status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #4CAF50;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .connection-status {
            margin-top: 20px;
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>RPS Monitor</h1>
        <div class="label">Requests Per Second</div>
        <div class="rps-display" id="rps-value">--</div>
        <div class="connection-status">
            <span class="status" id="status"></span>
            <span id="status-text">Connecting...</span>
        </div>
        <div class="timestamp" id="timestamp">--</div>
    </div>

    <script>
        const rpsValue = document.getElementById('rps-value');
        const timestamp = document.getElementById('timestamp');
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status');

        // Create EventSource to connect to /rps endpoint
        const eventSource = new EventSource('/rps');

        eventSource.onmessage = function(event) {
            // Clear the display first
            rpsValue.textContent = '--';
            
            // Then update with new data
            const data = JSON.parse(event.data);
            rpsValue.textContent = data.rps;
            timestamp.textContent = 'Last update: ' + data.timestamp;
            statusText.textContent = 'Connected';
            statusDot.style.backgroundColor = '#4CAF50';
        };

        eventSource.onerror = function(error) {
            rpsValue.textContent = '--';
            statusText.textContent = 'Connection lost';
            statusDot.style.backgroundColor = '#f44336';
            console.error('EventSource error:', error);
        };

        eventSource.onopen = function() {
            statusText.textContent = 'Connected';
            statusDot.style.backgroundColor = '#4CAF50';
        };
    </script>
</body>
</html>
    '''
    return html

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Flask server with RPS tracking')
    parser.add_argument('-p', '--port', type=int, default=5000, 
                        help='Port number to run the server on (default: 5000)')
    args = parser.parse_args()
    
    # Get port from environment variable APP_PORT, fallback to command-line arg
    port = int(os.environ.get('APP_PORT', args.port))
    
    # Start the RPS calculation thread
    rps_thread = threading.Thread(target=calculate_rps, daemon=True)
    rps_thread.start()
    
    print(f"Starting Flask server with RPS tracking on port {port}...")
    print(f"Access the server at http://localhost:{port}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=True)
