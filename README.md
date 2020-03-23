# Census RM Toolbox

The most bestestest tools for make running the census big success wow.

## Questionnaire Linking
On dev-toolbox run
```bash
qidlink <filename.csv>
```


## Bad Message Wizard
On the pod run
```bash
msgwizard
```

This should start a terminal wizard for dealing with bad messages through the exception manager service

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
   
## How to use - Loss of Concentration or Boredom

Go on an adventure:
   ```bash
   adventure
   ```
Use commands like 'go north' and 'kill enemy' to go on an entertaining adventure.

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

Publishing message from GCS bucket to pubsub topic
### Arguments

| Name                      | Description                                                                                                         |                                                                                        
| ---------------------     | ------------------------------------------------------------------------------------------------------------------- |
| `topic name`              | topic name to put message on                                                                                               |
| `project id`              | GCP project name                                                                                                    |
| `bucket name`             | Bucket you want to move the pubsub message to                                                                       |                                                  
| `bucket blob name`        | Name of the blob you want to publish to a topic                                                                     |                                                  

Publishing message from GCS bucket to pubsub topic:
```bash
python publish_message_from_bucket.py <topic name> <project id> <bucket blob name> <bucket name>
```

## QID Checksum Validator
A tool to check if a QID checksum is valid. Also shows the valid checksum digits if the QID fails. 

### Usage
```bash
qidcheck <QID>
```

### Arguments
| Name                      | Description                                                                                                         |                                                                                        
| ---------------------     | ------------------------------------------------------------------------------------------------------------------- |
| `qid`                     | The QID you wish to validate                                                                                        |

#### Optional Arguments
A non-default modulus and or factor for the checksum algorithm can be used with the optional flags `--modulus` and `--factor` 
   
## Running in Kubernetes
To run the toolbox in a kubernetes environment, you'll have to create the deployment using the YAML files in census-rm-kubernetes. If you do not have a Cloud SQL Read Replica, use the dev deployment YAML file

Once the pod is up, you can connect to it:
```bash
kubectl exec -it $(kubectl get pods --selector=app=census-rm-toolbox -o jsonpath='{.items[*].metadata.name}') -- /bin/bash
```



## Configure and Whitelist Cloud Shell Tool

This repo includes scripts to configure the cloud shell to point at an RM cluster in a project and whitelist/un-whitelist itself.  

### Prerequisites
#### Install pyenv
Requres [pipenv](https://github.com/pypa/pipenv) and [pyenv](https://github.com/pyenv/pyenv)


To be able to use these scripts, you'll need to have [pyenv](https://github.com/pyenv/pyenv#installation) installed in your cloudshell environment to be able to install a python 3 version. To do this you can use these commands:
```shell script
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"
```

#### Install python 3 and pipenv
Once this is done, you should be able to install python 3 and pipenv dependencies using these commands:
```shell script
pyenv install 3.7.4
pyenv global 3.7.4
pip install pipenv
pipenv install --dev
```

### Set Up Aliases and Shortcuts
If you're going to be running these commands regularly it may be helpful to have the scripts on your `PATH` and set up some alias in your cloudshell bash.
Add these lines to your `~/.bashrc` file in the cloudshell 
```shell script
export PATH="<PATH_TO_CENSUS_RM_TOOLBOX>/cloudshell_utilities:$PATH"
alias prod-configure="configure_and_whitelist.sh census-rm-prod"
alias prod-exit="remove_from_whitelist.sh census-rm-prod"

function prod-toolbox {
    prod-configure
    kubectl exec -it $(kubectl get pods --selector=app=census-rm-toolbox -o jsonpath='{.items[*].metadata.name}') -- /bin/bash || true
    prod-exit
}
```

The `prod-toolbox` function then gives you a single command to get into a toolbox pod and de-whitelist your cloudshell when it's finished.

### Usage
#### Configure and Whitelist
To point the cloudshell at a project and whitelist itself in the RM cluster, run
```shell script
configure_and_whitelist.sh <PROJECT_ID>
```

This changes the `gcloud` target project, generates the `kubectl` context and adds a whitelist entry to the target projects cluster for your current cloudshell IP.

#### Remove Whitelist Entry
To delete your cloudshell whitelist entry when you are finished, run
```shell script
remove_from_whitelist.sh <PROJECT_ID>
```

## Generate Fulfilment Counts

### Daily Fulfilment
To generate fulfilment counts for the day, connect to the Toolbox from cloud shell and run:
```python
fulfilment <FULFILMENT_DATE_FROM> <FULFILMENT_DATE_TO> <DB_USERNAME>
```
The fulfilment dates should be in the format of `2019-10-18T16:00:00+01:00`.

After you run this you will prompted to type in your password for the database. Once you entered in your credentials, it will create a CSV file of the counts for you
in the format of `fulfilments-<date>.csv`.

### Weekend Fulfilment count

To run the fulfilment count for the weekend run:
```python
weekendfulfilment <DB_USERNAME>
```
You'll be prompted for your password and once entered, it will generate fulfilment counts for the last 3 days.

## Work From Home (WFH) Whitelist Script
To whitelist yourself on White Lodge and Black Lodge clusters and DB, plus a bunch of other things, run this script:
```bash
./whitelist_me_for_wfh.sh
```

## Colleague (i.e. tester) Work From Home (WFH) Whitelist Script
Once you have whitelisted yourself you can easily add all the whitelisting for a colleague who is working from home by running the following script:
```bash
./whitelist_for_wfh.sh <IP ADDRESS> <NAME OF PERSON>
```
