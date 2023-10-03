import subprocess
import os
from gateway_setup import setup_gateway
from core_setup import setup_core
from handler_setup import setup_handler

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

setup_gateway()

os.chdir('../')

setup_core()

os.chdir('../')

setup_handler()

print('Notification System Setup Complete')


