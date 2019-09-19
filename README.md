# Census RM Toolbox

The most bestestest tools for make running the census big success wow.

## How to use - Message Manipulator

View messages on a queue (default 100 max):
   ```bash
   queuetool <queue name>
   ```

View messages on a queue with bigger limit:
   ```bash
   queuetool <queue name> -l <limit>
   ```
   
   
Search for message(s) on a queue:
   ```bash
   queuetool <queue name> -s <search text>
   ```
   
   
Delete message from a queue:
   ```bash
    queuetool <queue name> <message hash> DELETE
   ```
   
   
Move message from one queue to another:
   ```bash
   queuetool <queue name> <message hash> MOVE <destination queue>
   ```
   
## How to use - Find Queues with Poison Messages

Find queues with high redelivery rate:
   ```bash
   findbadmessages
   ```
   

## How to use - Find and remove messages on pubsub

View messages on pubsub subscription:
   ```bash
   python get_pubsub_messages.py <subscription name> <subscription project id>
   ```
   
View messages on a pubsub subscription with bigger limit:
   ```bash
   python get_pubsub_messages.py <subscription name> <subscription project id> -l <limit>
   ```
   
Search for a message:
   ```bash
   python get_pubsub_messages.py <subscription name> <subscription project id> -s <search term>
   ```

Delete message on pubsub subscription:   
   ```bash
   python get_pubsub_messages.py <subscription name> <subscription project id> <message_id> DELETE
   ```
   
   
## How to use - Moving messages from pubsub to bucket

Moving a pubsub message to a bucket:
```bash
python put_message_on_bucket.py <subscription name> <subscription project id> <bucket name> <message_id>
```
## How to use - publishing message from GCS bucket to pubsub topic

Moving a pubsub message to a bucket:
```bash
python publish_message_from_bucket.py <topic name> <project id> <bucket blob name> <bucket name>
```

   


## Running in Kubernetes
To run the toolbox in a kubernetes environment, you'll have to create the deployment using `census-rm-toolbox-deployment.yml`
```bash
make apply-deployment
```
Once the pod is up, you can connect to it:
```bash
make connect-to-pod
```
Once you're finished with the pod, you can remove it from your kubernetes environment:
```bash
make delete-pod
```