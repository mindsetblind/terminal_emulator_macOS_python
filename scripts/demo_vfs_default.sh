#!/bin/bash
# VFS не указана: создаётся VFS по умолчанию
cd "$(dirname "$0")/.."
./run.sh --script scripts/stage3.txt
