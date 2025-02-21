#!/usr/bin/env bash
echo running...
source .venv/Scripts/activate
uvicorn tinkering:app --reload