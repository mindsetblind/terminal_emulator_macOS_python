#!/bin/bash
# VFS: больше трёх уровней вложенности
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/nested.xml
