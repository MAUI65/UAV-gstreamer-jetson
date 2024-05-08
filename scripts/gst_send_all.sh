HOST=192.168.50.26
PYLON_WIDTH=3840
PYLON_HEIGHT=2160
PYLON_FPS=8

RPI_WIDTH=1920
RPI_HEIGHT=1080
RPI_FPS=8

gst-launch-1.0 pylonsrc device-index=0 ! "video/x-raw,format=YUY2, width=$PYLON_WIDTH, height=$PYLON_HEIGHT, framerate=$PYLON_FPS/1" ! nvvidconv ! video/x-raw,width=1280,height=720 ! tee name=t \
t. ! queue ! textoverlay text="Jetson: Basler Cam 0" valignment=top halignment=left ! fpsdisplaysink sync=false text-overlay=true \
t. ! queue ! nvvidconv ! nvv4l2h264enc insert-sps-pps=true ! rtph264pay ! udpsink host=$HOST port=5000 &


gst-launch-1.0 pylonsrc device-index=1 ! "video/x-raw,format=YUY2, width=$PYLON_WIDTH, height=$PYLON_HEIGHT, framerate=$PYLON_FPS/1" ! nvvidconv ! video/x-raw,width=1280,height=720 ! tee name=t \
t. ! queue ! textoverlay text="Jetson: Basler Cam 1" valignment=top halignment=left ! fpsdisplaysink sync=false text-overlay=true \
t. ! queue ! nvvidconv ! nvv4l2h264enc insert-sps-pps=true ! rtph264pay ! udpsink host=$HOST port=5001 &

gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! "video/x-raw(memory:NVMM), width=$RPI_WIDTH, height=$RPI_HEIGHT, framerate=$RPI_FPS/1, format=NV12" ! nvvidconv ! video/x-raw,width=1280,height=720 ! tee name=t \
t. ! queue ! textoverlay text="Jetson: RPI Cam 0" valignment=top halignment=left ! nvvidconv ! nvegltransform ! nveglglessink -e \
t. ! queue ! nvvidconv ! nvv4l2h264enc insert-sps-pps=true ! rtph264pay ! udpsink host=$HOST port=5002 &

gst-launch-1.0 nvarguscamerasrc sensor_id=1 ! "video/x-raw(memory:NVMM), width=$RPI_WIDTH, height=$RPI_HEIGHT, framerate=$RPI_FPS/1, format=NV12" ! nvvidconv ! video/x-raw,width=1280,height=720 ! tee name=t \
t. ! queue ! textoverlay text="Jetson: RPI Cam 1" valignment=top halignment=left ! nvvidconv ! nvegltransform ! nveglglessink -e \
t. ! queue ! nvvidconv ! nvv4l2h264enc insert-sps-pps=true ! rtph264pay ! udpsink host=$HOST port=5003 
