#!/bin/bash
# Скрипт с ошибкой: выполнение прерывается
cd "$(dirname "$0")/.."
./run.sh --script scripts/error.txt
