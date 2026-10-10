#!/bin/bash
# Ошибка загрузки VFS: неверная структура
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/wrong_format.xml
