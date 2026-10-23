#!/bin/bash
# Этап 5: touch и mv в памяти, затем загрузка сохранённой VFS
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/nested.xml --script scripts/stage5.txt
./run.sh --vfs /tmp/emulator_stage5.xml
