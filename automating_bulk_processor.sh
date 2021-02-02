#!/bin/bash

python -m toolbox.bulk_processing.refusal_processor
ret_value=$?
if [ $ret_value -ne 0 ];
then
  echo "refusal_processor has failed"
fi
python -m toolbox.bulk_processing.new_address_processor
ret_value=$?
if [ $ret_value -ne 0 ];
then
  echo "new_address_processor has failed"
fi
python -m toolbox.bulk_processing.invalid_address_processor
ret_value=$?
if [ $ret_value -ne 0 ];
then
  echo "invalid_address_processor has failed"
fi
python -m toolbox.bulk_processing.deactivate_uac_processor
ret_value=$?
if [ $ret_value -ne 0 ];
then
  echo "deactivate_uac_processor has failed"
fi
python -m toolbox.bulk_processing.address_update_processor
ret_value=$?
if [ $ret_value -ne 0 ];
then
  echo "address_update_processor has failed"
fi
python -m toolbox.bulk_processing.uninvalidate_address_processor
ret_value=$?
if [ $ret_value -ne 0 ];then
    echo "uninvalidate_address_processor has failed"
fi