# Path utils

## About
The path utils python module is a package focusing on dealing with folder lookup
and image path manipulation.

## Features
- os_path
    - walk2 -> advanced os.walk adding level of depth and excludes parameter
    - scan_folder -> builds on top of walk2, scans files based on a given regex
- imagepath.Image -> image path value manipulations
    - get/set base image name
    - get/set image frame incl. hash, frame digit padding
    - get/set version in file and folder
    - get all image values

## Licensing
Apache License, Version 2.0

## Authors
Wilfried Pollan - Maintainer

## Versioning
See https://semver.org

0.1.0 - First release - basic module
