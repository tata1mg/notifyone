import subprocess
import json
import os
_docker_check_res = subprocess.run(['docker info'], shell=True, capture_output=True)
if _docker_check_res.returncode != 0:
    print("Either Docker is not installed or not running\n"+(str(_docker_check_res.stderr.decode('utf-8'))))
    exit(1)


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

print("\n Setting up Notification gateway \n")

_res = subprocess.run(["git clone https://github.com/tata1mg/notifyone-gateway.git"], shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    #exit(1)

os.chdir('notifyone-gateway')

_res = subprocess.run(['cp config_template.json config.json'],  shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)

with open('config.json') as c:
    _gateway_config = json.load(c)
    _gateway_port = str(_gateway_config.get("PORT") or 6561)
    _trigger_notifications = _gateway_config.get("TRIGGER_NOTIFICATIONS", {})
    _gateway_queue_names = [_trigger_notifications.get('HIGH_PRIORITY', {}).get('QUEUE_NAME', ''),
                            _trigger_notifications.get('MEDIUM_PRIORITY', {}).get('QUEUE_NAME', ''),
                            _trigger_notifications.get('LOW_PRIORITY', {}).get('QUEUE_NAME', '')]

# create local stack queues
for _q in _gateway_queue_names:
    _res = subprocess.run(["docker exec -i $(docker ps | grep localstack | awk '{print $1}') awslocal sqs create-queue --queue-name "+_q],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print("\nError in creating queue {}\n".format(_q))
        print(_res.stderr.decode('utf-8'))
    else:
        pass

_stat = subprocess.run(['docker rm --force notifyone-gateway'], shell=True)
_stat = subprocess.run(["docker image rm notifyone-gateway"], shell=True)

_res = subprocess.run(['docker build . --tag notifyone-gateway --build-arg SERVICE_NAME=notifyone_gateway'],  shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)

_res = subprocess.run(['docker run -p '+ _gateway_port+':'+_gateway_port + ' --detach --name notifyone-gateway notifyone-gateway'],  shell=True, capture_output=True)
if _res.returncode != 0:
    print(str(_res.stderr.decode('utf-8')))
    exit(1)

os.chdir('../')

print(os.getcwd())