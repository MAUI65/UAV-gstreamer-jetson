import asyncio
import time

import gstreamer.utils as gst_utils
from UAV.manager import Gui
from UAV.mavlink import CameraClient, MAVCom, mavlink
from UAV.utils import helpers
from UAV.utils.general import boot_time_str
from gstreamer import Gst
from UAV.mavlink.vs_gimbal import GimbalClient
from gstreamer import GstVideoSource
import cv2
from UAV.camera_sdks.viewsheen.gimbal_cntrl import VS_IP_ADDRESS, VS_PORT, KeyReleaseThread

# con1, con2 = "udpin:localhost:14445", "udpout:localhost:14445"
con1, con2 = "/dev/ttyACM0", "/dev/ttyUSB1"
# con1, con2 = "/dev/ttyUSB0", "/dev/ttyUSB1"
# con1 = "udpout:192.168.122.84:14445"
con1 = "udpin:localhost:14445"
con1 = "udpin:10.42.0.1:14445"
con1 = "udpin:192.168.1.175:14445"     # this is the wlan IP of this pc
# utils.set_gst_debug_level(Gst.DebugLevel)

async def run_gimbal(width=800, height=600):


    GIMBAL_PIPELINE = gst_utils.to_gst_string([
        # 'rtspsrc location=rtsp://admin:admin@192.168.144.108:554 latency=100 ! queue',
        'udpsrc port=5010 ! application/x-rtp,encoding-name=H265',
        'rtph265depay ! h265parse ! avdec_h265',
        'decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
        'appsink name=mysink emit-signals=true sync=false async=false max-buffers=2 drop=true',
    ])
    cv2.namedWindow('Gimbal', cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow('Gimbal', width, height)

    # video = GST_Video.GST_Video()

    MAV_TYPE_GCS = mavlink.MAV_TYPE_GCS
    MAV_TYPE_CAMERA = mavlink.MAV_TYPE_CAMERA
    MAV_TYPE_GIMBAL = mavlink.MAV_TYPE_GIMBAL

    con1, con2 = "udpin:localhost:14445", "udpout:localhost:14445"
    con1 = "udpin:192.168.1.175:14445"  # this is the wlan IP of this pc
    # con1, con2 = "/dev/ttyACM0", "/dev/ttyUSB0"
    with MAVCom(con1, source_system=111) as client:
        gimbal: GimbalClient = client.add_component(GimbalClient(mav_type=MAV_TYPE_GCS, source_component=11, loglevel=10))
        ret = await gimbal.wait_heartbeat(target_system=222, target_component=mavlink.MAV_COMP_ID_GIMBAL, timeout=1)
        print(f"Heartbeat {ret = }")

        time.sleep(0.1)
        gimbal.set_target(222, mavlink.MAV_COMP_ID_GIMBAL)

        NAN = float("nan")

        print('Initialising stream...')
        waited = 0
        pipeline = GstVideoSource(GIMBAL_PIPELINE, leaky=True)
        pipeline.startup()

        while True:
            buffer = pipeline.pop()
            if buffer:
                break
            waited += 1
            print('\r  Frame not available (x{})'.format(waited), end='')
            cv2.waitKey(30)

        print('\nSuccess!\nStarting streaming - press "q" to quit.')
        # ret, (width, height) = gst_utils.get_buffer_size_from_gst_caps(Gst.Caps)
        count = 0
        gimbal_speed = 40
        while True:
            buffer = pipeline.pop(timeout=0.01)
            count += 1
            # print(f" {count = }")
            if buffer:
                cv2.imshow('Gimbal', buffer.data)

            k = cv2.waitKey(1)
            if k == ord('q') or k == ord('Q') or k == 27:
                break

            if k == ord('d'):  # Right arrow key
                print("Right arrow key pressed")
                await gimbal.set_attitude(NAN, NAN, 0.0, 0.2)
                # pan_tilt(gimbal_speed)
                KeyReleaseThread().start()

            if k == ord('a'):  # Left arrow key
                print("Left arrow key pressed")
                await gimbal.set_attitude(NAN, NAN, 0.0, -0.2)
                KeyReleaseThread().start()

            if k == ord('w'):
                print("Up arrow key pressed")
                await gimbal.set_attitude(NAN, NAN, 0.2, 0.0)
                KeyReleaseThread().start()

            if k == ord('s'):
                print("Down arrow key pressed")
                await gimbal.set_attitude(NAN, NAN, -0.2, 0.0)
                KeyReleaseThread().start()

            if k == ord('1'):
                print("Zoom in pressed")
                await gimbal.set_zoom(1)

            if k == ord('2'):
                print("Zoom out pressed")
                await gimbal.set_zoom(2)

            if k == ord('3'):
                print("Zoom stop pressed")
                await gimbal.set_zoom(3)

            if k == ord('4'):
                print("Zoom  = 1")
                await gimbal.set_zoom(4)

            if k == ord('5'):
                print("Zoom x2 in")
                await gimbal.set_zoom(5)

            if k == ord('6'):
                print("Zoom x2 out")
                await gimbal.set_zoom(6)

            if k == ord('c'):
                print("Snapshot in pressed")
                gimbal.start_capture()

        pipeline.shutdown()


async def main():
    with MAVCom(con1, source_system=111, ) as client:
        # with MAVCom(con2, source_system=222, ) as server:
        cam: CameraClient = client.add_component(CameraClient(mav_type=mavlink.MAV_TYPE_GCS, source_component=11, loglevel=20))
        ret = await cam.wait_heartbeat(target_system=222, target_component=mavlink.MAV_COMP_ID_CAMERA, timeout=3)
        print(f"Heartbeat {ret = }")
        time.sleep(0.1)

        # Run the main function using asyncio.run
        gui = Gui(camera_client=cam)
        t1 = asyncio.create_task(gui.find_cameras())
        # t2 = asyncio.create_task(gui.find_gimbals())
        t3 = asyncio.create_task(gui.run_gui())
        t4 = asyncio.create_task(run_gimbal())

        try:
            # await asyncio.gather(t1, t2, t3)
            await asyncio.gather(t1, t3, t4)
        except asyncio.CancelledError:
            print("CancelledError")
            pass




if __name__ == '__main__':
    print(f"{boot_time_str =}")
    p = helpers.start_displays(display_type='cv2', decoder='h265', num_cams=2, port=5000)
    # p = helpers.dotest()
    asyncio.run(main())
    p.terminate()
