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

