import subprocess
import json
import os
from utils import extract_values
from sys import platform


def setup_core():
    print("\n Setting up Notification Core \n")

    _res = subprocess.run(["git clone https://github.com/tata1mg/notifyone-core.git"], shell=True,
                          capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        #exit(1)

    os.chdir('notifyone-core')

    _res = subprocess.run(['cp config_template.json config.json'], shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    with open('config.json') as c:
        _core_config = json.load(c)
        _core_queue_names = extract_values(_core_config, "QUEUE_NAME")
        _port = str(_core_config.get("PORT") or 6562)
        if platform.lower() == 'darwin':
            _core_config['DB_CONNECTIONS']['connections']['default']['credentials']['host'] = 'host.docker.internal'
            _core_config['SUBSCRIBE_NOTIFICATION_STATUS_UPDATES']['SQS']['SQS_ENDPOINT_URL'] = 'http://host.docker.internal:4566'
            _core_config['DISPATCH_NOTIFICATION_REQUEST']['SQS']['SQS_ENDPOINT_URL'] = 'http://host.docker.internal:4566'
            _core_config['NOTIFICATION_REQUEST']['SQS']['SQS_ENDPOINT_URL'] = 'http://host.docker.internal:4566'
            _core_config['REDIS_CACHE_HOSTS']['default']['REDIS_HOST'] = 'host.docker.internal'
            with open('config.json', 'w') as f:
                json.dump(_core_config, f)

    # create local stack queues
    for _q in _core_queue_names:
        _res = subprocess.run(["docker exec -i $(docker ps | grep localstack | awk '{print $1}') awslocal sqs create-queue --queue-name " + _q],
                              shell=True, capture_output=True)
        if _res.returncode != 0:
            print("\nError in creating queue {}\n".format(_q))
            print(_res.stderr.decode('utf-8'))
        else:
            pass

    _stat = subprocess.run(['docker rm --force notifyone-core'], shell=True)
    _stat = subprocess.run(["docker image rm notifyone-core"], shell=True)

    _res = subprocess.run(['docker build . --tag notifyone-core --build-arg SERVICE_NAME=notifyone_core'],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    _res = subprocess.run(['docker run -p ' + _port + ':' + _port + ' --detach --name notifyone-core notifyone-core'],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    _res = subprocess.run(["docker exec -i $(docker ps | grep notifyone-core | awk '{print $1}') python3 database.py upgrade "],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print("\nError in DB upgrade\n")
        print(_res.stderr.decode('utf-8'))
    else:
        pass

    print("\n Notification Core setup completed \n")