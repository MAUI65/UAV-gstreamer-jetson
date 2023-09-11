# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/api/21_mavlink.component.ipynb.

# %% auto 0
__all__ = ['Component']

# %% ../../nbs/api/21_mavlink.component.ipynb 9
import time, os, sys

from ..logging import logging
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

# from UAV.imports import *   # TODO why is this relative import on nbdev_export?


# %% ../../nbs/api/21_mavlink.component.ipynb 10
from .mavcom import MAVCom, BaseComponent, get_linenumber, format_rcvd_msg

# %% ../../nbs/api/21_mavlink.component.ipynb 11
from .mavcom import MAVCom, BaseComponent, get_linenumber, format_rcvd_msg

# %% ../../nbs/api/21_mavlink.component.ipynb 12
class Component:
    """Create a mavlink Component with an ID  for MAV_COMPONENT"""

    def __init__(self, mav_connection,  # MavLinkBase connection
                 source_component,  # used for component indication
                 mav_type,  # used for heartbeat MAV_TYPE indication
                 debug):  # logging level
        # todo change to def __init__(self:MavLinkBase, ....
        self.mav_connection: MAVCom = mav_connection
        self.master = mav_connection.master
        self.mav:MAVLink = self.master.mav
        self.mav_type = mav_type
        self.source_system = self.mav_connection.source_system
        self.source_component = source_component


        self._log = logging.getLogger("uav.{}".format(self.__class__.__name__))
        self._log.setLevel(logging.DEBUG if debug else logging.INFO)

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

        self._t_heartbeat = threading.Thread(target=self.send_heartbeat, daemon=True)
        self._t_heartbeat.start()

        self._t_command = threading.Thread(target=self.listen, daemon=True)
        self._t_command.start()
        self.log.info(
            f"Component Started {self.source_component = }, {self.mav_type = }, {self.source_system = }")

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<{}>".format(self)

    @property
    def log(self) -> logging.Logger:
        return self._log

    def set_source_compenent(self):
        """Set the source component for the master.mav """
        self.master.mav.srcComponent = self.source_component

    def set_message_callback(self, callback: typ.Callable):
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

    def send_heartbeat(self):
        """Send a heartbeat message to indicate the server is alive."""
        self._t_heartbeat_stop = False

        # self.log.info(f"Starting heartbeat type: {self.mav_type} to all Systems and Components")
        while not self._t_heartbeat_stop:
            self.set_source_compenent()
            # self.log.debug(f"Sent hrtbeat to All")
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

    def wait_heartbeat(self, remote_mav_type=None,  # type of remote system
                       target_system=None,  # target system
                       target_component=None,  # target component
                       timeout: int = 1,  # seconds
                       tries: int = 3) -> bool:  # number of tries
        """Wait for a heartbeat from target_system and target_component."""
        # Todo is this correct ? Wait for a heartbeat, so we know the target system IDs (also it seems to need it to start receiving commands)
        if remote_mav_type is None:
            self.log.debug(f"Waiting for heartbeat from {target_system = }:  {target_component = }")
        else:
            self.log.debug(
                f"Waiting for heartbeat from {remote_mav_type} from {target_system = }:  {target_component = }")
        count = 0
        while count < tries:
            try:
                msg = self._heartbeat_que.get(timeout=timeout)
                self.log.debug(format_rcvd_msg(msg, extra='self._heartbeat_que.get() '))
                # self.log.debug(f"Rcvd Heartbeat from src_sys: {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg} ")
                # check if the heartbeat is from the correct system and component
                if msg.type == remote_mav_type and msg.get_srcSystem() == target_system and msg.get_srcComponent() == target_component:
                    return True
                elif msg.get_srcSystem() == target_system and msg.get_srcComponent() == target_component:
                    return True
            except queue.Empty:  # i.e time out
                count += 1

        self.log.debug(f"No heartbeat received after {tries} tries")
        return False

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
            self.log.debug(f"Sent ACK for command: {msg.command} to system: {msg.get_srcSystem()} comp: {msg.get_srcComponent()}")
            self.num_acks_sent += 1
        except Exception as e:
            self.log.warning(f"Error sending ACK {e}")

        # self.master.mav.command_ack_send(
        #     msg.command,
        #     ack_result,  # or other MAV_RESULT enum
        #     # todo enabling these causes QGC not to show them
        #     int(0),  # progress
        #     int(0),  # result_param2
        #     msg.get_srcSystem(),  # target_system = msg.get_srcSystem(),  # target_system
        #     msg.get_srcComponent(),  # target_component = msg.get_srcComponent(),  # target_component
        # )
        # self.log.debug(f"Sent ACK for command: {msg.command} to system: {msg.get_srcSystem()} comp: {msg.get_srcComponent()}")
        # self.num_acks_sent += 1

    def _wait_ack(self, target_system, target_component, command_id=None, timeout = 0.1) -> bool:
        """Wait for an ack from target_system and target_component."""
        self.log.debug(f"Waiting for ACK for command: {command_id} from system: {target_system} comp: {target_component}")

        try:
            msg = self._ack_que.get(timeout=timeout)
            # self.log.debug(f"ACK received from src_sys: {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg}")
            if (command_id == msg.command or command_id is None)  and msg.get_srcSystem() == target_system and msg.get_srcComponent() == target_component:
                self.log.debug(f"*** ACK received for cmd {command_id} from src_comp: {msg.get_srcComponent()} {msg}")
                return True
            else:
                self.log.debug(f"*** ACK not handled {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg}")
                self.log.debug(f"{command_id = } {msg.get_srcSystem() = }, {target_system = },  {msg.get_srcComponent() = }, {target_component = }")
        except queue.Empty:  # i.e time out
            pass
        self.log.debug("*** No ACK received")
        return False

    def wait_ack(self, target_system, target_component, command_id=None, timeout = 0.1) -> bool:
        """Wait for an ack from target_system and target_component."""
        self.log.debug(f"Waiting for ACK for command: {command_id} from system: {target_system} comp: {target_component}")
        _time = 0
        _TIME_STEP = 0.1
        while _time < timeout:
            _time += _TIME_STEP
            # print(f"{_time = }")
            try:
                msg = self._ack_que.get(timeout=_TIME_STEP)
                # self.log.debug(f"ACK received from src_sys: {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg}")
                if (command_id == msg.command or command_id is None)  and msg.get_srcSystem() == target_system and msg.get_srcComponent() == target_component:
                    self.log.debug(f"*** ACK received for cmd {command_id} from src_comp: {msg.get_srcComponent()} {msg}")
                    return True
                else:
                    self.log.debug(f"*** ACK not handled {msg.get_srcSystem()}, src_comp: {msg.get_srcComponent()} {msg}")
                    print(f"{command_id = } {msg.get_srcSystem() = }, {target_system = },  {msg.get_srcComponent() = }, {target_component = }")
                    self.log.debug(f"{command_id = } {msg.get_srcSystem() = }, {target_system = },  {msg.get_srcComponent() = }, {target_component = }")

            except queue.Empty:  # i.e time out
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

    def listen(self, timeout: int = 1, ):  # seconds
        """Listen for MAVLink commands and trigger the camera when needed."""

        self._t_cmd_listen_stop = False
        # self.log.info(f"Component Listening for messages sent on the message_queue ...")
        while not self._t_cmd_listen_stop:

            try:
                msg = self._message_que.get(timeout=timeout)
                if msg.get_type() != 'HEARTBEAT':
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
                self.log.debug(f"Received ACK ")
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

    def send_command(self, target_system: int,  # target system
                     target_component: int,  # target component
                     command_id: int,  # mavutil.mavlink.MAV_CMD....
                     params: list,  # list of parameters
                     timeout = 0.5,  # seconds
                     ):
        self.log.debug(f"Sending command: {command_id} to system: {target_system} comp: {target_component}")
        self.set_source_compenent()
        self.master.mav.command_long_send(
            target_system,  # target_system   Todo Tried using self.master.target_system but it didn't work
            target_component,  # target_component Todo tried using self.master.target_component but it didn't work
            command_id,  # command id
            0,  # confirmation
            *params  # command parameters
        )
        self.num_cmds_sent += 1

        if self.wait_ack(target_system, target_component, command_id=command_id, timeout=timeout):
            self.log.debug(
                f"ACK received for command: {command_id} from system: {target_system} comp: {target_component}")
            self.num_acks_rcvd += 1
            return True
        else:
            self.log.debug(
                f"No ACK received for command: {command_id} from system: {target_system} comp: {target_component}")
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



