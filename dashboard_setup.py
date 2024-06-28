import subprocess
import json
import os
from sys import platform


def setup_dashboard(sys_platform):
    print("\nSetting up notifyone-dashboard.....\n")

    os.chdir('notifyone-dashboard')

    with open('./src/config.json', 'r') as c:
        _dashboard_config = json.load(c)
        _dashboard_port = str(_dashboard_config.get("communication").get("communicationAppUrlPort") or 8000)
        # if platform.lower() == 'darwin':
        #     _dashboard_config["communication"]["serverDomain"] = "http://host.docker.internal:9402"
        #     _dashboard_config["server"]["base_notification_url"] = "http://host.docker.internal:9402"
        # with open('./src/config.json', 'w') as f:
        #     json.dump(_dashboard_config, f)

    _stat = subprocess.run(['docker rm --force notifyone-dashboard'], shell=True)
    _stat = subprocess.run(["docker image rm notifyone-dashboard"], shell=True)

    _res = subprocess.run(['docker build . --tag notifyone-dashboard --build-arg SERVICE_NAME=notifyone_dashboard --build-arg SYS_PLATFORM={}'.format(sys_platform)],
                          shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    _res = subprocess.run([
        'docker run -p ' + _dashboard_port + ':' + _dashboard_port + ' --detach --name notifyone-dashboard notifyone-dashboard'],
        shell=True, capture_output=True)
    if _res.returncode != 0:
        print(str(_res.stderr.decode('utf-8')))
        exit(1)

    print("\nnotifyone-dashboard setup completed\n")
