""" Run this on the drone to start the cameras and the MAVCom server"""

import asyncio
import time

import cv2

from gstreamer import GstContext
from UAV.cameras.gst_cam import GSTCamera, logging
from UAV.logging import LogLevels
from mavcom.mavlink import MAVCom, mavlink
from UAV.mavlink import CameraServer
# from UAV.mavlink.gimbal_server_viewsheen import GimbalServerViewsheen
from UAV.utils import config_dir, get_platform, boot_time_str, toml_load
# import platform
# import subprocess

# from pathlib import Path

# print(platform.processor())

# cli = GimbalClient(mav_connection=None, source_component=11, mav_type=MAV_TYPE_GCS, debug=False)
# gim1 = GimbalServer(mav_connection=None, source_component=22, mav_type=MAV_TYPE_CAMERA, debug=False)

# con2 = "udpout:10.42.0.1:14445"
# con2 = "udpout:192.168.1.175:14445"
# con2 = "udpout:localhost:14445"
# con1, con2 = "/dev/ttyACM0", "/dev/ttyUSB0"

# ENCODER = '265enc'
# ENCODER = ''

# def config_dir():
#     return Path(__file__).parent.parent / "config"
#
# con2 = "udpout:192.168.1.175:14445" if mach == 'jetson' else "udpout:localhost:14445"
# con2 = "/dev/ttyUSB0" if mach == 'jetson' else "/dev/ttyUSB1"


async def main():
    logging.info(f"boot_time_str = {boot_time_str = }")

    mach = get_platform()
    conf_path = config_dir()
    config_dict = toml_load(conf_path / f"{mach}_server_config.toml")
    mav_connection = config_dict['mavlink']['connection']

    print(f"{mach = }, {conf_path = } {mav_connection = }")
    print(config_dict)

    #usb_mount_command = config_dict['usb_mount_command']
    #subprocess.run(usb_mount_command.split())

    print("Starting GSTCameras")
    cam_0 = GSTCamera(config_dict, camera_dict=toml_load(conf_path / f"{mach}_cam_0.toml"), loglevel=LogLevels.DEBUG)
    cam_1 = GSTCamera(config_dict, camera_dict=toml_load(conf_path / f"{mach}_cam_1.toml"), loglevel=LogLevels.INFO)
    cam_2 = GSTCamera(config_dict, camera_dict=toml_load(conf_path / f"{mach}_cam_2.toml"), loglevel=LogLevels.INFO)
    cam_3 = GSTCamera(config_dict, camera_dict=toml_load(conf_path / f"{mach}_cam_3.toml"), loglevel=LogLevels.INFO)

    print("*** Starting MAVcom")
    try:
        UAV_server = MAVCom(mav_connection, source_system=222, loglevel=LogLevels.DEBUG)
    except Exception as e:
        print(f"*** MAVCom failed to start: {e} **** ")
        cam_0.close()
        cam_1.close()
        cam_2.close()
        cam_3.close()
        # cam_4.close()
        exit(1)

    with GstContext():
        with UAV_server:  # This runs on drone
            UAV_server.add_component(CameraServer(mav_type=mavlink.MAV_TYPE_CAMERA, source_component=mavlink.MAV_COMP_ID_CAMERA, camera=cam_0, loglevel=20))
            UAV_server.add_component(CameraServer(mav_type=mavlink.MAV_TYPE_CAMERA, source_component=mavlink.MAV_COMP_ID_CAMERA2, camera=cam_1, loglevel=20))
            UAV_server.add_component(CameraServer(mav_type=mavlink.MAV_TYPE_CAMERA, source_component=mavlink.MAV_COMP_ID_CAMERA3, camera=cam_2, loglevel=20))
            UAV_server.add_component(CameraServer(mav_type=mavlink.MAV_TYPE_CAMERA, source_component=mavlink.MAV_COMP_ID_CAMERA4, camera=cam_3, loglevel=20))

            while True:
                time.sleep(0.5)

    cv2.destroyAllWindows()
    time.sleep(0.01)
    cam_0.close()
    cam_1.close()
    cam_2.close()
    cam_3.close()
if __name__ == '__main__':
    print(__doc__)
    asyncio.run(main())