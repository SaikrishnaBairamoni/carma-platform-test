#!/bin/bash

#  Copyright (C) 2018-2021 LEIDOS.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file except in compliance with the License. You may obtain a copy of
#  the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations under
#  the License.


# Script for running carma via Docker, assumes image carma is already built

CONFIG_FOLDER=$(pwd)/$1
docker run \
    --rm \
    --net=host \
    --name carma \
    -v $CONFIG_FOLDER/HostVehicleParams.yaml:/opt/carma/params/HostVehicleParams.yaml \
    -v $CONFIG_FOLDER/carma.urdf:/opt/carma/urdf/carma.urdf \
    -v $CONFIG_FOLDER/carma_src.launch.py:/opt/carma/launch/carma_src.launch.py \
    -v $CONFIG_FOLDER/drivers.launch.py:/opt/carma/launch/drivers.launch.py \
    -v $CONFIG_FOLDER/carma.config.js:/var/www/html/scripts/carma.config.js \
    -itd carma
