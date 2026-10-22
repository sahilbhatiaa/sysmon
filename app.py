import os
import platform
import time

import psutil
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Prime the counters so the first browser refresh shows real numbers.
psutil.cpu_percent(interval=None, percpu=True)
for _proc in psutil.process_iter():
    try:
        _proc.cpu_percent(None)
    except psutil.Error:
        pass


def top_processes(limit=8):
    procs = []
    attrs = ["pid", "name", "cpu_percent", "memory_percent"]
    for proc in psutil.process_iter(attrs):
        info = proc.info
        procs.append(
            {
                "pid": info["pid"],
                "name": info["name"] or "?",
                "cpu": round(info["cpu_percent"] or 0, 1),
                "memory": round(info["memory_percent"] or 0, 1),
            }
        )
    procs.sort(key=lambda p: (p["cpu"], p["memory"]), reverse=True)
    return procs[:limit]


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/stats")
def stats():
    per_cpu = psutil.cpu_percent(interval=None, percpu=True)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    return jsonify(
        hostname=platform.node(),
        uptime_seconds=int(time.time() - psutil.boot_time()),
        cpu_percent=round(sum(per_cpu) / len(per_cpu), 1),
        per_cpu=per_cpu,
        load_avg=[round(x, 2) for x in os.getloadavg()],
        memory_percent=mem.percent,
        memory_used=mem.used,
        memory_total=mem.total,
        disk_percent=disk.percent,
        disk_used=disk.used,
        disk_total=disk.total,
        net_sent=net.bytes_sent,
        net_recv=net.bytes_recv,
        processes=top_processes(),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
