import subprocess
import json
import os
import boto3
from utils import extract_values
from sys import platform


def setup_gateway(sys_platform):
    print("\nSetting up notifyone-gateway.....\n")

    os.chdir('notifyone-gateway')

    _res = subprocess.run(['cp config_template.json config.json'], shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    with open('config.json', 'r') as c:
        _gateway_config = json.load(c)
        _gateway_port = str(_gateway_config.get("PORT") or 9401)
        _gateway_queue_names = extract_values(_gateway_config, "QUEUE_NAME")
        if platform.lower() == 'darwin':
            _gateway_config['NOTIFICATION_SERVICE']['HOST'] = 'http://host.docker.internal:9402'
            _gateway_config['TRIGGER_NOTIFICATIONS']['SQS']['SQS_ENDPOINT_URL'] = 'http://host.docker.internal:5000'
            with open('config.json', 'w') as f:
                json.dump(_gateway_config, f)
        elif platform.lower() == "linux":
            _gateway_config['NOTIFICATION_SERVICE']['HOST'] = 'http://notifyone-core:9402'
            _gateway_config['TRIGGER_NOTIFICATIONS']['SQS']['SQS_ENDPOINT_URL'] = 'http://moto-server:5000'
            with open('config.json', 'w') as f:
                json.dump(_gateway_config, f)

    # create sqs queues
    _sqs_endpoint = 'http://localhost:5000'
    sqs = boto3.client(
        'sqs',
        endpoint_url=_sqs_endpoint,
        region_name='us-east-1',
        aws_access_key_id='test',       # non-secret placeholder — moto accepts any non-empty string
        aws_secret_access_key='test',   # non-secret placeholder
    )
    for _q in _gateway_queue_names:
        try:
            sqs.create_queue(QueueName=_q)
            print(f"Created queue: {_q}")
        except Exception as e:
            print(f"Error creating queue {_q}: {e}")

    _stat = subprocess.run(['docker rm --force notifyone-gateway'], shell=True)
    _stat = subprocess.run(["docker image rm notifyone-gateway"], shell=True)

    _res = subprocess.run(['docker build . --tag notifyone-gateway --build-arg SERVICE_NAME=notifyone_gateway --build-arg SYS_PLATFORM={}'.format(sys_platform)],
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

    print("\nnotifyone-gateway setup completed\n")