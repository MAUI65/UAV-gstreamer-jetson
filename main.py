""" Run this on the drone to start the cameras and the MAVCom server"""
import asyncio
from UAV_jetson.run_server import main
if __name__ == '__main__':
    print(__doc__)
    asyncio.run(main())
