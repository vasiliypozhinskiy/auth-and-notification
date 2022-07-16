#!/bin/bash

# Start the first process
python3 -m grpc_tools.protoc -I ./protobufs --python_out . --grpc_python_out . ./protobufs/auth.proto && python3 server_grpc.py &

/wait \
    && flask db upgrade \
    && python create_superuser.py \
    && gunicorn --worker-class gevent --workers 4 --bind 0.0.0.0:5000 main:app


# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?