#!/bin/bash
# vfs-save: сохранение VFS и повторная загрузка сохранённого файла
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/nested.xml --script scripts/stage3.txt
./run.sh --vfs /tmp/emulator_vfs.xml
