"""
BEFORE RUNNING:
---------------
1. If not already done, enable the Kubernetes Engine API
   and check the quota for your project at
   https://console.developers.google.com/apis/api/container
2. This sample uses Application Default Credentials for authentication.
   If not already done, install the gcloud CLI from
   https://cloud.google.com/sdk and run
   `gcloud beta auth application-default login`.
   For more information, see
   https://developers.google.com/identity/protocols/application-default-credentials
3. Install the Python client library for Google APIs by running
   `pip install --upgrade google-api-python-client`
"""
import os
from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()

service = discovery.build('container', 'v1', credentials=credentials)


request = service.projects().locations().clusters().get(name=f'projects/census-rm-ryangrundy/locations/europe-west2/clusters/rm-k8s-cluster')
response = request.execute()

current_authorised_networks = response['masterAuthorizedNetworksConfig']

new_ip = {'displayName': 'New IP',
          'cidrBlock': '130.211.59.47/32'}

new_authorised_networks = {'update': {'desiredMasterAuthorizedNetworksConfig': current_authorised_networks}}

new_authorised_networks['update']['desiredMasterAuthorizedNetworksConfig']['cidrBlocks'].append(new_ip)

update_request = service.projects().locations().clusters().update(name=f'projects/census-rm-ryangrundy/locations'
                                                                       f'/europe-west2/clusters/rm-k8s-cluster',
                                                                  body=new_authorised_networks)

update_request.execute()