#!/bin/bash

USBFS_SIZE=1000  # 1000MB

# Increase the usbfs_memory_mb memory for the current session.
if [ -f /sys/module/usbcore/parameters/usbfs_memory_mb ] ; then
    echo "Parameter usbfs_memory_mb in /sys/module/usbcore/parameters changed to $USBFS_SIZE"
    sudo sh -c "echo $USBFS_SIZE > /sys/module/usbcore/parameters/usbfs_memory_mb"
else
    echo "Cannot change usbfs_memory_mb because /sys/module/usbcore/parameters/usbfs_memory_mb does not exist"
fi

