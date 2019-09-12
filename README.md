# Census RM Toolbox

The most bestestest tools for make running the census big success wow.

## How to use - Message Manipulator

View messages on a queue (default 100 max):
   `queuetool <queue name>`

View messages on a queue with bigger limit:
   `queuetool <queue name> -l <limit>`
   
   
Search for message(s) on a queue:
   `queuetool <queue name> -s <search text>`
   
   
Delete message from a queue:
   `queuetool <queue name> <message hash> DELETE`
   
   
Move message from one queue to another:
   `queuetool <queue name> <message hash> MOVE <destination queue>`
   
## How to use - Find Queues with Poison Messages

Find queues with high redelivery rate:
   `findbadmessages`
   

## How to use - Find and remove messages on pubsub

View messages on pubsub subscription:
   `python get_pubsub_messages.py <subscription name> <subscription project id>`
   
View messages on a pubsub subscription with bigger limit:
   `python get_pubsub_messages.py <subscription name> <subscription project id> -l <limit>`
   
Search for a message:
   `python get_pubsub_messages.py <subscription name> <subscription project id> -s <search term>`

Delete message on pubsub subscription:   
   `python get_pubsub_messages.py <subscription name> <subscription project id> <message_id> DELETE`
   


## Running in Kubernetes
To run the toolbox in Kubernetes 

```bash
./run_in_kubernetes.sh
```
You can also run it with a specific image rather than the default with
```bash
IMAGE=fullimagelocation ./run_in_kubernetes.sh
```