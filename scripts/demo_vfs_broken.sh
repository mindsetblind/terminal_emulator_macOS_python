#!/bin/bash
# Ошибка загрузки VFS: неверный XML
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/broken.xml
