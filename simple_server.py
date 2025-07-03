import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs
import asyncio
from numpy import true_divide
import svn_util
import config_path
import loc_check
import os
# --- Configuration ---
PORT = 8090 # The port your server will listen on
HOST = "0.0.0.0" # "0.0.0.0" for all interfaces, "127.0.0.1" for local only

# --- Custom Request Handler ---
class SimpleCustomHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom HTTP request handler that extends SimpleHTTPRequestHandler
    to add dynamic logic for specific paths, while falling back to
    static file serving for other requests.
    """

    def do_GET(self):
        super().do_GET()

    def do_POST(self):
        print('receive request')
        if(self.path == '/check_cn'):
            ret_code = svn_util.checkout_subprocess(config_path.repository_local_path)
            try:
                if(ret_code.success):
                    checker = loc_check.LocalizeChecker()
                    checker.excel_name = config_path.path_in_repo
                    coroutine = checker.check_CN(local_path=config_path.repository_local_path, is_pub=True)
                    rst = asyncio.run(coroutine)
                    response = {
                        'error': rst,
                    }
                    self._send_json_response(200, response)
                else:
                    self._send_error_response(400, ret_code.error_content)
            except Exception as e:
                self._send_error_response(400, str(e))
        else:
            self._send_error_response(400, 'invalid path')
        
    # --- Helper Methods for Sending Responses ---
    def _send_response_header(self, status_code, content_type):
        """Sends the HTTP status code and Content-Type header."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def _send_json_response(self, status_code, data):
        """Sends a JSON response."""
        self._send_response_header(status_code, 'application/json')
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_html_response(self, status_code, html_content):
        """Sends an HTML response."""
        self._send_response_header(status_code, 'text/html')
        self.wfile.write(html_content.encode('utf-8'))

    def _send_text_response(self, status_code, text_content):
        """Sends a plain text response."""
        self._send_response_header(status_code, 'text/plain')
        self.wfile.write(text_content.encode('utf-8'))

    def _send_error_response(self, status_code, message):
        """Sends an error response with a plain text message."""
        self.send_error(status_code, message)

    def log_message(self, format, *args):
        """Override to customize or suppress server log messages."""
        # You can add custom logging here, e.g., to a file.
        # By default, it prints to standard error.
        print(f"[ACCESS] {self.address_string()} - {format % args}")

# --- Server Setup ---
def run_server():
    """Starts the multi-threaded HTTP server."""
    # ThreadingTCPServer allows handling multiple requests concurrently
    with socketserver.ThreadingTCPServer((HOST, PORT), SimpleCustomHandler) as httpd:
        print(f"--- Serving HTTP on {HOST}:{PORT} ---")
        print("Available Routes:")
        print(f"  - Static files: http://localhost:{PORT}/ (e.g., index.html)")
        print(f"  - GET /api/time: http://localhost:{PORT}/api/time")
        print(f"  - GET /greet?name=YourName: http://localhost:{PORT}/greet?name=Alice")
        print(f"  - GET /info: http://localhost:{PORT}/info")
        print(f"  - POST /api/submit_data: Use curl or Postman to send JSON data.")
        print(f"    Example curl: curl -X POST -H 'Content-Type: application/json' -d '{{\"item\": \"book\", \"qty\": 2}}' http://localhost:{PORT}/api/submit_data")
        print("\nPress Ctrl+C to stop the server.")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n--- Server shutting down ---")
            httpd.shutdown()
            httpd.server_close()

# --- Main Execution ---
if __name__ == "__main__":
    os.chdir(config_path.repository_local_path)
    run_server()