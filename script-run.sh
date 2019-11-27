#!/bin/bash
set -e
if [ "$1" == "train" ]; then
	python3 /home/training/TRAIN.py
else 
	if [ "$1" == "predict" ]; then
		python3 /home/predict/PREDICT.py
	else
		python3 /home/healthcheck.py
	fi
fi