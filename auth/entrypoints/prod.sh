#!/bin/bash

# Start the first process
/wait \
    && flask db upgrade \
    && python create_superuser.py \
    && gunicorn --worker-class gevent --workers 4 --bind 0.0.0.0:5000 main:app
    &

./entrypoints/grpc_debug.sh
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?