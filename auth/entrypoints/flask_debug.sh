#!/bin/bash
  
/wait && flask db upgrade && python3 create_superuser.py && python3 main.py & 