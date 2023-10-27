import time

from UAV.camera.airsim_cam import AirsimCamera
from UAV.logging import LogLevels
from UAV.utils import start_displays
from UAV.utils.general import toml_load, config_dir
from gstreamer import GstContext

# gst_utils.set_gst_debug_level(Gst.DebugLevel.FIXME)
if __name__ == '__main__':

    UDP_ENCODER = 'h264'
    # UDP_ENCODER = 'raw-video'
    camera_dict_0 = toml_load(config_dir() / "airsim_cam_front.toml")
    camera_dict_1 = toml_load(config_dir() / "airsim_cam_left.toml")
    p = start_displays(num_cams=2, port=5000)

    with GstContext():
        with AirsimCamera(camera_name='front', camera_dict=camera_dict_0, loglevel=LogLevels.INFO) as air_cam_0:
            # if True:
            with AirsimCamera(camera_name='left', camera_dict=camera_dict_1, loglevel=LogLevels.INFO) as air_cam_1:


                # air_cam_1.video_start_streaming()
                for i in range(10):
                    air_cam_0.video_start_streaming()
                    air_cam_1.video_start_streaming()
                     # air_cam_1.pause()
                    time.sleep(2)
                    air_cam_0.video_stop_streaming()
                    air_cam_1.video_stop_streaming()

                    time.sleep(2)
                # air_cam_1.video_stop_streaming()
                time.sleep(1)
                print(f"Waiting for capture thread to finish")

    p.terminate()
