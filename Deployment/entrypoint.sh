#!/bin/bash

# Start the worker in the background
python3 worker.py &

# Start the Flask API
python3 api.py
