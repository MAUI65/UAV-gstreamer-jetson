

__all__ = ['logger', 'DefaultParams', 'GstStream', 'ping_ip', 'Mqtt']


from ..imports import *   # TODO why is this relative import on nbdev_export?
from fastcore.utils import *
import gi
import numpy as np
import threading
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import subprocess
import platform

import paho.mqtt.client as mqtt_client

import time

from pathlib import Path
import logging
import UAV.params as params


logging.basicConfig(format='%(asctime)-8s,%(msecs)-3d %(levelname)5s [%(filename)10s:%(lineno)3d] %(message)s',
                    datefmt='%H:%M:%S',
                    level=params.LOGGING_LEVEL)  # Todo add this to params
logger = logging.getLogger(params.LOGGING_NAME)


from dataclasses import dataclass

@dataclass
class DefaultParams():
    camera_dev = "CAM-0"
    cameras = {
        "CAM-0": {
            "gst": [
                'videotestsrc pattern=smpte is-live=true ! tee name=t ',
                't. ! queue leaky=2 ! videoconvert ! videorate drop-only=true ! video/x-raw,framerate=10/1,format=(string)BGR ! ',
                '   videoconvert ! appsink name=sink emit-signals=true  sync=false async=false  max-buffers=2 drop=true ',
                't. ! queue leaky=2 ! valve name=myvalve drop=true ! video/x-raw,format=I420,width=640,height=480 ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5000',
                ],
            "udp": True,
            "host": "127.0.0.1",
            "port": 5000,
        },
        "CAM-1": {
            "gst": [
                'videotestsrc pattern=ball is-live=true ! tee name=t ',
                't. ! queue leaky=2 ! videoconvert ! videorate drop-only=true ! video/x-raw,framerate=10/1,format=(string)BGR ! ',
                '   videoconvert ! appsink name=sink emit-signals=true  sync=false async=false  max-buffers=2 drop=true ',
                't. ! queue leaky=2 ! valve name=myvalve drop=true ! video/x-raw,format=I420,width=640,height=480 ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5001',
                ],
            "udp": True,
            "host": "127.0.0.1",
            "port": 5001,
        },
        "CAM-2": {
            "gst": [
                'videotestsrc pattern=snow is-live=true ! tee name=t ',
                't. ! queue leaky=2 ! videoconvert ! videorate drop-only=true ! video/x-raw,framerate=10/1,format=(string)BGR ! ',
                '   videoconvert ! appsink name=sink emit-signals=true  sync=false async=false  max-buffers=2 drop=true ',
                't. ! queue leaky=2 ! valve name=myvalve drop=true ! video/x-raw,format=I420,width=640,height=480 ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5002',
                ],
            "udp": True,
            "host": "127.0.0.1",
            "port": 5002,
        },
        "CAM-3": {
            "gst": [
                'videotestsrc pattern=pinwheel is-live=true ! tee name=t ',
                't. ! queue leaky=2 ! videoconvert ! videorate drop-only=true ! video/x-raw,framerate=10/1,format=(string)BGR ! ',
                '  videoconvert ! appsink name=sink emit-signals=true  sync=false async=false  max-buffers=2 drop=true ',
                't. ! queue leaky=2 ! valve name=myvalve drop=true ! video/x-raw,format=I420,width=640,height=480 ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5003',
                ],
            "udp": True,
            "host": "127.0.0.1",
            "port": 5003,
            },
    
       }

    # socket address and port
    mqqt_address='127.0.0.1'
    src_port=1234


# https://github.com/gkralik/python-gst-tutorial/blob/master/basic-tutorial-4.py

