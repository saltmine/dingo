from dingo import server

def run_server():
  server.app.run('0.0.0.0', port=5002, debug=True)
