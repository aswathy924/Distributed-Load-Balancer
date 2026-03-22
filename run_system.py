import subprocess
import time

processes = []

def start_process(command):
    return subprocess.Popen(command, shell=True)

try:
    print("Starting backend servers...")

    processes.append(start_process("python backend/server.py 1"))
    processes.append(start_process("python backend/server.py 2"))
    processes.append(start_process("python backend/server.py 3"))

    time.sleep(2)

    print("Starting load balancer...")
    processes.append(start_process("python load_balancer/balancer.py"))

    print("\nSystem started!")
    print("Open browser: http://localhost:8000/dashboard")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down system...")

    for p in processes:
        p.terminate()