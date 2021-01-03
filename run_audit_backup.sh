#!/usr/bin/env bash

gsutil -m rsync -x ".*sql*." -r ~/.audit gs://$TOOLBOX_AUDIT_BUCKET