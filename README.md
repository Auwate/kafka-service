# kafka-service

An event-streaming platform for brokering messages between applications. Uses Ansible to bootstrap setup so the service can easily be deployed on any VM with open ports.

## - Disclaimer

This documentation is built for Unix operating systems. If you are using a Mac or Windows machine, much of the documentation may apply but dependency usage and installation may be different.

# Setup

To setup the application, please clone this repository and following the following code. It's setup for the usage of `Ansible`.

```
python3 -m venv kafka_venv

source kafka_venv/bin/activate

pip install -r kafka_service/requirements.txt
```

Then, please `chdir` into `kafka_service/ansible` and run the following code. It's the Ansible playbook for bootstrapping dependencies and running `Docker Compose`:

```
ansible-playbook playbooks/setup_kafka/playbook.yaml
```

# Setup Issues

The `Ansible` playbook uses several commands to setup the cluster. Here are the following possible issues:

## - cURL not present

If `cURL` is not present on the machine you are working on, please install it on your machine using:

```
{sudo} apt update
{sudo} apt install curl
```

## - Docker Compose not present

If `Docker Compose` is not present on the machine you are working on, please install it using official documentation:

**Debian**:

- Docker Compose & Engine: https://docs.docker.com/engine/install/debian/

**Ubuntu**:

- Docker Compose & Engine: https://docs.docker.com/engine/install/ubuntu/

## - Ansible: "Illegal instruction"

Previous development have shown "Illegal instruction" output whenever using Ansible on certain systems. If it does, please try the following:

### 1: Ensure you pip install the requirements.txt file

If you installed Ansible directly through:

```
pip install ansible
```

Then please try the following:

```
pip uninstall ansible

pip install -r requirements.txt --no-cache
```

### 2: Check with system adminstrator

The VM this was developed on may have used a different architecture (such as a different CPU) than what is available. If that is the case, please check with the system adminstrator and downgrade the version as needed.

# Kafka

The deployment is made using `Docker Compose`, which is a simple way to deploy applications with identical environments. It's an abstraction over Docker to provide some repeatable environment configurations.

## - Docker

### -- Deployment

In case `Ansible` is not working, you can run the cluster using:

```
cd kafka_service/build

docker compose up -d

# If `docker compose` is not recognized, use docker-compose
```

### -- Teardown

To teardown the application, use:

```
docker compose down
```

### -- Monitoring

To monitor the cluster, use:

```
docker ps -a
```

### -- Maintenance

To apply maintenance or run commands on the individual containers, use:

```
docker exec -it {CONTAINER_NAME} /bin/bash
```

## - Apache Kafka Commands

The following are commands you can use inside each Kafka container. It's important to know that many of these only work on `brokers`, as the `controllers` do not have access to topic metadata.

**WARNING**

If you look online, there may be examples of different commands not listed here using `--bootstrap-server=localhost:9092`. For our cluster, this will not work for reasons outside of the scope of this README, but to get it to work use `--boostrap-server=localhost:19092`.

To begin, please run:

```
docker exec -it {CONTAINER_NAME} /bin/bash

cd /opt/kafka/bin
```

### -- kafka-topics.sh

#### What it does:

The `kafka-topics.sh` command is used to manage Kafka topics. You can create, list, and delete topics, and view topic configurations. It’s a critical tool for managing the Kafka ecosystem's structure.

#### Example usage:

- **Create a topic**:

    ```
    ./kafka-topics.sh --create --topic my_topic --bootstrap-server localhost:19092 --partitions 3 --replication-factor 1
    ```

    This creates a topic called `my_topic` with 3 partitions and a replication factor of 1.

- **List topics**:

    ```
    ./kafka-topics.sh --list --bootstrap-server localhost:19092
    ```

    This lists all Kafka topics in the cluster.

- **Describe a topic**:

    ```
    ./kafka-topics.sh --describe --topic my_topic --bootstrap-server localhost:19092
    ```

    This shows detailed information about the `my_topic`, such as partitions and replication.

### -- kafka-console-producer.sh

#### What it does:

The `kafka-console-producer.sh` command allows you to send messages to a Kafka topic from the command line. It's a simple way to test producing messages.

#### Example usage:

- **Produce messages to a topic**:

    ```
    ./kafka-console-producer.sh --topic my_topic --bootstrap-server localhost:19092
    ```

    After running this command, you can type messages, and they will be sent to the `my_topic` topic.

### -- kafka-console-consumer.sh

#### What it does:

The `kafka-console-consumer.sh` command is used to consume messages from a Kafka topic. You can specify a starting point for consumption, such as the latest messages or from the beginning.

#### Example usage:

- **Consume messages from a topic**:

    ```
    ./kafka-console-consumer.sh --topic my_topic --bootstrap-server localhost:19092 --from-beginning
    ```

    This will read all messages from the `my_topic` starting from the beginning.

- **Consume messages from a specific partition**:

    ```
    ./kafka-console-consumer.sh --topic my_topic --partition 0 --offset 10 --bootstrap-server localhost:19092
    ```

    This starts consuming from partition 0, beginning at offset 10.

### -- kafka-consumer-groups.sh

#### What it does:

The `kafka-consumer-groups.sh` command is used to view and manage consumer group offsets. It allows you to check consumer group status, reset offsets, and more.

#### Example usage:

- **List all consumer groups**:

    ```
    ./kafka-consumer-groups.sh --list --bootstrap-server localhost:19092
    ```

    This command lists all the consumer groups that are currently registered with the Kafka broker.

- **Describe a consumer group**:

    ```
    ./kafka-consumer-groups.sh --describe --group my_group --bootstrap-server localhost:19092
    ```

    This provides information on the consumer group `my_group`, such as the offsets and lag for each partition.

### -- kafka-broker-api-versions.sh

#### What it does:
The `kafka-broker-api-versions.sh` command is used to display the supported API versions on the Kafka broker. It helps in understanding what Kafka versions and features are available.

#### Example usage:

- **Check broker API versions**:
    
    ```
    ./kafka-broker-api-versions.sh --bootstrap-server localhost:19092
    ```

    This shows the available API versions on the Kafka broker at the specified address.

### -- kafka-replica-verification.sh

#### What it does:

The `kafka-replica-verification.sh` script is used to verify the replication status of Kafka topics. It can help identify out-of-sync replicas and potential replication issues.

#### Example usage:

- **Verify replica status**:

    ```
    ./kafka-replica-verification.sh --bootstrap-server localhost:19092
    ```

    This checks the status of replicas across topics and identifies any issues with replication.
