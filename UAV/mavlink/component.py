from __future__ import annotations

__all__ = ['mavlink_command_to_string', 'Component']

import time, os, sys

from ..logging import logging, LogLevels
from ..utils.general import LeakyQueue

# os.environ['MAVLINK20'] == '1' should be placed in UAV.__init__.py
assert os.environ[
           'MAVLINK20'] == '1', "Set the environment variable before from pymavlink import mavutil  library is imported"

# logging.getLogger("uav").setLevel(logging.DEBUG)
# logging.root.setLevel(logging.INFO)
import threading
import queue
import typing as typ
from pathlib import Path
from inspect import currentframe, getframeinfo
from pymavlink import mavutil
from pymavlink.dialects.v20.ardupilotmega import MAVLink
import pymavlink.dialects.v20.ardupilotmega as mavlink

# from UAV.imports import *   # TODO why is this relative import on nbdev_export?
import asyncio


# from .mavcom import MAVCom, BaseComponent, get_linenumber, format_rcvd_msg


# from .mavcom import MAVCom, BaseComponent, get_linenumber, format_rcvd_msg

def get_linenumber():
    cf = currentframe()
    filename = Path(getframeinfo(cf).filename).name
    return f"{filename}:{cf.f_back.f_lineno}"

def format_rcvd_msg(msg, extra=''):
    """ Format a message for logging."""
    s = f"{str(msg)} ... {extra}"
    try:
        s = f"Rcvd {msg.get_srcSystem():3d}/{msg.get_srcComponent():3d} {s}"
    except:
        try:
            s = f"Rcvd {'???'}/{msg.get_srcComponent():3d} {s}"
        except:
            s = f"Rcvd {'???'}/{'???'} {s}"
    return s

def mavlink_command_to_string(command_id):
    try:
        return mavutil.mavlink.enums['MAV_CMD'][command_id].name
    except:
        return command_id

