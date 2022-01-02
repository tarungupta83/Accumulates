#!/bin/sh
eval "$(conda shell.bash hook)"
cd "$(dirname "$0")"
conda activate "$(cd "$(dirname "$0")" && pwd)"/".venv"
python start