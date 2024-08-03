# Installation

## Hardware Prerequisites

* A Raspberry Pi with Bluetooth
* [Waveshare 2.13inch Touch e-Paper HAT for Raspberry Pi](https://www.waveshare.com/2.13inch-touch-e-paper-hat.htm)

## Software Prerequisites

* `mopidy`
  * `mopidy-alsamixer`
  * `mopidy-local`
* `pipenv`

## Mopidy Config
As root, copy the Mopidy config included in the repo to Mopidy's system service config directory. Also enable the Mopidy service:

```sh
# cp ./mopidy.conf /etc/mopidy/mopidy.conf
# systemctl enable --now mopidy
```

## Running
Ensure the following features are enabled on your Raspberry Pi by using `raspi-config` or editing `/boot/firmware/config.txt` directly:

* I2C
* SPI

Enter the root of the repository and run the following:

```sh
$ pipenv sync
$ pipenv shell
$ python ./controller.py
```
