#!/bin/bash

flake8 ./ --max-line-length=120
coverage run --source='.' manage.py test
coverage report -m
