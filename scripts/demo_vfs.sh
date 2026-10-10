#!/bin/bash
# Только путь к VFS
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/minimal.xml
