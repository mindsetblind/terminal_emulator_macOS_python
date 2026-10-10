#!/bin/bash
# VFS: несколько файлов, включая двоичный
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/several_files.xml
