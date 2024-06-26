#!/bin/bash

# Set the usbfs1000.service

# Define the source file and the target directory
src="./scripts/usbfs1000.service"
target_dir="/etc/systemd/system/"

# Check if the file is not present in the target directory
if [ ! -f "$target_file" ]; then
    # If the file is not present, copy it
    sudo cp "$src" "$target_dir"
fi

# Use the systemctl command to enable the service
sudo systemctl enable usbfs1000.service
sudo systemctl start usbfs1000.service

# Check the status of the service
if sudo systemctl status usbfs1000.service >/dev/null; then
    echo "usbfs1000.service is running correctly"
else
    echo "usbfs1000.service is not running correctly"
fi

echo "usbfs_memory_m = $(cat /sys/module/usbcore/parameters/usbfs_memory_mb)MB"

# Set the runserver.service

# Define the source file and the target directory
src="./scripts/runserver.service"
target_dir="/etc/systemd/system/"

# Check if the file is not present in the target directory
if [ ! -f "$target_file" ]; then
    # If the file is not present, copy it
    sudo cp "$src" "$target_dir"
fi

# sudo cp ./scripts/runserver.service /etc/systemd/system/
echo "-----------------------------------------------------"
echo "Installed runserver.service as follows:"
echo ""
cat /etc/systemd/system/runserver.service
echo "-----------------------------------------------------"

# Use the systemctl command to enable the service
sudo systemctl enable runserver.service
sudo systemctl start runserver.service

# Check the status of the service
if sudo systemctl status runserver.service >/dev/null; then
    echo "runserver.service is running correctly"
else
    echo "runserver.service is not running correctly"
    systemctl status runserver.service
fi