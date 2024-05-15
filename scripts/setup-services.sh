#!/bin/bash

# Define the source file and the target directory
src="./scripts/usbfs1000.service"
target_dir="/etc/systemd/system/"

# Use the cp command to copy the file
sudo cp "$src" "$target_dir"

# Use the systemctl command to enable the service
sudo systemctl enable usbfs1000.service
sudo systemctl start usbfs1000.service
sudo systemctl status usbfs1000.service
