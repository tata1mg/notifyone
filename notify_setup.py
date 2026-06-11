import subprocess
import os
import sys
import time
import urllib.request
from sys import platform
from gateway_setup import setup_gateway
from core_setup import setup_core
from handler_setup import setup_handler
from dashboard_setup import setup_dashboard

sys_platform = sys.argv[1] if len(sys.argv) > 1 else "linux/amd64"
cms_api_endpoint = sys.argv[2] if len(sys.argv) > 2 else ""

print("Building for system platform - {}".format(sys_platform))

_docker_check_res = subprocess.run(['docker info'], shell=True, capture_output=True)
if _docker_check_res.returncode != 0:
    print("Either Docker is not installed or not running\n"+(str(_docker_check_res.stderr.decode('utf-8'))))
    exit(1)


print("\n Setting up Postgres on Docker\n")
_res = subprocess.run(['docker pull postgres:14.5'],  shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)

_stat = subprocess.run(['docker rm --force postgres_notify'], shell=True)
_res = subprocess.run(["docker run  --detach -p5432:5432 -e POSTGRES_PASSWORD='postgres' -e POSTGRES_USER=postgres --name postgres_notify postgres:14.5"],  shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)

print("\n Setting up Redis on Docker\n")
_stat = subprocess.run(['docker rm --force redis_notify'], shell=True)
_res = subprocess.run(["docker run --detach --name redis_notify -p 6379:6379 -d redis"],  shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)


print("\n Setting up moto-server\n")
_moto_already_up = False
try:
    urllib.request.urlopen("http://localhost:15000")
    _moto_already_up = True
    print("moto-server already running on port 5000, skipping start.")
except Exception:
    pass

if not _moto_already_up:
    _res = subprocess.run(['docker pull motoserver/moto'], shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    subprocess.run(['docker rm --force moto-server'], shell=True, capture_output=True)
    _res = subprocess.run(['docker run -p 15000:5000 --detach --name moto-server motoserver/moto'], shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    print("Waiting for moto-server to be ready...")
    for _ in range(30):
        try:
            urllib.request.urlopen("http://localhost:15000")
            print("moto-server is ready.")
            break
        except Exception:
            time.sleep(1)
    else:
        print("ERROR: moto-server failed to start or port 5000 is unreachable.")
        exit(1)

print("### Init component submodules........")
subprocess.run('git submodule init', shell=True, capture_output=True)
print("### Update component submodules........")
subprocess.run('git submodule update', shell=True, capture_output=True)

# Pull required python slim image
print("Pull required python slim image - python:3.9.10-slim")
_res = subprocess.run('docker pull --platform="{}" python:3.9.10-slim'.format(sys_platform), shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)

# Create a docker network and connect components to the network
if platform == "linux":
    subprocess.run('docker network create notifyone-network', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network postgres_notify', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network redis_notify', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network moto-server', shell=True, capture_output=True)

setup_gateway(sys_platform)

os.chdir('../')

setup_core(sys_platform)

os.chdir('../')

setup_handler(sys_platform)

os.chdir('../')

setup_dashboard(sys_platform, cms_api_endpoint)

os.chdir('../')

if platform == "linux":
    subprocess.run('docker network connect notifyone-network notifyone-gateway', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network notifyone-core', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network notifyone-handler', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network notifyone-dashboard', shell=True, capture_output=True)

_res = subprocess.run(["docker exec -i $(docker ps | grep notifyone-core | awk '{print $1}') python3 database.py upgrade "],
                          shell=True, capture_output=True)
if _res.returncode != 0:
    print("\nError in DB upgrade\n")
    print(_res.stderr.decode('utf-8'))
else:
    print("\nDB upgrade Successful\n")

print('##### Congratulations! NotifyOne system setup Completed #####')
print('Service Hosts - \n\t notifyone-dashboard : http://localhost:8001 \n\t notifyone-gateway : http://localhost:9401 \n\t notifyone-core : http://localhost:9402 \n\t notifyone-handler : http://localhost:9403')
print('Create App API documentation - \n\t http://localhost:9402/swagger/#/Apps/post_apps')
print('Create Event API documentation - \n\t http://localhost:9402/swagger/#/Events/post_event_create')
print('Send-Notification API documentation - \n\t http://localhost:9401/swagger/#/event_notification/post_send_notification')
print('Get-Notification-Detail API documentation - \n\t http://localhost:9401/swagger/#/event_notification/get_get_notification')