class Component:
    """Create a mavlink Component with an ID  for MAV_COMPONENT"""

    def __init__(self,
                 source_component,  # used for component indication
                 mav_type,  # used for heartbeat MAV_TYPE indication
                 loglevel:LogLevels=LogLevels.INFO,  # logging level
                 ):
        # todo change to def __init__(self:MavLinkBase, ....
        # self.mav_connection: MAVCom = None # this is a mavcom object that contains the mav_connection , set up in add_component
        # self.master = None
        # self.mav:MAVLink = None #
        self.mav_type = mav_type
        # self.source_system = None
        self.source_component = source_component


        self._log = logging.getLogger("uav.{}".format(self.__class__.__name__))
        self._log.setLevel(int(loglevel))

        self._loop = asyncio.get_event_loop()

        self.ping_num = 0
        self.max_pings = 4
        self.num_msgs_rcvd = 0
        self.num_cmds_sent = 0
        self.num_cmds_rcvd = 0
        self.num_acks_sent     = 0
        self.num_acks_rcvd = 0
        self.num_acks_drop = 0
        self.message_cnts: {} = {}  # received message counts, indexed by system and message type

        self.target_system = None
        self.target_component = None



        self.message_callback = None # callback function for when a command is received
        self._heartbeat_que = LeakyQueue(maxsize=10)
        self._ack_que = LeakyQueue(maxsize=10)
        self._message_que = LeakyQueue(maxsize=10)
        self._wait_message_que = LeakyQueue(maxsize=10)

        self._t_heartbeat = threading.Thread(target=self._thread_send_heartbeat, daemon=True)
        # self._t_heartbeat.start()

        self._t_command = threading.Thread(target=self._t_listen, daemon=True)
        # self._t_command.start()
        # self.log.info(
        #     f"Component Started {self.source_component = }, {self.mav_type = }, {self.source_system = }")

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<{}>".format(self)

    @property
    def log(self) -> logging.Logger:
        return self._log

    def set_mav_connection(self, mav_com: "MAVCom"):

        # def start_mav_connection(self, mav_connection: "MAVCom"):
        """Set the mav_connection for the component"""
        self.mav_com = mav_com
        self.master = mav_com.master
        self.mav:MAVLink = mav_com.master.mav
        self.source_system = mav_com.source_system
        print(f"set_mav_connection {self.__class__.__name__} {get_linenumber()} {self.mav_com = }")
        self._t_heartbeat.start()
        self._t_command.start()
        self.on_mav_connection()
        self.log.info(
            f"Component Started {self.source_component = }, {self.mav_type = }, {self.source_system = }")

    def on_mav_connection(self):
        self.log.debug("Called from Component.start_mav_connection(), override to add startup behaviour")

    def set_source_compenent(self):
        """Set the source component for the master.mav """
        if self.master is None:
            print(f"{self.__class__.__name__} {get_linenumber()} {self.master = }")
        assert self.master is not None, "self.master is None"
        self.master.mav.srcComponent = self.source_component

    def _set_message_callback(self, callback: typ.Callable):
        """Set the callback function for when a command is received."""
        self.message_callback = callback
    def send_ping(self, target_system: int, target_component: int, ping_num: int = None):
        """Send self.max_pings * ping messages to test if the server is alive."""

        if ping_num == 0:
            self.ping_num = 0
        if self.ping_num >= self.max_pings:
            return

        self.set_source_compenent()
        self.master.mav.ping_send(
            int(time.time() * 1000),  # Unix time 
            self.ping_num,  # Ping number
            target_system,  # Request ping of this system
            target_component,  # Request ping of this component
        )
        self.log.debug(f"Sent Ping #{self.ping_num} to:   {target_system:3d}, comp: {target_component:3d}")
        self.ping_num += 1

    def _thread_send_heartbeat(self):
        """Send a heartbeat message to indicate the server is alive."""
        self._t_heartbeat_stop = False

        self.log.debug(f"Starting heartbeat type: {self.mav_type} to all Systems and Components")
        while not self._t_heartbeat_stop:
            self.set_source_compenent()
            self.log.debug(f"Sent hrtbeat to All")
            # "Sent Ping #2 to:   111, comp: 100"
            self.master.mav.heartbeat_send(
                self.mav_type,  # type
                # mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,  # autopilot
                0,  # base_mode
                0,  # custom_mode
                mavutil.mavlink.MAV_STATE_ACTIVE,  # system_status
            )
            # print("Cam heartbeat_send")
            time.sleep(1)  # Send every second

    async def wait_heartbeat(self, remote_mav_type=None,  # type of remote system
                       target_system=None,  # target system
                       target_component=None,  # target component
                       timeout: int = 1,):  # seconds

        """Wait for a heartbeat from target_system and target_component."""
        # Todo is this correct ? Wait for a heartbeat, so we know the target system IDs (also it seems to need it to start receiving commands)

        self.log.debug(
                f"Waiting for heartbeat from {remote_mav_type} from {target_system = }:  {target_component = }")

        _time = 0
        _TIME_STEP = 0.1
        while _time < timeout:
            _time += _TIME_STEP
            try:
                # msg = self._heartbeat_que.get(timeout=timeout)
                msg = self._heartbeat_que.get_nowait()
                self.log.debug(format_rcvd_msg(msg, extra='self._heartbeat_que.get() '))
                # self.log.debug(f"Rcvd Heartbeat from src_sys: {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg} ")
                # check if the heartbeat is from the correct system and component
                if not msg.get_srcSystem() and not msg.get_srcComponent():
                    if msg.type is None or msg.type == remote_mav_type:
                        return (msg.get_srcSystem(), msg.get_srcComponent())
                else:
                    if msg.type == remote_mav_type:
                        return (msg.get_srcSystem(), msg.get_srcComponent())

            except queue.Empty:  # i.e time out
                await asyncio.sleep(_TIME_STEP)
                self.log.debug(f"HB queue Empty  {target_system = }:  {target_component = }")

        self.log.debug(f"No heartbeat received after {timeout} seconds")
        return None

    def send_ack(self, msg, ack_result: object = mavutil.mavlink.MAV_RESULT_ACCEPTED):
        """Send an ACK message to indicate a command was received."""
        self.set_source_compenent()
        try:
            self.master.mav.command_ack_send(
                msg.command,
                ack_result,  # or other MAV_RESULT enum
                # todo enabling these causes QGC not to show them
                int(0),  # progress
                int(0),  # result_param2
                msg.get_srcSystem(),  # target_system = msg.get_srcSystem(),  # target_system
                msg.get_srcComponent(),  # target_component = msg.get_srcComponent(),  # target_component
            )
            self.log.debug(f"Sent ACK for {mavlink_command_to_string(msg.command)}:{msg.command} to system: {msg.get_srcSystem()} comp: {msg.get_srcComponent()}")
            self.num_acks_sent += 1
        except Exception as e:
            self.log.warning(f"Error sending ACK {e}")


    async def wait_ack(self, target_system, target_component, command_id=None, timeout = 0.1) -> bool:
        """Wait for an ack from target_system and target_component."""
        self.log.debug(f"Waiting for ACK: {target_system}/{target_component} : {mavlink_command_to_string(command_id)}:{command_id}")
        _time = 0
        _TIME_STEP = 0.1
        while _time < timeout:
            _time += _TIME_STEP
            # print(f"{_time = }")
            try:
                msg = self._ack_que.get_nowait()
                # msg = self._ack_que.get(timeout=_TIME_STEP)
                # self.log.debug(f"ACK received from src_sys: {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg}")
                if (command_id == msg.command or command_id is None)  and msg.get_srcSystem() == target_system and msg.get_srcComponent() == target_component:
                    self.log.debug(f"Rcvd ACK: {msg.get_srcSystem()}/{msg.get_srcComponent()} {mavlink_command_to_string(msg.command)}:{msg.command} {msg.get_srcComponent()} {msg}")
                    return True
                else:
                    self.log.warning(f"**** ACK not handled {mavlink_command_to_string(msg.command)}:{msg.command} from : {msg.get_srcSystem()}/{msg.get_srcComponent()} {msg}")
                    # print(f"{command_id = } {msg.get_srcSystem() = }, {target_system = },  {msg.get_srcComponent() = }, {target_component = }")
                    self.log.warning(f"      command_id = {mavlink_command_to_string(msg.command)} {msg.get_srcSystem() = }, {target_system = },  {msg.get_srcComponent() = }, {target_component = }")

            except queue.Empty:  # i.e time out
                await asyncio.sleep(_TIME_STEP)
                pass

        self.log.debug("!!!!*** No ACK received")
        return False
    def count_message(self, msg):
        """ Count a message by adding it to the message_cnts dictionary. indexed by system and message type"""
        try:
            self.message_cnts[msg.get_srcSystem()][msg.get_type()] += 1
        except Exception as e:
            # print(f"!!!! new Message type {msg.get_type()} from system {msg.get_srcSystem()}")
            sys = msg.get_srcSystem()
            if sys not in self.message_cnts:
                self.message_cnts[sys] = {}
            self.message_cnts[sys][msg.get_type()] = 1

        return True

    def _t_listen(self, timeout: int = 1, ):  # seconds
        """Listen for MAVLink commands and trigger the camera when needed."""

        self._t_cmd_listen_stop = False
        # self.log.info(f"Component Listening for messages sent on the message_queue ...")
        while not self._t_cmd_listen_stop:

            try:
                msg = self._message_que.get(timeout=timeout)
                if msg.get_type() != 'HEARTBEAT':   # todo change to msg.get_msgId() == MAVLink.MAVLINK_MSG_ID_HEARTBEAT
                    # print (f"{MAVLink.MAVLINK_MSG_ID_HEARTBEAT = }")
                    self.log.debug(format_rcvd_msg(msg))
                self.num_msgs_rcvd += 1
            except queue.Empty:  # i.e time out
                time.sleep(0.01)
                continue

            self.count_message(msg)

            # print (f"{msg.get_type() = }")
            # if msg.get_type() == 'COMMAND_LONG':
            #     # print("Om command ")
            #     self._on_command_rcvd(msg)
            # elif msg.get_type() == 'COMMAND_INT':
            #     self._on_command_rcvd(msg)

            if msg.get_type() == 'COMMAND_ACK':
                # self.log.debug(f"Received ACK ")
                self._ack_que.put(msg, block=False)

            elif msg.get_type() == 'HEARTBEAT':
                # self.log.debug(f"Received HEARTBEAT ")
                self._heartbeat_que.put(msg, block=False)

            elif msg.get_type() == 'PING':
                # self.log.debug(f"Received PING {msg}")
                # ping_num = msg.time_usec
                ping_num = msg.seq
                # print(f"{ping_num = } {msg}")
                if ping_num < self.max_pings:
                    self.log.debug(f"Received PING {msg}")
                    self.send_ping(msg.get_srcSystem(), msg.get_srcComponent())

            else:
                self._on_message_rcvd(msg)

    def _on_message_rcvd(self, msg):
        # Callback for when a message is received.
        if self.message_callback is not None:
            ok = self.message_callback(msg)
        else:
            self.log.debug(f"Received command but no callback set {msg}")
            # print(f"!!! YAY!!! {get_linenumber()} {self} Received command {msg}")
            ok = False
        self.num_cmds_rcvd += 1
        if ok:
            self.send_ack(msg, mavutil.mavlink.MAV_RESULT_ACCEPTED)

    def set_target(self, target_system, target_component):
        """Set the target system and component for the gimbal"""
        self.target_system = target_system
        self.target_component = target_component

    async def send_command(self, target_system: int,  # target system
                     target_component: int,  # target component
                     command_id: int,  # mavutil.mavlink.MAV_CMD....
                     params: list,  # list of parameters
                     timeout = 0.5,  # seconds
                     ):
        self.log.debug(f"Sending: {target_system}/{target_component} : {mavlink_command_to_string(command_id)}:{(command_id)} ")
        self.set_source_compenent()
        self.master.mav.command_long_send(
            target_system,  # target_system   Todo Tried using self.master.target_system but it didn't work
            target_component,  # target_component Todo tried using self.master.target_component but it didn't work
            command_id,  # command id
            0,  # confirmation
            *params  # command parameters
        )
        self.num_cmds_sent += 1

        ret = await self.wait_ack(target_system, target_component, command_id=command_id, timeout=timeout)
        if ret:
        # if self.wait_ack(target_system, target_component, command_id=command_id, timeout=timeout):
            self.log.debug(
                f"Rcvd ACK: {target_system}/{target_component} {mavlink_command_to_string(command_id)}:{command_id}")
            self.num_acks_rcvd += 1
            return True
        else:
            self.log.warning(
                f"**No ACK: {target_system}/{target_component} {mavlink_command_to_string(command_id)}:{command_id}")
            self.num_acks_drop += 1
            return False

    def _test_command(self, target_system: int,  # target system
                      target_component: int,  # target component
                      camera_id: int = 1):  # camera id (0 for all cams)
        """
        Use MAV_CMD_DO_DIGICAM_CONTROL to trigger a camera 
        """
        self.set_source_compenent()
        mav_cmd = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL
        rst = self.send_command(target_system, target_component,
                                mav_cmd,
                                [camera_id,  # param1 (session)  or cam # (0 for all cams)
                                 1,  # param2 (trigger capture)
                                 0,  # param3 (zoom pos)
                                 0,  # param4 (zoom step)
                                 0,  # param5 (focus lock)
                                 0,  # param6 (shot ID)
                                 0,  # param7 (command ID)
                                 ])

        # self.log.debug(f"Sent message to:   {target_system:3d}, comp: {target_component:3d} command MAV_CMD_DO_DIGICAM_CONFIGURE")
        return rst

    def close(self):
        self._t_heartbeat_stop = True
        self._t_heartbeat.join()
        self.log.info(f"{self.__class__.__name__} closed")



