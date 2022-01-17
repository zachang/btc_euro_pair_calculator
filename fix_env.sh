#!/usr/bin/env bash
echo "Fixing env"
poetry env use python3.9
poetry install
poetry update
echo "Downgraded to python3.9"
