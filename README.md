art-packer
==========

Sprite sheets generator written in python

Features:
---------
* CLI and Python interface 
* Allow recursive folders walking
* Support of multiple sprite sheets of fixed size
* Configurable padding between sprites in the sheet
* Duplicate sprites detection based in fuzzy threshold
* Auto-crop sprites by transparent pixels
* Supports PNG, GIF, JPEG and BMP for input format
* Supports PNG for output format
* Supports JSON for output metadata format

Dependencies:
-------------

pip install pil

Installation:
-------------

This software works without installation, but if you want just run

sudo python setup.py install

or even 

pip install artpacker

Usage:
------

./bin/art-packer --input-path [path-to-sprites]