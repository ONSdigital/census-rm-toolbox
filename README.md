# Census RM Toolbox

The most bestestest tools for make running the census big success wow.

## Batched reminder scheduling
To comply with a limit on the number of cases we can send for reminder print materials in one day, some reminder runs are split into batches and spread in a wave over multiple days. 
To ensure we maximize our use of said limit, we need to maximize how many batches of cases we include in each day of this wave. The reminder batching script in this repo counts the cases that would be included from each batch and adds them to a rolling total, pulling batches in until the limit is hit.
The script can then just output the classifiers including these batches, or insert the action rules for them itself depending on the options it is run with.

### Running the reminder batch scheduler
#### Without setting up action rules
This is useful to get preliminary counts of the cases included.

Run the script with 
```bash 
reminderbatch -w <WAVE_NUMBER> -b <STARTING_BATCH_NUMBER> -a <ACTION_PLAN_ID>
```
This should output the case count for each print batch until it hits the max.

#### Setting up the action rules
**WARNING:** This will insert the action rules into the action database. Be sure you want to schedule these materials for print.

Run the script with the `--insert-rules` flag.

The `--trigger-date-time` also become necessary to schedule the rule correctly.
The trigger date time must be supplied in [rfc3339 format](https://tools.ietf.org/html/rfc3339).
```bash
reminderbatch -w <WAVE_NUMBER> -b <STARTING_BATCH_NUMBER> -a <ACTION_PLAN_ID> --insert-rules --trigger-date-time=<DATE_TIME>
```
Once the script succeeds the action rules should be present in the action database. 

**IMPORTANT:** The output should tell you the final batch included, you may need to keep this in order to start from the next batch the following day.

#### Specifying max cases
The max cases for a day defaults to 2,500,000. You may need to lower this limit to compensate for other print materials that day.
Use the flag `--max-cases <MAX_CASES>`

e.g.
```bash
reminderbatch -w <WAVE_NUMBER> -b <STARTING_BATCH_NUMBER> -a <ACTION_PLAN_ID> --max-cases 2000000
```
```bash
reminderbatch -w <WAVE_NUMBER> -b <STARTING_BATCH_NUMBER> -a <ACTION_PLAN_ID> --insert-rules --trigger-date-time=<DATE_TIME> --max-cases=1000000 
```

## Response-driven reminder scheduling
We can create response-driven action rules from a provided CSV file of LSOAs from a bucket. The format of the file name will be `<REMINDER_TYPE>_<REGION>_<DATE_TIMESTAMP>.csv`, e.g. `rdr1_E_2019-08-03T14-30-01.csv`. You will need to copy this file from the bucket to your cloud shell, then copy to the running toolbox instance.

#### Get counts of cases for response-driven reminders
To get a count of cases using the LSOAs file:
```bash
reminderlsoacount <LSOA_FILE.CSV> --action-plan-id <ACTION_PLAN_ID>
```

#### Without setting up action rules
This is useful to get the shape of what the classifiers will look like when used in the action rule.

Run the script with:
```bash 
reminderlsoa <LSOA_FILE.CSV> --reminder-action-type <ACTION_TYPE> --action-plan-id <ACTION_PLAN_ID>
```
This should output the classifiers used for the action rule.

#### Setting up the action rules
**WARNING:** This will insert the action rules into the action database. Be sure you want to schedule these materials for print.

**WARNING:** There is currently NO validation on the LSOAs file. You will need to be sure that the business area have validated the LSOAs for RM to ingest. We will process whatever they provide, as agreed.
Run the script with the `--trigger-date-time` and `--insert-rule` flags. The trigger date time must be supplied in [rfc3339 format](https://tools.ietf.org/html/rfc3339):

```bash
reminderlsoa <LSOA_FILE.CSV> --reminder-action-type <ACTION_TYPE> --action-plan-id <ACTION_PLAN_ID> --trigger-date-time <DATE_TIME> --insert-rule 
```
Once the script succeeds the action rule should be present in the action database.

## Bulk Processing
### Bulk Refusals
Bulk refusals files can be dropped in a bucket for processing, the file format required is 
```csv
case_id,refusal_type
16400b37-e0fb-4cf4-9ddf-728abce92049,HARD_REFUSAL
180e2636-d8e5-4949-bced-f7a0c532190c,EXTRAORDINARY_REFUSAL
```
Including the header row.

The refusal type must be one of 
```
HARD_REFUSAL
EXTRAORDINARY_REFUSAL
```

The file should be placed in the configured bulk refusals bucket with a name matching `refusals_*.csv`, then the processor can be run with
```shell script
bulkrefusals
```
Rows which are successfully processed will be added to `PROCESSED_refusals_*.csv` and errored rows be appended to `ERROR_refusals_*.csv` with the corresponding error details written to `ERROR_DETAIL_refusals_*.csv`.

### Bulk New Addresses
Bulk new addresses can be dropped in a bucket for processing, the file format required is
```csv
UPRN,ESTAB_UPRN,ADDRESS_TYPE,ESTAB_TYPE,ADDRESS_LEVEL,ABP_CODE,ORGANISATION_NAME,ADDRESS_LINE1,ADDRESS_LINE2,ADDRESS_LINE3,TOWN_NAME,POSTCODE,LATITUDE,LONGITUDE,OA,LSOA,MSOA,LAD,REGION,HTC_WILLINGNESS,HTC_DIGITAL,TREATMENT_CODE,FIELDCOORDINATOR_ID,FIELDOFFICER_ID,CE_EXPECTED_CAPACITY,CE_SECURE,PRINT_BATCH
29763560087,42815171218,HH,HOUSEHOLD,U,RD04,,34 Definitely a street,,,Armless Hamlet,EI7 1PW,120.4446,-95.6070,E32528638,E93337100,E91038113,E34651127,E66650625,2,4,HH_LP1E,,,0,0,86
```

This follows the same validation rules as the sample loader.

To process the file it needs to be put in the bulk new addresses bucket with a name matching `new_addresses_*.csv`. The processor can then be run with
```shell script
bulknewaddresses
```

Rows which are successfully processed will be added to `PROCESSED_new_addresses_*.csv` and errored rows be appended to `ERROR_new_addresses_*.csv` with the corresponding error details written to `ERROR_DETAIL_new_addresses_*.csv`.

### Bulk Invalid Addresses
Bulk invalid addresses files can be dropped in a bucket for processing, the file format required is 
```csv
case_id,reason
16400b37-e0fb-4cf4-9ddf-728abce92049,DEMOLISHED
180e2636-d8e5-4949-bced-f7a0c532190c,DOES_NOT_EXIST
```
Including the header row.

The file should be placed in the configured bulk invalid addresses bucket with a name matching `invalid_addresses_*.csv`, then the processor can be run with
```shell script
bulkinvalidaddresses
```
Rows which are successfully processed will be added to `PROCESSED_invalid_addresses_*.csv` and errored rows be appended to `ERROR_invalid_addresses_*.csv` with the corresponding error details written to `ERROR_DETAIL_invalid_addresses_*.csv`.

### Bulk Un-Invalidate Address
Bulk un-invalidating addresses can be dropped in a bucket for processing, the file format required is
```csv
CASE_ID
16400b37-e0fb-4cf4-9ddf-728abce92049
```
Including the header row

The file should be placed in the configured bulk uninvalidated addresses bucket with a name matching `uninvalidated_addresses_*.csv`, then the processor can be run with
```shell script
bulkuninvalidateaddresses
```
Rows which are successfully processed will be added to `PROCESSED_uninvalidated_addresses_*.csv` and errored rows be appended to `ERROR_uninvalided_addresses_*.csv` with the corresponding error details written to `ERROR_DETAIL_uninvalidated_addresses_*.csv`.

### Bulk Deactivate UAC
Bulk deactivate uac files can be dropped in a bucket for processing, the file format required is
```csv
qid
0123456789
```
Including the header row.

The file should be placed in the configured bulk deactivate uac bucket with a name matching `deativate_uac_*.csv`, then the processor can be run with
```shell script
bulkdeactivateuacs
```

### Bulk Address Update
Bulk address updates can be dropped in a bucket for processing, the file format required is
```csv
CASE_ID,UPRN,ESTAB_UPRN,ESTAB_TYPE,ABP_CODE,ORGANISATION_NAME,ADDRESS_LINE1,ADDRESS_LINE2,ADDRESS_LINE3,TOWN_NAME,POSTCODE,LATITUDE,LONGITUDE,OA,LSOA,MSOA,LAD,HTC_WILLINGNESS,HTC_DIGITAL,TREATMENT_CODE,FIELDCOORDINATOR_ID,FIELDOFFICER_ID,CE_EXPECTED_CAPACITY,CE_SECURE,PRINT_BATCH
ce00bce1-4d3f-400c-95df-a3d8150622c3,123456789,987654321,ROYAL HOUSEHOLD,4321,foo_incorporated,foo flat1,foo some road,foo somewhere,foo some town,F00 BAR,0.0,127.0,foo_1,foo_2,foo_3,foo_4,5,3,HH_LP1E,ABC123,XYZ999,10,1,99
```

This follows similar validation rules as the sample loader.

To process the file it needs to be put in the bulk address update bucket with a name matching `address_updates_*.csv`. The processor can then be run with
```shell script
bulkaddressupdate
```

Rows which are successfully processed will be added to `PROCESSED_address_updates_*.csv` and errored rows be appended to `ERROR_address_updates_*.csv` with the corresponding error details written to `ERROR_DETAIL_address_updates_*.csv`.


### Bulk Non-Compliance
Bulk non-compliance files can be dropped in a bucket for processing, the file format required is 
```csv
CASE_ID,NC_STATUS,FIELDCOORDINATOR_ID,FIELDOFFICER_ID
16400b37-e0fb-4cf4-9ddf-728abce92049,NCL,ABC123,XYZ999
180e2636-d8e5-4949-bced-f7a0c532190c,NCF,ABC123,XYZ999
```
Including the header row.

The non-compliance status must be one of 
```
NCL - for 1st letter
NCF - for field follow up
```

The file should be placed in the configured bulk non-compliance bucket with a name matching `non_compliance_*.csv`, then the processor can be run with
```shell script
bulknoncompliance
```
Rows which are successfully processed will be added to `PROCESSED_non_compliance_*.csv` and errored rows be appended to `ERROR_non_compliance_*.csv` with the corresponding error details written to `ERROR_DETAIL_non_compliance_*.csv`.


### Find Invalid Address Case IDs from UPRN File
Run Book - https://collaborate2.ons.gov.uk/confluence/display/SDC/Find+Invalid+Address+Case+ID%27s+by+UPRN+-+ADDRESS_DELTA

When we receive a file of UPRNs for cases that have been identified as invalid addresses, this feature will call the Case API against the UPRNs provided and generate a new file in the bulk invalid address bucket and run the bulk processor against the file.

This is done by running:
```shell script
invalidaddressdelta <file_name>
```

The rows which are successfully processed will be added to `PROCESSED_invalid_addresses_*.csv`

The file format will be:
```csv
case_id,reason
16400b37-e0fb-4cf4-9ddf-728abce92049,ADDRESS_DELTA
180e2636-d8e5-4949-bced-f7a0c532190c,ADDRESS_DELTA
```
Including the header row. The reason given will always be `ADDRESS_DELTA`.


### Build Bulk Address Update From Sample File

To enable updating case data from an amended sample file (without knowing the case IDs), this script will run through a sample file looking up the UPRNs in the case API and build a address update file that can be run through the bulk processor. These files must be manually copied onto and off the toolbox pod. 

This script will fail if there are more than one case IDs or no matching any UPRN as we need to be able to match one and only one case.

Note that the columns `REGION`, `ADDRESS_LEVEL` and `ADDRESS_TYPE` are included in the sample file but not in the address update. 

Usage:
```
python -m toolbox.bulk_processing.build_address_update_from_sample <PATH TO SAMPLE FOR UPDATE>
```
(outside the pod using `pipenv run python`)

The output file will be written to `address_updates_<SOURCE FILE NAME>` in the current working directory.

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

There is an option to filter messages, this works by regex on every field in the message summary.
Some common examples are:

```
    ^Case ID.*not present$ 
```

```
    ^Questionnaire Id.*not found!
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
   python -m toolbox.message_tools.get_pubsub_messages <subscription name> <subscription project id>
   ```
   
View messages on a pubsub subscription with bigger limit:
   ```bash
   python -m toolbox.message_tools.get_pubsub_messages <subscription name> <subscription project id> -l <limit>
   ```
   
Search for a message:
   ```bash
   python -m toolbox.message_tools.get_pubsub_messages <subscription name> <subscription project id> -s <search term>
   ```

Delete message on pubsub subscription:   
   ```bash
   python -m toolbox.message_tools.get_pubsub_messages <subscription name> <subscription project id> <message_id> DELETE
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
python -m toolbox.message_tools.put_message_on_bucket <subscription name> <subscription project id> <bucket name> <message_id>
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
python -m toolbox.message_tools.publish_message_from_bucket <topic name> <project id> <bucket blob name> <bucket name>
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
   
## SFTP Support Login
To connect to SFTP (i.e. GoAnywhere) to check print files (read only). 

### Usage
```bash
doftp
```

## Uploading a file to a bucket
To upload a file to a bucket.

### Usage
```bash
uploadfiletobucket <file> <project> <bucket>
```

## Running in Kubernetes
To run the toolbox in a kubernetes environment, you'll have to create the deployment using the YAML files in census-rm-kubernetes. If you do not have a Cloud SQL Read Replica, use the dev deployment YAML file

Once the pod is up, you can connect to it:
```bash
kubectl exec -it $(kubectl get pods --selector=app=census-rm-toolbox -o jsonpath='{.items[*].metadata.name}') -- /bin/bash
```
