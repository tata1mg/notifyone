import subprocess
import time as _time
from sys import platform


KAFKA_CONTAINER_NAME = "kafka-notifyone"
KAFKA_IMAGE = "bitnami/kafka:3.6"
KAFKA_INTERNAL_PORT = 9092
KAFKA_CONTROLLER_PORT = 9093
KAFKA_TOPIC_PARTITIONS = 12
KAFKA_REPLICATION_FACTOR = 1


def setup_kafka_container(sys_platform: str) -> None:
    """
    Start a bitnami/kafka:3.6 container in KRaft mode (no ZooKeeper).
    Idempotent: removes any existing container before starting.
    """
    print("\n Setting up Kafka (KRaft mode) on Docker\n")

    _res = subprocess.run(
        ["docker pull {}".format(KAFKA_IMAGE)],
        shell=True, capture_output=True,
    )
    if _res.returncode != 0:
        print("Error pulling Kafka image: " + _res.stderr.decode("utf-8"))
        exit(1)

    subprocess.run(
        ["docker rm --force {}".format(KAFKA_CONTAINER_NAME)],
        shell=True, capture_output=True,
    )

    if sys_platform.startswith("darwin") or platform.lower() == "darwin":
        advertised_listeners = "PLAINTEXT://host.docker.internal:{}".format(KAFKA_INTERNAL_PORT)
    else:
        advertised_listeners = "PLAINTEXT://{}:{}".format(KAFKA_CONTAINER_NAME, KAFKA_INTERNAL_PORT)

    docker_cmd = (
        "docker run --detach --name {container}"
        " -p {port}:{port}"
        " -e KAFKA_CFG_NODE_ID=0"
        " -e KAFKA_CFG_PROCESS_ROLES=controller,broker"
        " -e KAFKA_CFG_LISTENERS=PLAINTEXT://:{port},CONTROLLER://:{ctrl_port}"
        " -e KAFKA_CFG_ADVERTISED_LISTENERS={advertised}"
        " -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@{container}:{ctrl_port}"
        " -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER"
        " -e ALLOW_PLAINTEXT_LISTENER=yes"
        " {image}"
    ).format(
        container=KAFKA_CONTAINER_NAME,
        port=KAFKA_INTERNAL_PORT,
        ctrl_port=KAFKA_CONTROLLER_PORT,
        advertised=advertised_listeners,
        image=KAFKA_IMAGE,
    )

    _res = subprocess.run([docker_cmd], shell=True, capture_output=True)
    if _res.returncode != 0:
        print("Error starting Kafka container: " + _res.stderr.decode("utf-8"))
        exit(1)

    print("Waiting 10 seconds for Kafka broker to be ready...")
    _time.sleep(10)

    if platform.lower() == "linux":
        subprocess.run(
            ["docker network connect notifyone-network {}".format(KAFKA_CONTAINER_NAME)],
            shell=True, capture_output=True,
        )

    print("Kafka container '{}' started.\n".format(KAFKA_CONTAINER_NAME))


def create_kafka_topics(topics: list, container_name: str = KAFKA_CONTAINER_NAME) -> None:
    """
    Create Kafka topics inside the running container.
    Uses --if-not-exists so it is safe to call multiple times.
    Each topic is created with 12 partitions and replication factor 1.
    """
    for topic in topics:
        cmd = (
            "docker exec -i {container} kafka-topics.sh"
            " --create --if-not-exists"
            " --bootstrap-server localhost:{port}"
            " --partitions {partitions}"
            " --replication-factor {rf}"
            " --topic {topic}"
        ).format(
            container=container_name,
            port=KAFKA_INTERNAL_PORT,
            partitions=KAFKA_TOPIC_PARTITIONS,
            rf=KAFKA_REPLICATION_FACTOR,
            topic=topic,
        )
        _res = subprocess.run([cmd], shell=True, capture_output=True)
        if _res.returncode != 0:
            print("Error creating Kafka topic {}: {}".format(topic, _res.stderr.decode("utf-8")))
        else:
            print("Kafka topic created: {}".format(topic))
