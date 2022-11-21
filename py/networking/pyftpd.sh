#!/bin/bash

# Launch a python FTP server
python3 -m pyftpdlib --directory=./ --port=21 --write
