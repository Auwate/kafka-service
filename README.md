# kafka-service

An event-streaming platform for brokering messages between applications. Uses Ansible to bootstrap setup so the service can easily be deployed on any VM with open ports.

This service uses the following ports on each machine:

- 29092 TCP - Kafka
- 29093 TCP - Kafka
- 39092 TCP - Kafka
- 39093 TCP - Kafka
- 49092 TCP - Kafka
- 49093 TCP - Kafka
- 2377 TCP - Docker Swarm (Overlay Network)
- 7946 TCP - Docker Swarm (Discovery)
- 4789 UDP - Docker Swarm (Ingress Network)

## - Disclaimer

This documentation is built for Unix operating systems. If you are using a Mac or Windows machine, much of the documentation may apply but dependency usage and installation may be different.

# Setup

Currently the setup does not use `Ansible` for automation, although this may change with future iterations. Thus, the following is manual setup.

## Gathering dependencies:

The application relies heavily on Docker, hence this application will require Docker to be installed on all VMs that will be used. You can find more information here: https://docs.docker.com/engine/install/

## Starting the swarm

Firstly to get the service ready, we need to have all three VMs up and running using `Docker Swarm`. This is a native tool provided by Docker to distribute the load across multiple machines, providing built-in load balancing, redeployment, and networking.

To get started, please log into the first machine and run `docker swarm init`. This will return to you a token to which you will use in the next step.

## Joining swarm on other VMs

Next, go into the other VMs and run `docker swarm join --token <ENTER_TOKEN_HERE> <IP_ADDRESS_OF_VM>:2377`. Please insert the token where `<ENTER_TOKEN_HERE>` is and the IP address of the current VM in `<IP_ADDRESS_OF_VM>`

Next, go back to the machine you initialized the swarm in and run `docker node promote <HOST_NAME_OR_NODE_ID>`, where you would put the host name or the ID of the node in `<HOST_NAME_OR_NODE_ID>`. This will promote each node into a hybrid, which essentially takes care of both managerial and labor-based tasks. You can find these attributes by running `docker node ls` in the first machine.

## Labeling each node in the swarm

After joining each node in the swarm, gather the hostname by using `docker node ls` and go into any node (as they are all hybrid managers) to run the following commands:

```
docker node update --label-add group=group1 <VM_1_HOST_NAME_OR_NODE_ID>
docker node update --label-add group=group2 <VM_2_HOST_NAME_OR_NODE_ID>
docker node update --label-add group=group3 <VM_3_HOST_NAME_OR_NODE_ID>
```

## Adding IP addresses as secrets

`Docker Swarm` provides service called `secrets` which is a scalable way to share information between nodes to configure their containers. This application relies heavily on it to supply the IP addresses of each node. To get started, please find the IP addresses (or DNS addresses) for each VM in the swarm.

Next, run the following commands:

```
echo -n "<IP_ADDRESS_OF_VM_1>" >> group1_ip
echo -n "<IP_ADDRESS_OF_VM_2>" >> group2_ip
echo -n "<IP_ADDRESS_OF_VM_3>" >> group3_ip
```

Then run the following commands to create the secrets:

```
docker secret create group1_ip group1_ip
docker secret create group2_ip group2_ip
docker secret create group3_ip group3_ip
```

## Deploying the stack

After getting the swarm up and running, please clone the repository (if you haven't already) into any of the machines and move the current working directory into the `/build` section. Then, run `docker stack deploy -c docker-compose.yaml kafka`. This will launch the stack and deploy the containers across each VM.

# Dev Commands

## - Apache Kafka Commands

The following are commands you can use inside each Kafka container. It's important to know that many of these only work on `brokers`, as the `controllers` do not have access to topic metadata.

**WARNING**

If you look online, there may be examples of different commands not listed here using `--bootstrap-server=localhost:9092`. For our cluster, this will not work for reasons outside of the scope of this README, but to get it to work use the IP address of the VM you are on, followed by the IP the Kafka cluster advertises on, such as: `--boostrap-server=192.108.0.109:29093`.

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
    ./kafka-topics.sh --create --topic my_topic --bootstrap-server <IP_ADDR>:29092 --partitions 3 --replication-factor 1
    ```

    This creates a topic called `my_topic` with 3 partitions and a replication factor of 1.

- **List topics**:

    ```
    ./kafka-topics.sh --list --bootstrap-server <IP_ADDR>:29092
    ```

    This lists all Kafka topics in the cluster.

- **Describe a topic**:

    ```
    ./kafka-topics.sh --describe --topic my_topic --bootstrap-server <IP_ADDR>:29092
    ```

    This shows detailed information about the `my_topic`, such as partitions and replication.

### -- kafka-console-producer.sh

#### What it does:

The `kafka-console-producer.sh` command allows you to send messages to a Kafka topic from the command line. It's a simple way to test producing messages.

#### Example usage:

- **Produce messages to a topic**:

    ```
    ./kafka-console-producer.sh --topic my_topic --bootstrap-server <IP_ADDR>:29092
    ```

    After running this command, you can type messages, and they will be sent to the `my_topic` topic.

### -- kafka-console-consumer.sh

#### What it does:

The `kafka-console-consumer.sh` command is used to consume messages from a Kafka topic. You can specify a starting point for consumption, such as the latest messages or from the beginning.

#### Example usage:

- **Consume messages from a topic**:

    ```
    ./kafka-console-consumer.sh --topic my_topic --bootstrap-server <IP_ADDR>:29092 --from-beginning
    ```

    This will read all messages from the `my_topic` starting from the beginning.

- **Consume messages from a specific partition**:

    ```
    ./kafka-console-consumer.sh --topic my_topic --partition 0 --offset 10 --bootstrap-server <IP_ADDR>:29092
    ```

    This starts consuming from partition 0, beginning at offset 10.

### -- kafka-consumer-groups.sh

#### What it does:

The `kafka-consumer-groups.sh` command is used to view and manage consumer group offsets. It allows you to check consumer group status, reset offsets, and more.

#### Example usage:

- **List all consumer groups**:

    ```
    ./kafka-consumer-groups.sh --list --bootstrap-server <IP_ADDR>:29092
    ```

    This command lists all the consumer groups that are currently registered with the Kafka broker.

- **Describe a consumer group**:

    ```
    ./kafka-consumer-groups.sh --describe --group my_group --bootstrap-server <IP_ADDR>:29092
    ```

    This provides information on the consumer group `my_group`, such as the offsets and lag for each partition.

### -- kafka-broker-api-versions.sh

#### What it does:
The `kafka-broker-api-versions.sh` command is used to display the supported API versions on the Kafka broker. It helps in understanding what Kafka versions and features are available.

#### Example usage:

- **Check broker API versions**:
    
    ```
    ./kafka-broker-api-versions.sh --bootstrap-server <IP_ADDR>:29092
    ```

    This shows the available API versions on the Kafka broker at the specified address.

### -- kafka-replica-verification.sh

#### What it does:

The `kafka-replica-verification.sh` script is used to verify the replication status of Kafka topics. It can help identify out-of-sync replicas and potential replication issues.

#### Example usage:

- **Verify replica status**:

    ```
    ./kafka-replica-verification.sh --bootstrap-server <IP_ADDR>:29092
    ```

    This checks the status of replicas across topics and identifies any issues with replication.
