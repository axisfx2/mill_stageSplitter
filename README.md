# Stage Splitter

* Description: Cinema 4D plugin that splits a stage object into takes and render settings
* Author: Ewan Davidson
* Email: ewan@axisfx.design
* Release Date: 28.03.2024
* Current Version: 1.2

## Installation

* Click the green 'Code' button
* Click 'Download ZIP'
* Extract the ZIP

## Useage

1. Disable all shot specific lights and objects
2. Nest your shot specific light/objects inside separate nulls
3. Prefix the camera's name to the name of your null IE 'camera_name_LIGHTS', 'camera_name_BG'. Make sure you include the underscore after the cameras name. The cameras name is case sensitive.
4. Select a Stage object at least 1 keyframe
5. Extensions > User Scripts > Run Script...
6. Run the stageSplitter.py script

## Changelog

### 1.2  |  28.03.2024

* Stage Splitter must be loaded with 'Run Script' now instead of being installed and ran like a plugin
* Lights and objects inside nulls that start with the name of the camera will be enabled in the take

### 1.1  |  28.03.2024

* Deleted standalone menu - scripts are now found in the 'Extensions' menu

### 1.0  |  28.03.2024

* Initial commit