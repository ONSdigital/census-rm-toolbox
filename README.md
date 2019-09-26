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


## Configure and Whitelist Cloud Shell Tool

This repo includes scripts to configure the cloud shell to point at an RM cluster in a project and whitelist/un-whitelist itself.  

### Prerequisits
Requres [pipenv](https://github.com/pypa/pipenv)

Install python dependencies in the clouds shell with `pipenv install --dev`

### Usage
#### Configure and Whitelist
To be able to use these scripts, you'll need to have [pyenv](https://github.com/pyenv/pyenv#installation) installed in your cloudshell environment to be able to install a python 3 version. To do this you can use these commands:
```shell script
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"
```
Once this is done, you should be able to install python version 3.7 with `pyenv install 3.7.4`.

To point the cloudshell at a project and whitelist itself in the RM cluster, run
```shell script
cloudshell_utilities/configure_and_whitelist.sh <PROJECT_ID>
```

This changes the `gcloud` target project, generates the `kubectl` context and adds a whitelist entry to the target projects cluster for your current cloudshell IP.

#### Remove Whitelist Entry
To delete your cloudshell whitelist entry when you are finished, run
```shell script
pipenv run python cloudshell_utilities/remove_cloudshell_ip.py <PROJECT_ID>
```
