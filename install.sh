#!/bin/bash
sudo rm -r build/
sudo python setup.py build
sudo python setup.py install
sudo rm -r build/
