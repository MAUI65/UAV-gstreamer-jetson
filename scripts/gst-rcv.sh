#!/bin/bash

# from https://gist.github.com/hum4n0id/cda96fb07a34300cdb2c0e314c14df0a
# fps
gst-launch-1.0 udpsrc port=5000 ! "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" \
! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text="GCS: Basler Cam 0" valignment=top halignment=left ! fpsdisplaysink sync=false text-overlay=true &

gst-launch-1.0 udpsrc port=5001 ! "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" \
! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text="GCS: Basler Cam 1" valignment=top halignment=left ! fpsdisplaysink sync=false text-overlay=true &

gst-launch-1.0 udpsrc port=5002 ! "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" \
! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text="GCS: RPI HQ Cam 0" valignment=top halignment=left ! fpsdisplaysink sync=false text-overlay=true &

gst-launch-1.0 udpsrc port=5003 ! "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" \
! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text="GCS: RPI HQ Cam 1" valignment=top halignment=left ! fpsdisplaysink sync=false text-overlay=true &

