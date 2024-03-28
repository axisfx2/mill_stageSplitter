# Stage Splitter

* Description: Cinema 4D plugin that splits a stage object into takes and render settings
* Author: Ewan Davidson
* Email: ewan@axisfx.design
* Release Date: 28.03.2024
* Current Version: 1.3

## Installation

* Click the green 'Code' button
* Click 'Download ZIP'
* Extract the ZIP

## Useage

1. Make your source render setting and make sure its first in the list
2. Disable all shot specific lights and objects
3. Nest your shot specific light/objects inside separate nulls
4. Supported null names are: 'camera_name_LIGHTS', 'camera_name_BG' and 'camera_name_SCENE'
5. Select a Stage object at least 1 keyframe
6. Extensions > User Scripts > Run Script...
7. Run the stageSplitter.py script

## Changelog

### 1.3  |  28.03.2024

* Log created when script is ran - saved in Documents\Stage Splitter\Logs
* Takes are sorted alphabetically
* Limitting accepted shot specific nulls to certain keywords
* Prompting user if they want to look for shot specific nulls

### 1.2  |  28.03.2024

* Stage Splitter must be loaded with 'Run Script' now instead of being installed and ran like a plugin
* Lights and objects inside nulls that start with the name of the camera will be enabled in the take

### 1.1  |  28.03.2024

* Deleted standalone menu - scripts are now found in the 'Extensions' menu

### 1.0  |  28.03.2024

* Initial commit