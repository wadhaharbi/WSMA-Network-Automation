#!/bin/bash

cd ~/network-automation

ansible-playbook -i inventory full-automation.yml --tegs $1
