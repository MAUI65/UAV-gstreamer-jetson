
#### Gstreamer fail to load deepstream plugins in TX2NX
https://forums.balena.io/t/gstreamer-fail-to-load-deepstream-plugins-in-tx2nx/368378

#### Building on jetson orin nx deepstream 6.4 ubuntu 22 #95
https://github.com/basler/gst-plugin-pylon/issues/95

####  Unable to build 7.4.0 with NVMM support on Linux / Jetson Orin #82 
https://github.com/basler/gst-plugin-pylon/issues/82

#### Remove gstreamer cach to rescan plugins
```bash
rm -rf ~/.cache/gstreamer-1.0
```

#### Problems with avdec_h264 running on the jetson orin
- see [Unable find avdec_h264 after intsalled gstreamer plug-ins into Jetson AGX Orin](https://forums.developer.nvidia.com/t/unable-find-avdec-h264-after-intsalled-gstreamer-plug-ins-into-jetson-agx-orin/226575/5    )

 Run this first  
```bash
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1
```
Alternativily place in .bashrc
```bash
echo 'export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1' >> ~/.bashrc
```


## To Do
args for running on lan, local or wifi or give ip address.



/usr/lib/aarch64-linux-gnu/gstreamer-1.0/libgstpylon.so
/usr/lib/aarch64-linux-gnu/gstreamer-1.0/libgstinterpipe.so


sudo ldd /usr/lib/x86_64-linux-gnu/gstreamer-1.0/libgstpylon.so


sudo ldd /usr/lib/x86_64-linux-gnu/gstreamer-1.0/libgstpylon.so

The `ldd` command is used to print the shared libraries required by a program. When you run `ldd` with `sudo`, you're running it as the root user.

The difference in output between running `ldd` as a normal user and running it with `sudo` could be due to differences in the environment variables between the two users. In particular, the `LD_LIBRARY_PATH` environment variable, which specifies directories to search for shared libraries, could be set differently for the two users.

When you run `ldd` as a normal user, it uses your user's environment variables. When you run `ldd` with `sudo`, it uses the root user's environment variables. If the `LD_LIBRARY_PATH` environment variable includes additional directories for your user that are not included for the root user, then running `ldd` as your user could find more shared libraries than running `ldd` with `sudo`.

To see the environment variables for your user, you can use the `printenv` command. To see the environment variables for the root user, you can use `sudo printenv`. Comparing the output of these two commands could help you identify any differences in the `LD_LIBRARY_PATH` environment variable.

sudo su - root

/home/maui/repos/UAV-gstreamer-jetson/venv/bin/python /home/maui/repos/UAV-gstreamer-jetson/src/examples/howto_access_features.py

The service
``` sh
[Unit]
Description=run on startup
After=rc-local.service

[Service]
Type=simple
Restart=no
RestartSec=10
ExecStart=/home/maui/repos/UAV-gstreamer-jetson/venv/bin/runserver
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```