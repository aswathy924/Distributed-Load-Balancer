import subprocess
import time

processes = []

def start_process(command):
    return subprocess.Popen(command, shell=True)

try:
    print(" Starting backend servers...")

    #  Start backend servers on different ports
    processes.append(start_process("python backend/server.py 5001"))
    processes.append(start_process("python backend/server.py 5002"))
    processes.append(start_process("python backend/server.py 5003"))

    time.sleep(2)

    print(" Starting load balancer...")
    processes.append(start_process("python load_balancer/app.py"))

    print(" Starting dashboard...")
    processes.append(start_process("python dashboard/app.py"))

    print("\n System started!")
    print(" Load Balancer: http://localhost:5000")
    print(" Dashboard: http://localhost:7000")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down system...")

    for p in processes:
        p.terminate()