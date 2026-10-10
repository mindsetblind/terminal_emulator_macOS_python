#!/bin/bash
# Несуществующий стартовый скрипт
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/minimal.xml --script scripts/nope.txt
