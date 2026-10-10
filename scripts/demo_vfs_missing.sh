#!/bin/bash
# Ошибка загрузки VFS: файл не найден
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/nope.xml