class GstStream():
    """"GstStream  class using gstreamer
        Create and start a GStreamer pipe
            gst_pipe = GstStream() 
            The valve is a simple element that drops buffers when the drop property is set to TRUE and lets then through otherwise. 
        """

    def __init__(self, name:str='CAM-0' # camera name
                 , gstcommand:List=['videotestsrc ! autovideosink'] # gst command list
                 , address:str='127.0.0.1'  # udp address
                 , port:int=5000): # udp port
        self.cname = self.__class__.__name__
        Gst.init(None)
        assert isinstance(name, str), "name must be a string"
        self.name = name
        assert isinstance(gstcommand, List), "gstcommand must be a list"
        self.gstcommand = gstcommand
        self.address = address
        self.port = port

        self.latest_frame = self._new_frame = None
        self.start_gst()
        self._thread = threading.Thread(target=self.msg_thread_func, daemon=True)
        self._stop_thread = False
        # self._thread .start()
        logger.info(f"{self.cname} started")

    def start_gst(self):
        """ Start gstreamer pipeline and sink
        """
        if self.gstcommand != []:
            command = ' '.join(self.gstcommand)
        else:
            command = 'videotestsrc ! autovideosink'
            command = "videotestsrc ! tee name=t t. ! queue ! autovideosink " +\
                       " t. ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert ! " +\
                       " queue ! appsink name=sink emit-signals=true "

        # print (command)
        self.pipeline = Gst.parse_launch(command)
        self.appsink = self.pipeline.get_by_name('sink')
        if self.appsink is None:
            logger.warning(f"{self.cname} Error: appsink is None")
        else:
            self.appsink.connect('new-sample', self.sink_callback)
        
        # appsrc = self.pipeline.get_by_name('source')
        # if appsrc is None:
        #     logger.warning(f"{self.cname} Error: appsrc is None")
        # else:
        #     appsrc.connect('need-data', self.callback)
        #     
        #     
        # try:
        #     self.appsink.connect('new-sample', self.callback)
        # except:
        #     logger.error(f"{self.cname} Error connecting to callback")
        #
        self.pipeline.set_state(Gst.State.PLAYING)
        self.bus = self.pipeline.get_bus() # https://lazka.github.io/pgi-docs/Gst-1.0/classes/Bus.html
        # allow bus to emit messages to main thread
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message) # https://lazka.github.io/pgi-docs/GObject-2.0/classes/Object.html#GObject.Object.connect
        
    def on_message(self, bus:Gst.Bus
                   , message: Gst.Message):     
        """Callback function for bus message
                Gstreamer Message Types and how to parse
                https://lazka.github.io/pgi-docs/Gst-1.0/flags.html#Gst.MessageType
        """
        print("on_message")
        t = message.type
        if t == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            logger.info(f"{self.cname} End-Of-Stream reached.")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(f"{self.cname} Error received from element {message.src.get_name()}: {err}")
            logger.error(f"{self.cname} Debugging information: {debug}")
            self.pipeline.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            logger.warning(f"{self.cname} Warning received from element {message.src.get_name()}: {err}")
            logger.warning(f"{self.cname} Debugging information: {debug}")
        return True
        
    def msg_thread_func(self):   
        "Run thread"
        # Poll for messages on the bus (like EOS or ERROR), and handle them
        while not self._stop_thread:
            message = self.bus.timed_pop_filtered(100*Gst.MSECOND, Gst.MessageType.ANY)
            if message is None:
                continue
    
            if message.type == Gst.MessageType.EOS:
                logger.info("End-Of-Stream reached.")
                break
            elif message.type == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                logger.error(f"{self.cname} Error received from element {message.src.get_name()}: {err}")
                logger.error(f"{self.cname} Debugging information: {debug}")
                break
        # # Cleanup 
        # logger.info(f"{self.cname} Stopping pipeline")
        # self.pipeline.set_state(Gst.State.NULL)
        
    @staticmethod
    def gst_to_opencv(sample):
        "Transform byte array into np array"
        buf = sample.get_buffer()
        caps_structure = sample.get_caps().get_structure(0)
        array = np.ndarray(
            ( caps_structure.get_value('height'),caps_structure.get_value('width'), 3),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        """ Get Frame
        Returns:
            np.ndarray: latest retrieved image frame
        """
        if self.frame_available():
            self.latest_frame = self._new_frame
            # reset to indicate latest frame has been 'consumed'
            self._new_frame = None
        return self.latest_frame

    def frame_available(self, 
                             timeout=2  # timeout in seconds
                             )->bool:   # true if a new frame is available within timeout    
        """Wait for a new frame to be available"""
        elapsetime = 0
        while self._new_frame is None:
            time.sleep(0.01)
            elapsetime += 0.01
            if elapsetime > timeout:
                return False
        return True
    
            
    def sink_callback(self, sink):
        sample = sink.emit('pull-sample')
        # if not self.pause:
        self._new_frame = self.gst_to_opencv(sample)

        return Gst.FlowReturn.OK
    
    # def need_data(self, appsrc, length):
    #     """ Push data into the appsrc when needed
    #     """
    #     if self._new_frame is None:
    #         return
    #     data = self._new_frame.tostring()
    #     appsrc.emit("push-buffer", Gst.Buffer.new_wrapped(data))
    #     self._new_frame = None
        
        # data = self.frame.tobytes()
        # buf = Gst.Buffer.new_allocate(None, len(data), None)
        # buf.fill(0, data)
        # buf.duration = self.duration
        # timestamp = self.number_frames * self.duration
        # buf.pts = buf.dts = int(timestamp)
        # buf.offset = timestamp
        # 
        # retval = src.emit('push-buffer', buf)
        # info = f"frame {self.number_frames}, duration {self.duration / Gst.SECOND}, code {codes[0]} s"
        # # print(info)
        # if retval != Gst.FlowReturn.OK:
        #     print(retval)
        
    def close(self):
        """Close gstreamer pipeline
        see https://github.com/gkralik/python-gst-tutorial/blob/master/basic-tutorial-1.py
        """
        self.pipeline.send_event(Gst.Event.new_eos())   # Todo does not seem to stop pipeline
        self.pipeline.set_state(Gst.State.NULL)
        self._stop_thread = True
        # self._thread.join()
        logger.info(f"{self.cname}  closed")

        
    def __enter__(self):
        """with context manager"""

        return self  # This value is assigned to the variable after 'as' in the 'with' statement
    
    def __exit__(self, exc_type, exc_value, traceback):
        """with context manager"""
        self.close()
        # If an exception occurred, exc_type, exc_value, and traceback will be provided
        # Returning False (or None) will propagate the exception
        # Returning True will suppress it
        return False
    
# with GstStream("CAM-0", gstcommand) as gs:
#     gs.cls()


@patch
def set_valve_state(self:GstStream
                    , valvename: str  # name of valve element
                    , drop_state: bool  # True = drop frames
                    ):
    """Set the state of a valve element
    The valve is a simple element that drops buffers when the drop property is set to TRUE and lets then through otherwise. """
    valve = self.pipeline.get_by_name(valvename)
    valve.set_property("drop", drop_state)
    new_drop_state = valve.get_property("drop")
    logger.info(f"{self.name}: new drop state: {new_drop_state}")



@patch
def get_valve_state(self:GstStream
                    , valvename: str  # name of valve element
                    ):
    "Get the state of a valve element"

    valve = self.pipeline.get_by_name(valvename)
    return valve.get_property("drop")



def ping_ip(ip_address:str # IP address to ping
            )->bool :  # returns True if IP address is in use
    "Ping an IP address to see if it is in use"
    if platform.system().lower() == "windows":
        status = subprocess.call(
            ['ping', '-q', '-n', '1', '-W', '1', ip_address],
            stdout=subprocess.DEVNULL)
    else:
        status = subprocess.call(
            ['ping', '-q', '-c', '1', '-W', '1', ip_address],
            stdout=subprocess.DEVNULL)
        
    if status == 0:
        logger.debug(f"Ping: Found {ip_address}")
        return True
    else:
        logger.debug(f"Ping: cant find {ip_address}")
        return False


class Mqtt:
    "Class to control a gst valve via MQTT"
    def __init__(self, camera:str  # name of camera
                 , video:GstStream  # video object
                 , valve_name:str="myvalve"  # name of valve element
                 , addr:str="127.0.0.1"  # IP address of MQTT broker
                 ):
        self.cname = self.__class__.__name__
        self.camera = camera
        self.video = video
        self.valve_name = valve_name
        self.client = mqtt_client.Client(self.camera)
        self.msg = None

        if ping_ip(addr):
            # logger.info(f"Ping: Connecting to {addr}")
            self.client.connect(addr)
        else:
            # logger.info("Ping: Connecting to 127.0.0.1")
            self.client.connect("127.0.0.1")

        self.client.loop_start()
        
        self.connected = False
        self.client.on_message = self.on_mqtt_message
        self.client.on_connect = self.on_connect


    def on_mqtt_message(self, client:mqtt_client.Client # mqtt client
                        , userdata # user data
                        , message:mqtt_client.MQTTMessage # message
                        ):
        """Callback function for mqtt_client message
            Sets the valve state to True or False depending on the message payload"""
        self.msg = str(message.payload.decode("utf-8"))
        logger.info(f"{self.cname} Received message: {self.msg}" )
        if self.video is not None:
            try:
                if self.msg == self.camera:
                    self.video.set_valve_state(self.valve_name, False)
                else:
                    self.video.set_valve_state(self.valve_name, True)
            except Exception as e:
                logger.error(f"{self.cname}: Not able to set valve state: {e}")   # todo - log this error and fix it
    
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        """The callback for when the client receives a CONNACK response from the server."""
        logger.info(f"{self.cname} connected with result code {str(rc)}")
        self.client.subscribe("STREAM-CAMERA")
        self.connected = True
        
    def wait_connection(self, 
                             timeout=2  # timeout in seconds
                             )->bool:   # true if connected within timeout    
        """Wait for connection to be available"""
        elapsetime = 0
        while not self.connected:
            time.sleep(0.01)
            elapsetime += 0.01
            if elapsetime > timeout:
                logger.error(f"{self.cname}: Timeout waiting for connection")
                return False
            
        # logger.info(f"{self.cname}: connected")
        return True
        
    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info(f"{self.cname} Closed client")
        
    def __enter__(self):
        """with context manager"""
        return self  # This value is assigned to the variable after 'as' in the 'with' statement
    
    def __exit__(self, exc_type, exc_value, traceback):
        """with context manager"""
        self.close()
        # If an exception occurred, exc_type, exc_value, and traceback will be provided
        # Returning False (or None) will propagate the exception
        # Returning True will suppress it
        return False


