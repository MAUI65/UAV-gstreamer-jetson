
## To Do
1. args for running on lan, local or wifi or give ip address.
2. snapshot errors on more than 2 cams
3. copy runserver to ~/bin
4. explain how to setup services




# UAV jetson


### Installation
Download UAV-gstreamer-jetson from github and create a virtual environment
- Tested on python 3.8.10  ( make sure python3 >= 3.8)

``` sh
mkdir repos
cd repos
git clone https://github.com/MAUI65/UAV-gstreamer-jetson.git
cd UAV-gstreamer-jetson
python3 -m venv 'venv'
source ./venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### Install gstreamer

``` sh
sudo apt-get install libcairo2 libcairo2-dev libgirepository1.0-dev
sudo apt install libgirepository1.0-dev
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

#### Setup Services

``` sh
./scripts/
```
#### Packaging (optional)
With the above in place, you can now build your package by running `python -m build --wheel` from the folder where the pyproject.toml resides. (You may need to install the build package first: `pip install build`.) This should create a build/ folder as well as a dist/ folder (don’t forget to add these to your .gitignore, if they aren’t in there already!), in which you will find a wheel named something like example-0.1.0-py3-none-any.whl. That file contains your package, and this is all you need to distribute it. You can install this package anywhere by copying it to the relevant machine and running `pip install example-0.1.0-py3-none-any.whl`.

When developing you probably do not want to re-build and re-install the wheel every time you have made a change to the code, and for that you can use an editable install. This will install your package without packaging it into a file, but by referring to the source directory. You can do so by running `pip install -e .` from the directory where the pyproject.toml resides. Any changes you make to the source code will take immediate effect. But note that you may need to trigger your python to re-import the code, either by restarting your python session, or for example by using autoreload in a Jupyter notebook. Also note that any changes to the configuration of your package (i.e. changes to setup.cfg) will only take effect after re-installing it with `pip install -e .` .

## Use
``` sh
runserver -h

(venv) maui@maui1:~/repos/UAV-gstreamer-jetson$ runserver -h

DEBUG  | asyncio              | 14:43:19.201 |[selector_events.py: 59] MainThread | Using selector: EpollSelector
usage: runserver [-h] [--udp UDP] [--mav MAV]

Tracking of small objects in video frames

optional arguments:
  -h, --help  show this help message and exit
  --udp UDP   set UDP IP address, ie: 10.42.0.1
  --mav MAV   set mav connection, ie: udpout:10.42.0.1:14445
```

Using config files


``` sh
runserver
```

This should output

