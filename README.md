# Census RM Toolbox

The most bestestest tools for make running the census big success wow.

## How to use - Message Manipulator

The message manipulator will allow you to look at rabbit messages inside a queue you specify.
### Arguments

| Name                      | Description                                                                                                         |                                                                                        
| ---------------------     | ------------------------------------------------------------------------------------------------------------------- |
| `source_queue_name`       | Rabbit queue to find messages on                                                                                    |
| `message_hash_search`     | Rabbit message hash to search by                                                                                    |
| `-s --search`             | Search for a string inside of the rabbit message body                                                               |                                                  
| `DELETE`                  | Used with `message_hash_search`, deletes rabbit message of the hash supplied                                        |
| `VIEW`                    | Used with `message_hash_search`, view rabbit message based on the hash supplied                                     |        
| `MOVE`                    | Used with `message_hash_search`, moves rabbit message based on the hash supplied to the `destination_queue_name`    |
| `destination_queue_name`  | Move a rabbit message to the destination queue that is supplied.                                                    |


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

This tool will allow you to be able to find and delete messages on a pubsub topic
### Arguments

| Name                      | Description                                                                                                         |                                                                                        
| ---------------------     | ------------------------------------------------------------------------------------------------------------------- |
| `subscription name`       | Pubsub subscription name to look on                                                                                 |
| `subscription project id` | GCP project name                                                                                                    |
| `-s --search`             | Search for a string inside of the pubsub message body                                                               |                                                  
| `DELETE`                  | Used with `message_id`, deletes pubsub message of the id supplied                                                   |
| `message_id`              | Message id of the pubsub message                                                                                    |



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
Move messages from pubsub to a GCS bucket
### Arguments

| Name                      | Description                                                                                                         |                                                                                        
| ---------------------     | ------------------------------------------------------------------------------------------------------------------- |
| `subscription name`       | Subscription name to look on                                                                                        |
| `subscription project id` | GCP project name                                                                                                    |
| `bucket name`             | Bucket you want to move the pubsub message to                                                                       |                                                  
| `message_id`              | Message id of the pubsub message you want to move                                                                   |



Moving a pubsub message to a bucket:
```bash
python put_message_on_bucket.py <subscription name> <subscription project id> <bucket name> <message_id>
```
## How to use - publishing message from GCS bucket to pubsub topic

Move messages from pubsub to a GCS bucket
### Arguments

| Name                      | Description                                                                                                         |                                                                                        
| ---------------------     | ------------------------------------------------------------------------------------------------------------------- |
| `topic name`              | Subscription name to look on                                                                                        |
| `project id`              | GCP project name                                                                                                    |
| `bucket name`             | Bucket you want to move the pubsub message to                                                                       |                                                  
| `bucket blob name`        | Name of the blob you want to publish to a topic                                                                     |                                                  

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