# UAV


### Installation
Download UAV-gstreamer-jetson from github and create a virtual environment
- Tested on python 3.8.10  ( make sure python3 = 3.8)

``` sh
mkdir repos
cd repos
git clone https://github.com/MAUI65/UAV-gstreamer-jetson
cd UAV
python3 -m venv 'venv'
source ./venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install -r requirements.txt
```
Install gstreamer

``` sh
sudo apt-get install libcairo2 libcairo2-dev libgirepository1.0-dev
sudo apt install libgirepository1.0-dev
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

4.  Install gstreamer-python

``` sh
pip install git+https://github.com/johnnewto/gstreamer-python.git
```

### Airsim ( optional for dev )

AirSim is a simulator for drones, cars and more, built on [Unreal
Engine](https://www.unrealengine.com/) (we now also have an experimental
[Unity](https://unity3d.com/) release). It is open-source, cross
platform, and supports software-in-the-loop simulation with popular
flight controllers such as PX4 & ArduPilot and hardware-in-loop with PX4
for physically and visually realistic simulations. It is developed as an
Unreal plugin that can simply be dropped into any Unreal environment.
Similarly, we have an experimental release for a Unity plugin.

Their goal was to develop AirSim as a platform for AI research to
experiment with deep learning, computer vision and reinforcement
learning algorithms for autonomous vehicles. For this purpose, AirSim
also exposes APIs to retrieve data and control vehicles in a platform
independent way. [![AirSim Drone Demo
Video](images/demo_video.png)](https://youtu.be/-WfTr1-OBGQ)

#### Install Airsim

For the binary releases of Airsim see
<https://github.com/microsoft/AirSim/releases/tag/v1.8.1> We recommend
the linux version as this repo is developed on linux.

## Developing with nbdev - Initial setup

if you want to develop with nbdev, you’ll need to install it first. For
a step-by-step guide to using nbdev [guide to using
nbdev](https://nbdev.fast.ai/tutorials/tutorial.html) You’ll need the
following software to develope using nbdev:

1.  Python venv
2.  A Python package manager: ie pip
3.  Jupyter Notebook

``` sh
pip install jupyter
```

4.  nbdev

``` sh
pip install nbdev
```

5.  Quarto

``` sh
nbdev_install_quarto
```

6.  Install Quarto JupyterLab extension

``` sh
pip install jupyterlab-quarto
```

7.  Install nbdev pre-commit hooks to catch and fix uncleaned and
    unexported notebooks

``` sh
pip install pre-commit
```

see [nbdev Pre-Commit
Hooks](https://nbdev.fast.ai/tutorials/pre_commit.html) for more details

#### Install msgpack-rpc-python with tornado 4.5.3

To run airsim in or beside jupyter notebook you need msgpack-rpc-python
to have an old version of tornado. The latest version of
msgpack-rpc-python is 0.4.1, which requires tornado 4.5.3. The latest
version of tornado is 6.1, which is not compatible with
msgpack-rpc-python.

The repo
<https://github.com/xaedes/msgpack-rpc-python/tree/with_tornado_453> is
a fork of msgpack-rpc-python which includes tornado 4.5.3 directly in
the repo.

Install msgpack-rpc-python with integrated tornado, pip install from
this repo
<https://github.com/johnnewto/msgpack-rpc-python/tree/with_tornado_453>

    pip uninstall msgpack-rpc-python
    pip install git+https://github.com/johnnewto/msgpack-rpc-python.git@with_tornado_453

### Preview Docs

Start the preview by entering this into your terminal:

``` sh
nbdev_preview
```

### Prepare your changes

Before commiting your changes to GitHub we recommend running
`nbdev_prepare` in the terminal,

which bundles the following commands:

- `nbdev_export`: Builds the `.py` modules from Jupyter notebooks
- `nbdev_test`: Tests your notebooks
- `nbdev_clean`: Cleans your notebooks to get rid of extreanous output
  for git
- `nbdev_readme`: Updates your repo’s `README.md` file from your index
  notebook.

### Update Static site docs

Generate the static docs by entering `nbdev_docs` into your terminal:

### Push to GitHub

You can now commit and push your changes to GitHub. As we mentioned
before, always remember to run `nbdev_prepare` before you commit to
ensure your modules are exported and your tests pass. You can use
`git status` to check which files have been generated or changed. Then:

``` sh
git add .
git commit -m 'Add `say_hello`; update index' # Update this text with your own message
git push
```

This will kick-off your GitHub Actions. Wait a minute or two for those
to complete, then check your updated repo and documentation.

## Other

### Set up autoreload

Since you’ll be often updating your modules from one notebook, and using
them in another, it’s helpful if your notebook automatically reads in
the new modules as soon as the Python file changes. To make this happen,
just add these lines to the top of your notebook:

``` sh
%load_ext autoreload
%autoreload 2
```
