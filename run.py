#!/usr/bin/env python
"""
Script de lancement unifié pour Meal Manager.
Usage :
  uv run python run.py          -> Démarre l'application complète sur http://localhost:8000
  uv run python run.py --dev    -> Démarre le backend FastAPI (8000) et le frontend Vite (5173) en mode hot-reload
"""

import sys
import os
import subprocess
import time

# Forcer l'encodage UTF-8 pour la sortie console sous Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def build_frontend_if_needed():
    dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
    if not os.path.exists(dist_dir):
        print("Compilation initiale du frontend Vue 3...")
        subprocess.run(["npm", "run", "build"], cwd=os.path.join(os.path.dirname(__file__), "frontend"), check=True, shell=True)
        print("Frontend compile dans frontend/dist")


def run_production():
    build_frontend_if_needed()
    print("=" * 60)
    print("Meal Manager demarre avec succes !")
    print("Rendez-vous sur : http://127.0.0.1:8000")
    print("=" * 60)
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, log_level="info")


def run_dev():
    print("=" * 60)
    print("Demarrage de Meal Manager en mode DEVELOPPEMENT...")
    print("   - Backend API :   http://127.0.0.1:8000")
    print("   - Frontend Vite : http://127.0.0.1:5173")
    print("=" * 60)

    processes = []
    try:
        # 1. Démarrer FastAPI avec reload
        backend_cmd = ["uv", "run", "uvicorn", "backend.app.main:app", "--reload", "--port", "8000"]
        backend_proc = subprocess.Popen(backend_cmd, shell=True)
        processes.append(backend_proc)

        # 2. Démarrer Vite dev server
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
        frontend_cmd = ["npm", "run", "dev"]
        frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=True)
        processes.append(frontend_proc)

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArret des serveurs...")
    finally:
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    if "--dev" in sys.argv:
        run_dev()
    else:
        run_production()
