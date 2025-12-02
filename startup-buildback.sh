#!/bin/bash
SCRIPT_DIR=$(dirname "$(realpath "$0")")

/cnb/lifecycle/launcher $SCRIPT_DIR/post-init.sh
echo "" >> /home/renku/.bashrc
/cnb/process/jupyterlab
