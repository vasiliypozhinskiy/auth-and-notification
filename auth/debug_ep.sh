#!/bin/bash

# Start the first process
python3 -m grpc_tools.protoc -I ./protobufs --python_out . --grpc_python_out . ./protobufs/auth.proto \
    && python3 server_grpc.py && seq 3 > hello&

/wait \
    && flask db upgrade \
    && python3 create_superuser.py \
    && python3 main.py 

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?