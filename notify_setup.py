import subprocess
import os
import sys
from sys import platform
from gateway_setup import setup_gateway
from core_setup import setup_core
from handler_setup import setup_handler
from dashboard_setup import setup_dashboard

sys_platform = sys.argv[1] if len(sys.argv) > 1 else "linux/amd64"

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


print("\n Setting up localstack\n")
# install localstack
_res = subprocess.run(['localstack --version'], shell=True, capture_output=True)
if _res.returncode != 0:
    print("Localstack not installed \n"+(str(_docker_check_res.stderr.decode('utf-8'))))
    print("\n installing localstack \n")
    _localstack_res = subprocess.run(['python3 -m pip install --force-reinstall localstack'], shell=True, capture_output=True)
    if _localstack_res.returncode != 0:
        print(str(_localstack_res.stderr.decode('utf-8')))
        exit(1)
    else:
        pass
else:
    pass

_localstack_start_res = subprocess.run(['localstack start -d'], shell=True, capture_output=True)
if _localstack_start_res.returncode != 0:
    print(str(_localstack_start_res.stderr.decode('utf-8')))
    exit(1)
else:
    pass

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
    subprocess.run('docker network connect notifyone-network localstack-main', shell=True, capture_output=True)

setup_gateway(sys_platform)

os.chdir('../')

setup_core(sys_platform)

os.chdir('../')

setup_handler(sys_platform)

os.chdir('../')

setup_dashboard(sys_platform)

os.chdir('../')

if platform == "linux":
    subprocess.run('docker network connect notifyone-network notifyone-gateway', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network notifyone-core', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network notifyone-handler', shell=True, capture_output=True)
    subprocess.run('docker network connect notifyone-network notifyone-dashboard', shell=True, capture_output=True)

print('##### Congratulations! NotifyOne system setup Completed #####')
print('Service Hosts - \n\t notifyone-dashboard : http://localhost:8001 \n\t notifyone-gateway : http://localhost:9401 \n\t notifyone-core : http://localhost:9402 \n\t notifyone-handler : http://localhost:9403')
print('Create App API documentation - \n\t http://localhost:9402/swagger/#/Apps/post_apps')
print('Create Event API documentation - \n\t http://localhost:9402/swagger/#/Events/post_event_create')
print('Send-Notification API documentation - \n\t http://localhost:9401/swagger/#/event_notification/post_send_notification')
print('Get-Notification-Detail API documentation - \n\t http://localhost:9401/swagger/#/event_notification/get_get_notification')
