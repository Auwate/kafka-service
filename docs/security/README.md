# Secure Kafka Cluster Setup and Tooling Documentation

## Overview

This documentation outlines an improved **secure setup** of a Kafka cluster using **SASL authentication (PLAIN or SCRAM)** and **ACL-based authorization**, as well as the development of supporting tools and monitoring integrations. It is tailored for environments using **Docker Compose** (and by extension **Docker Swarm**) and emphasizes development-mode flexibility and security.

To begin, we will be using a **simplified** version of the `docker-compose.yml` file in production currently. You can find it in this directory called `docker-compose-1.yml`. It only contains **3** brokers, instead of **6** brokers, but the concepts apply to the extra 3. In addition, because this is for testing purposes, the `secrets`, `health-checks`, `deploy`, and everything else that comes with a **Docker Swarm** specific deployment will not be used here. However, a quick conversation with ChatGPT should solve this issue.

---

## 1. Enabling Kafka Authentication and Authorization

### Goal

Enable secure **authentication** between brokers/controllers and clients, and enforce **authorization rules** via Kafka's built-in ACL system.

### Step-by-Step Process

#### Step 1: Create a new Docker Stack

For context, a `Docker Stack` is a `docker-compose.yml` file that is inserted into the `docker stack deploy` command.

Regardless, you will find a file called `docker-compose-secure.yml` in this directory. This provides the changes necessary to deploy a cluster with Docker Swarm. Again, this will not contain all **6** nodes, but it would be simple to expand to all **6** nodes.

Now, take this file and deploy it. It should have no issues.

##### Configuration Explanation

Some of the notable configurations to pay attention to are:

##### Environment variables:

```
- KAFKA_LISTENERS: 'PLAINTEXT://:19092,SASL_PLAINTEXT://:9092'
- KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,SASL_PLAINTEXT:SASL_PLAINTEXT
# Notice that these replace PLAINTEXT_HOST with SASL_PLAINTEXT

- KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
- KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer
- KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: true
- KAFKA_SUPER_USERS: User:admin
```

#### Step 2: Creating the JAAS and admin.properties files

You may have noticed two files mounted into the brokers, called `kafka_jaas.conf` and `admin.properties`. These are 2 very important files, described below:

##### JAAS

The JAAS file is a credentials file that the node uses to authenticate itself. It is **technically** unnecessary, as the brokers talk to each other over the `Docker Network`, allowing them to directly talk to the containers themselves instead of having to hit the `SASL_PLAINTEXT` endpoints, but having it is a safe bet AND is necessary to deploy anyway.

**IF** in the future the brokers/controllers need to talk over authenticated endpoints, create a user using `kafka-configs.sh` and insert the credentials into the `JAAS`.

```
KafkaServer {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="NA"
    password="NA";
};
```

##### admin.properties

The `admin.properties` file is used for admin users to give users permissions. It is specifically inserted at the `--command-config` flag, as seen below:

```
kafka-acls.sh --bootstrap-server broker-1:19092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:test-user \
  --operation Read \
  --topic event_logs
```

An example of what this may look like is provided:

```
security.protocol=SASL_PLAINTEXT
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="admin" password="password";
```

#### Step 3: Bootstrap Admin and Inter-Broker User

Run `docker exec` into one of the brokers and move to the `/opt/kafka/bin` directory:

```bash
docker exec -it CONTAINER_NAME /bin/bash

cd opt/kafka/bin
```

Now, create the required users:

```bash
# Example: Create admin user with SCRAM credentials.
# IMPORTANT: Admin user credentials are not required to change kafka-configs, like the example below.
# --bootstrap-server uses <DOCKER_INSTANCE_ALIAS>:<OPEN_PORT_IS_LIKELY_19092>
# REMEMBER TO CHANGE THE PASSWORD
./kafka-configs.sh \
  --bootstrap-server broker-1:19092 \
  --alter \
  --add-config 'SCRAM-SHA-512=[iterations=4096,password=CHANGE_ME]' \
  --entity-type users \
  --entity-name admin
```

### Validation

To validate that this was successful, run the logs on every broker and controller. You **may** see some exceptions on the controllers, but if it shows something like `The active controller appears to be node 2` then it's standard KRAFT behavior and you can disregard.

```sh
sudo docker logs controller-1
sudo docker logs controller-2
sudo docker logs controller-3

sudo docker logs broker-1
sudo docker logs broker-2
sudo docker logs broker-3
```

Everything should look fine, with the brokers showing `Kafka Server started (kafka.server.KafkaRaftServer)`.

#### Testing External Connection Requires SASL

##### Prerequisites

Before continuing, creating a `venv` with the following:

```sh
python3 -m venv venv
source venv/bin/activate

pip install aiokafka
```

##### Testing

For setups with `Docker Compose`, the test is relatively straightforward. Provided in this directory is `test.py`, which will launch an `AIOKafkaConsumer` and `AIOKafkaProducer`. Upon initially running it, it should show a connection error. Then, going into the broker logs for port 29092, you should see a network request, but that it was denied.

Now, uncomment the parts in the consumer and producer and `exec` into any of the broker instances and run the following:

```sh
sudo docker exec -it <BROKER_NAME> /bin/bash

./opt/kafka/bin/kafka-configs.sh \
  --bootstrap-server broker-1:19092 \
  --alter \
  --add-config 'SCRAM-SHA-512=[iterations=4096,password=password]' \
  --entity-type users \
  --entity-name test-user

./opt/kafka/bin/kafka-acls.sh \
  --bootstrap-server broker-1:19092 \
  --command-config /tmp/admin_properties \
  --add \
  --allow-principal User:test-user \
  --operation Write \
  --topic "event_logs"
```

Next, run `exit`, and try running `python test.py` again. It should run successfully.

**IMPORTANT**: If you are setting up a `Docker Swarm`, you will need to change the `bootstrap_servers` to point to the IP address of the server you are currently on, instead of using *localhost*. It should look something like:

```sh
bootstrap_servers='192.168.0.1:29092'
```
