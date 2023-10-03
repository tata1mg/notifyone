import subprocess
import json
import os
from utils import extract_values
from sys import platform


def setup_gateway():
    print("\n Setting up Notification gateway \n")

    _res = subprocess.run(["git clone https://github.com/tata1mg/notifyone-gateway.git"], shell=True,
                          capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        #exit(1)

    os.chdir('notifyone-gateway')

    _res = subprocess.run(['cp config_template.json config.json'], shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    with open('config.json', 'r') as c:
        _gateway_config = json.load(c)
        _gateway_port = str(_gateway_config.get("PORT") or 6561)
        _gateway_queue_names = extract_values(_gateway_config, "QUEUE_NAME")
        if platform.lower() == 'darwin':
            _gateway_config['NOTIFICATION_SERVICE']['HOST'] = 'host.docker.internal'
            _gateway_config['TRIGGER_NOTIFICATIONS']['SQS']['SQS_ENDPOINT_URL'] = 'http://host.docker.internal:4566'
            with open('config.json', 'w') as f:
                json.dump(_gateway_config, f)

    # create local stack queues
    for _q in _gateway_queue_names:
        _res = subprocess.run(["docker exec -i $(docker ps | grep localstack | awk '{print $1}') awslocal sqs create-queue --queue-name " + _q],
                              shell=True, capture_output=True)
        if _res.returncode != 0:
            print("\nError in creating queue {}\n".format(_q))
            print(_res.stderr.decode('utf-8'))
        else:
            pass

    _stat = subprocess.run(['docker rm --force notifyone-gateway'], shell=True)
    _stat = subprocess.run(["docker image rm notifyone-gateway"], shell=True)

    _res = subprocess.run(['docker build . --tag notifyone-gateway --build-arg SERVICE_NAME=notifyone_gateway'],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    _res = subprocess.run([
                              'docker run -p ' + _gateway_port + ':' + _gateway_port + ' --detach --name notifyone-gateway notifyone-gateway'],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    print("\n Notification gateway setup completed \n")