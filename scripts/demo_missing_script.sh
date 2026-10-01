#!/bin/bash
# Несуществующий стартовый скрипт
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/test.xml --script scripts/nope.txt
