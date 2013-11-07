#!/bin/bash

mkdir molmod
cp -r "$RECIPE_DIR"/../../ molmod
cd molmod
$PYTHON setup.py install

# Add more build steps here, if they are necessary.

# See
# https://github.com/ContinuumIO/conda/blob/master/conda/builder/README.txt
# for a list of environment variables that are set during the build process.

