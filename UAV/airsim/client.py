__all__ = ['logger', 'AirSimClient']

import random

import numpy as np
import cv2
import UAV.airsim_python_client as airsim
from ..airsim_python_client import MultirotorClient
import UAV.params as params

import logging

logging.basicConfig(format='%(asctime)-8s,%(msecs)-3d %(levelname)5s [%(filename)10s:%(lineno)3d] %(message)s',
                    datefmt='%H:%M:%S',
                    level=params.LOGGING_LEVEL)
logger = logging.getLogger(params.LOGGING_NAME)


class AirSimClient(MultirotorClient, object):
    """Multirotor Client for the Airsim simulator with higher level procedures"""
    def __init__(self, ip="",  # rpc connection address
                 port: int = 41451,  # rpc connection port
                 timeout_value=3600):  # timeout for client ping in seconds

        super(AirSimClient, self).__init__(ip, port, timeout_value)
        super().confirmConnection()
        self.objects = []

    def check_asset_exists(self,
                           name: str  # asset name
                           ) -> bool:  # exists
        """Check if asset exists"""
        return name in super().simListAssets()

    def place_object(self,  # airsim client
                     name: str,  # asset name
                     x: float,  # position x
                     y: float,  # position y
                     z: float,  # position z
                     scale: float = 1.0,  # scale
                     physics_enabled: bool = False,  # physics enabled
                     ):
        """Place an object in the simulator
            First check to see if the asset it is based on exists"""

        if not self.check_asset_exists(name):
            print(f"Asset {name} does not exist.")
            return
        desired_name = f"{name}_spawn_{random.randint(0, 100)}"
        pose = airsim.Pose(position_val=airsim.Vector3r(x, y, z), )
        scale = airsim.Vector3r(scale, scale, scale)
        self.objects.append(super(AirSimClient, self).simSpawnObject(desired_name, name, pose, scale, physics_enabled))
        # self.objects.append(super().simSpawnObject(desired_name, name, pose, scale, physics_enabled))

    def get_image(self,  # airsim client
                  camera_name: str = "0",  # camera name
                  rgb2bgr: bool = False,  # convert to bgr
                  ) -> np.ndarray:  # image
        """Get an image from camera `camera_name`"""
        responses = super(AirSimClient, self).simGetImages(
            [airsim.ImageRequest(camera_name, airsim.ImageType.Scene, False, False)])

        # print(f"airsim.client.get_image() {camera_name = }")
        response = responses[0]
        img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
        img = img1d.reshape(response.height, response.width, 3)
        if rgb2bgr:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img

    def get_images(self,  # airsim client
                   camera_names: list = ["0"],  # camera names
                   rgb2bgr: bool = False,  # convert to rgb
                   ) -> list[np.ndarray]:  # images
        """Get images from the simulator of cameras `camera_names`"""
        responses = super(AirSimClient, self).simGetImages(
            [airsim.ImageRequest(camera_name, airsim.ImageType.Scene, False, False) for camera_name in camera_names])
        images = []
        for response in responses:
            img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
            img = img1d.reshape(response.height, response.width, 3)
            if rgb2bgr:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
        return images

    def get_state(self) -> MultirotorClient:
        """Get the state of the drone"""
        return self.simGetGroundTruthKinematics()

    def takeoff(self,  # airsim client
                timeout: float = 5.0,  # timeout
                ) -> bool:  # success
        """Takeoff the drone"""
        return super().takeoffAsync(timeout_sec=timeout).join()
