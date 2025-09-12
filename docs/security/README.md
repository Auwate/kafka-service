# Secure Kafka Cluster Setup and Tooling Documentation

## Overview

This documentation outlines an improved **secure setup** of a Kafka cluster using **SASL authentication (PLAIN or SCRAM)** and **ACL-based authorization**, as well as the development of supporting tools and monitoring integrations. It is tailored for environments using **Docker Compose** (and by extension **Docker Swarm**) and emphasizes development-mode flexibility and security.

To begin, we will be using a **simplified** version of the `docker-compose.yml` file in production currently. You can find it in this directory called `docker-compose-1.yml`. It only contains **3** brokers, instead of **6** brokers, but the concepts apply to the extra 3. In addition, because this is for testing purposes, the `secrets`, `health-checks`, `deploy`, and everything else that comes with a **Docker Swarm** specific deployment will not be used here. However, a quick conversation with ChatGPT should solve this issue.

---

## 1. Enabling Kafka Authentication and Authorization

### Goal

Enable secure **authentication** between brokers/controllers and clients, and enforce **authorization rules** via Kafka's built-in ACL system.

### Step-by-Step Process

#### Step 1: Bootstrap Admin and Inter-Broker User

Run `docker exec` into one of the brokers and move to the `/opt/kafka/bin` directory:

```bash
docker exec -it CONTAINER_NAME /bin/bash

cd opt/kafka/bin
```

While the cluster is still **insecure** (how it is currently in production: no SASL or ACLs), create required users:

```bash
# Example: Create admin user with SCRAM credentials.
# IMPORTANT: Admin users are not required to change kafka-configs, like the example below. This is just a root user that developers can use programmatically that bypasses all ACLs and rules.
# --bootstrap-server uses <DOCKER_INSTANCE_ALIAS>:<OPEN_PORT_IS_LIKELY_19092_OR_9092>
# REMEMBER TO CHANGE THE PASSWORD
./kafka-configs.sh \
  --bootstrap-server broker-1:19092 \
  --alter \
  --add-config 'SCRAM-SHA-512=[iterations=4096,password=CHANGE_ME]' \
  --entity-type users \
  --entity-name admin
```

```bash
# Example: Create broker communication user
# REMEMBER TO CHANGE THE PASSWORD
./kafka-configs.sh \
  --bootstrap-server broker-1:19092 \
  --alter \
  --add-config 'SCRAM-SHA-512=[iterations=4096,password=CHANGE_ME]' \
  --entity-type users \
  --entity-name broker-user
```

> These users are stored in Kafka's internal metadata.

For reference, the users you just created are the admin user and the broker user. The admin user is what operators use to do their administrative tasks, and the broker user is what the Kafka cluster will try signing in as. Each broker/controller can share the same user, but they need one to log in.

#### Step 2: Shutdown the Cluster

IMPORTANT: Do **not** add `-v` to `docker-compose down`, as this will remove the created ACLs from before.

```bash
docker-compose down
```

#### Step 3: Create JAAS File

##### What is JAAS?

Up until now, we have created users on our cluster. However, when we activate the authentication in the cluster, each node will need to authentication themselves. Kafka accomplishes this by using JAAS, or Java Authentication and Authorization Service. JAAS is Java's pluggable authentication framework that allows applications to authenticate users and authorize access to resources.

In Kafka, JAAS handles the "who are you?" question by managing login credentials and authentication mechanisms for the nodes. Whenever the Kafka nodes start up or rejoin clusters (such as if they go down), they use the JAAS file for authentication.

#### Creating the JAAS

The following is a sample of what you would create. To use it, save it in the root directory of the docker-compose.yml file, saved as a `.conf` file. For future reference, we will refer to this as `kafka_jaas.conf`.

```properties
KafkaServer {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="broker-user"
    password="CHANGE_ME_PASSWORD";
};
```

If you're doing this on a Docker Swarm, you will need to create a secret which can be loaded into each individually. Here is an example:

```sh
# Create JAAS and save as kafka_jaas.conf in the current working directory
docker secret create kafka_jaas_conf ./kafka_jaas.conf
```

You will then add this in the `secrets` section of each service in the `docker-compose.yml` file.

#### Step 4: Add Security Configuration

Provided in this directory is `docker-compose-2.yml`, containing everything from `docker-compose-1.yml` but with new configurations. Please read **everything** as even one minor configuration mistake can cause an error. Some of the notable ones to pay attention to are:

##### Environment variables:

```
- KAFKA_NODE_ID: 20
# VERY IMPORTANT. Because we're updating existing brokers with new configs, the controllers will
# think they are duplicates trying to impersonate those nodes. To bypass this, we assign NEW id
# numbers, so the controllers accept them and use their new configs.


- KAFKA_LISTENERS: 'PLAINTEXT://:19092,SASL_PLAINTEXT://:9092'
- KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,SASL_PLAINTEXT:SASL_PLAINTEXT
# Notice that these replace PLAINTEXT_HOST with SASL_PLAINTEXT

- KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
- KAFKA_AUTHORIZER_CLASS_NAME: org.apache.kafka.metadata.authorizer.StandardAuthorizer
- KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: true
- KAFKA_SUPER_USERS: User:admin
- KAFKA_OPTS: "-Djava.security.auth.login.config=/etc/kafka/kafka_jaas.conf"
```

##### Volumes

```
volumes:
     - broker-1-volume:/var/lib/kafka/data
     - ./kafka_jaas.conf:/etc/kafka/kafka_jaas.conf:ro # <- Mounts the JAAS
```

If you are using `Docker Swarm`, you would want to add this at

```
secrets:
  - kafka_jaas_conf
```

You would then change `KAFKA_OPTS` to:

```
- KAFKA_OPTS: "-Djava.security.auth.login.config=/run/secrets/kafka_jaas_conf"
```

##### Command

```
command: >
  /bin/bash 
  -c 
  'export KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://broker-1:19092,SASL_PLAINTEXT://localhost:29092" && /etc/kafka/docker/run'
```

Notice that we changed PLAINTEXT_HOST to SASL_PLAINTEXT here as well.

If you are on `Docker Swarm`, remember to change `localhost` to the IP of the server you are on currently.

##### Controllers

It's important to note there were little to no changes to the controllers. This is because controllers are NOT public facing, thus they do not need SASL protection against users. The only way to get access to them would be to have access to the direct server they are running on.

#### Step 5: Removing Broker Volumes

Unfortunately, brokers save their own IDs into their volumes, authenticating themselves each time they come up. This is a problem for us because we **changed** their ID so the controllers can accept them. We solve this issue by removing the volumes for `broker-1`, `broker-2`, and `broker-3`:

```sh
sudo docker volume ls

sudo docker volume rm <BROKER-1-VOLUME-NAME>
sudo docker volume rm <BROKER-2-VOLUME-NAME>
sudo docker volume rm <BROKER-3-VOLUME-NAME>
```

#### Step 6: Rebooting Kafka

Restart the cluster. This will recreate new broker volumes for us to use.

```sh
sudo docker compose up -d
```

#### Important:

To ensure no problems, we are turning `KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: true`. This configuration will essentially allow anyone to connect if there are no ACLs. This should (in theory) do nothing since we setup ACLs, but in case the ACLs were not persisted, this will help us bypass and validate everything.

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
```

Next, run `exit`, and try running `python test.py` again. It should run successfully.

**IMPORTANT**: If you are setting up a `Docker Swarm`, you will need to change the `bootstrap_servers` to point to the IP address of the server you are currently on, instead of using *localhost*. It should look something like:

```sh
bootstrap_servers='192.168.0.1:29092'
```
