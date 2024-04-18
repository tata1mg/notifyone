import subprocess
import json
import os
from sys import platform
from utils import extract_values

def setup_handler(sys_platform):

    print("\nSetting up notifyone-handler.....\n")

    os.chdir('notifyone-handler')

    _res = subprocess.run(['cp config_template.json config.json'], shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    with open('config.json') as c:
        _handler_config = json.load(c)
        _handler_queue_names = extract_values(_handler_config, "QUEUE_NAME")
        _port = str(_handler_config.get("PORT") or 9403)
        if platform.lower() == 'darwin':
            _handler_config['SQS_AUTH']['SQS_ENDPOINT_URL'] = 'http://host.docker.internal:4566'
            with open('config.json', 'w') as f:
                json.dump(_handler_config, f)
        elif platform.lower() == "linux":
            _handler_config['SQS_AUTH']['SQS_ENDPOINT_URL'] = 'http://localstack-main:4566'
            with open('config.json', 'w') as f:
                json.dump(_handler_config, f)

    # create local stack queues
    for _q in _handler_queue_names:
        _res = subprocess.run(["docker exec -i $(docker ps | grep localstack | awk '{print $1}') awslocal sqs create-queue --queue-name " + _q],
                              shell=True, capture_output=True)
        if _res.returncode != 0:
            print("\nError in creating queue {}\n".format(_q))
            print(_res.stderr.decode('utf-8'))
        else:
            pass

    _stat = subprocess.run(['docker rm --force notifyone-handler'], shell=True)
    _stat = subprocess.run(["docker image rm notifyone-handler"], shell=True)

    _res = subprocess.run(['docker build . --tag notifyone-handler --build-arg SERVICE_NAME=notifyone_handler --build-arg SYS_PLATFORM={}'.format(sys_platform)],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    _res = subprocess.run(['docker run -p ' + _port + ':' + _port + ' --detach --name notifyone-handler notifyone-handler'],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    print("\nnotifyone-core setup completed\n")