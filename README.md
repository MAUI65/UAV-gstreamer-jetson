# UAV jetson


### Installation
Download UAV-gstreamer-jetson from github and create a virtual environment
- Tested on python 3.8.10  ( make sure python3 >= 3.8)

``` sh
mkdir repos
cd repos
gt clone https://github.com/MAUI65/UAV-gstreamer-jetson.git
cd UAV-gstreamer-jetson
python3 -m venv 'venv'
source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Install gstreamer

``` sh
sudo apt-get install libcairo2 libcairo2-dev libgirepository1.0-dev
sudo apt install libgirepository1.0-dev
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

## To Do
1. args for running on lan, local or wifi or give ip address.
2. snapshot errors on more than 2 cams


With the above in place, you can now build your package by running `python -m build --wheel` from the folder where the pyproject.toml resides. (You may need to install the build package first: `pip install build`.) This should create a build/ folder as well as a dist/ folder (don’t forget to add these to your .gitignore, if they aren’t in there already!), in which you will find a wheel named something like example-0.1.0-py3-none-any.whl. That file contains your package, and this is all you need to distribute it. You can install this package anywhere by copying it to the relevant machine and running `pip install example-0.1.0-py3-none-any.whl`.

When developing you probably do not want to re-build and re-install the wheel every time you have made a change to the code, and for that you can use an editable install. This will install your package without packaging it into a file, but by referring to the source directory. You can do so by running `pip install -e .` from the directory where the pyproject.toml resides. Any changes you make to the source code will take immediate effect. But note that you may need to trigger your python to re-import the code, either by restarting your python session, or for example by using autoreload in a Jupyter notebook. Also note that any changes to the configuration of your package (i.e. changes to setup.cfg) will only take effect after re-installing it with `pip install -e .` .