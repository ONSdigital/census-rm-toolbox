# Census RM Toolbox

The most bestestest tools for make running the census big success wow.

## How to use - Message Manipulator

View messages on a queue (default 100 max):
   `pipenv run python queue_manipulator.py <queue name>`

View messages on a queue with bigger limit:
   `pipenv run python queue_manipulator.py <queue name> -l 500`
   
   
Search for message(s) on a queue:
   `pipenv run python queue_manipulator.py <queue name> -s <search text>`
   
   
Delete message from a queue:
   `pipenv run python queue_manipulator.py <queue name> <message hash> DELETE`
   
   
Move message from one queue to another:
   `pipenv run python queue_manipulator.py <queue name> <message hash> MOVE <destination queue>`
   
## How to use - Find Queues with Poison Messages

Find queues with high redelivery rate:
   `pipenv run python poison_message_queue_finder.py`