``` sh
(venv) maui@maui1:~/repos/UAV-gstreamer-jetson$ runserver 
pynput not installed, install with pip install pynput
DEBUG  | asyncio              | 14:40:27.836 |[selector_events.py: 59] MainThread | Using selector: EpollSelector
args.udp = None, args.mav = None
INFO   | root                 | 14:40:27.838 |[run_server.py: 53] MainThread | boot_time_str = boot_time_str = '2024-05-15|14:40:27'
Found config directory at: /home/maui/repos/UAV-gstreamer-jetson/config
mach = 'jetson', conf_path = PosixPath('/home/maui/repos/UAV-gstreamer-jetson/config') mav_connection = 'udpout:10.42.0.1:14445' udp_ip = '10.42.0.1' 

{'camera_UDP_IP': '10.42.0.1', 'cam_0_UDP_port': 5000, 'cam_1_UDP_port': 5001, 'cam_2_UDP_port': 5002, 'cam_3_UDP_port': 5003, 'cam_0_flip_method': 2, 'cam_1_flip_method': 0, 'cam_2_flip_method': 2, 'cam_3_flip_method': 2, 'cam_0_pylon_id': 40407095, 'cam_1_pylon_id': 40407090, 'cam_10_UDP_port': 5010, 'UDP_bitrate': 5000000, 'usb_mount_command': '', 'image_save_path': 'snapshots', 'basler_raw_width': 3840, 'basler_raw_height': 2160, 'basler_raw_fps': 6, 'basler_stream_width': 1920, 'basler_stream_height': 1080, 'basler_stream_fps': 6, 'basler_snapshot_width': 3840, 'basler_snapshot_height': 2160, 'basler_snapshot_fps': 3, 'rpi_raw_width': 3840, 'rpi_raw_height': 2160, 'rpi_raw_fps': 6, 'rpi_stream_width': 1920, 'rpi_stream_height': 1080, 'rpi_stream_fps': 6, 'rpi_snapshot_width': 3840, 'rpi_snapshot_height': 2160, 'rpi_snapshot_fps': 3, 'mavlink': {'connection': 'udpout:10.42.0.1:14445'}}
Starting GSTCameras
John Doe                        
INFO   | uav.GSTCamera        | 14:40:27.853 |[gst_cam.py:354] MainThread | GSTCamera Started
INFO   | uav.GSTCamera        | 14:40:27.853 |[gst_cam.py:584] MainThread | Setting cam_0_flip_method = 2
INFO   | uav.GSTCamera        | 14:40:27.853 |[gst_cam.py:584] MainThread | Setting cam_0_pylon_id = 40407095
INFO   | uav.GSTCamera        | 14:40:27.854 |[gst_cam.py:584] MainThread | Setting basler_raw_width = 3840
INFO   | uav.GSTCamera        | 14:40:27.854 |[gst_cam.py:584] MainThread | Setting basler_raw_height = 2160
INFO   | uav.GSTCamera        | 14:40:27.854 |[gst_cam.py:584] MainThread | Setting basler_raw_fps = 6
INFO   | uav.GSTCamera        | 14:40:27.854 |[gst_cam.py:584] MainThread | Setting camera_UDP_IP = 10.42.0.1
INFO   | uav.GSTCamera        | 14:40:27.854 |[gst_cam.py:584] MainThread | Setting cam_0_UDP_port = 5000
INFO   | uav.GSTCamera        | 14:40:27.854 |[gst_cam.py:584] MainThread | Setting UDP_bitrate = 5000000
INFO   | uav.GSTCamera        | 14:40:27.855 |[gst_cam.py:584] MainThread | Setting basler_stream_width = 1920
INFO   | uav.GSTCamera        | 14:40:27.855 |[gst_cam.py:584] MainThread | Setting basler_stream_height = 1080
INFO   | uav.GSTCamera        | 14:40:27.855 |[gst_cam.py:584] MainThread | Setting basler_stream_fps = 6
INFO   | pygst.GstPipeline    | 14:40:32.124 |[gst_tools.py:244] MainThread | Starting GstPipeline: pylonsrc device-serial-number="40407095" ! video/x-raw, width=3840, height=2160, format=YUY2, framerate=6/1 ! nvvidconv flip-method=2 ! interpipesink name=cam_0 
DEBUG  | pygst.GstPipeline    | 14:40:32.124 |[gst_tools.py:248] MainThread | GstPipeline Setting pipeline state to PLAYING ... 
DEBUG  | pygst.GstPipeline    | 14:40:32.829 |[gst_tools.py:250] MainThread | GstPipeline Pipeline state set to PLAYING 
Opening in BLOCKING MODE 

.....


.....

GST_ARGUS: Creating output stream
CONSUMER: Waiting until producer is connected...
GST_ARGUS: Available Sensor modes :
GST_ARGUS: 3840 x 2160 FR = 29.999999 fps Duration = 33333334 ; Analog Gain range min 1.000000, max 22.250000; Exposure Range min 13000, max 683709000;

GST_ARGUS: 1920 x 1080 FR = 59.999999 fps Duration = 16666667 ; Analog Gain range min 1.000000, max 22.250000; Exposure Range min 13000, max 683709000;

GST_ARGUS: Running with following settings:
   Camera index = 1 
   Camera mode  = 0 
   Output Stream W = 3840 H = 2160 
   seconds to Run    = 0 
   Frame Rate = 29.999999 
GST_ARGUS: Setup Complete, Starting captures for 0 seconds
GST_ARGUS: Starting repeat capture requests.
CONSUMER: Producer has connected; continuing.
INFO   | uav.GSTCamera        | 14:40:34.257 |[gst_cam.py:782] MainThread | Video streaming "gstreamer_udpsink" stopped (paused) on port 5003
*** Starting MAVcom
INFO   | mavcom.MAVCom        | 14:40:34.359 |[ mavcom.py:386] Thread-5 | MAVLink Mav2: True, source_system: 222
INFO   | mavcom.CameraServer  | 14:40:34.412 |[basecomponent.py:123] MainThread | Component Started self.source_component = 100, self.mav_type = 30, self.source_system = 222
INFO   | mavcom.CameraServer  | 14:40:34.414 |[basecomponent.py:123] MainThread | Component Started self.source_component = 101, self.mav_type = 30, self.source_system = 222
INFO   | mavcom.CameraServer  | 14:40:34.417 |[basecomponent.py:123] MainThread | Component Started self.source_component = 102, self.mav_type = 30, self.source_system = 222
INFO   | mavcom.CameraServer  | 14:40:34.418 |[basecomponent.py:123] MainThread | Component Started self.source_component = 103, self.mav_type = 30, self.source_system = 222
```


## Todo
