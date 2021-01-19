#!/bin/bash
while [ 1 ]
do
    python -m toolbox.bulk_processing.refusal_processor
    echo "Completed bulk refusals"
    python -m toolbox.bulk_processing.new_address_processor
    echo "Completed bulk new addresses"
    python -m toolbox.bulk_processing.invalid_address_processor
    echo "Completed bulk invalid addresses"
    python -m toolbox.bulk_processing.deactivate_uac_processor
    echo "Completed bulk deactivate uacs"
    python -m toolbox.bulk_processing.address_update_processor
    echo "Completed bulk address update"
    python -m toolbox.bulk_processing.uninvalidate_address_processor
    echo "Completed bulk uninvalidate addresses"
    python -m toolbox.bulk_processing.non_compliance_processor
    echo "Completed bulk non compliance"
    echo "Now sleeping"
    sleep $BULK_PROCESSING_INTERVAL
done