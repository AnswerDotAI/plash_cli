import os
from jupyterlab.labapp import LabApp
from jupyter_server.auth import passwd

LabApp.launch_instance(argv=['--ServerApp.port=5001', '--ServerApp.ip=0.0.0.0', 
    f'--ServerApp.password={passwd('not-very-secret')}', '--ServerApp.token='])
