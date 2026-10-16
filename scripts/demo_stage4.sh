#!/bin/bash
# Этап 4: ls, cd, echo, whoami на VFS с вложенными папками
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/nested.xml --script scripts/stage4.txt
