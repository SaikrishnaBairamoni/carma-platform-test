
# Copyright (C) 2024 LEIDOS.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

cmake_minimum_required(VERSION 3.8)
project(basic_autonomy)

# Declare carma package and check ROS version
find_package(carma_cmake_common REQUIRED)
carma_check_ros_version(2)
carma_package()

# Use C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
endif()

## Find dependencies using ament auto
find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()

# Name build targets
set(node_lib basic_autonomy_lib)

# Includes
include_directories(
  include
)

# Build
ament_auto_add_library(${node_lib} SHARED
        src/basic_autonomy.cpp
        src/helper_functions.cpp
        src/log/log.cpp
        src/smoothing/BSpline.cpp
        src/smoothing/filters.cpp
)

target_link_libraries(
        ${node_lib}
)


# Testing
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies() # This populates the ${${PROJECT_NAME}_FOUND_TEST_DEPENDS} variable

  ament_add_gtest(test_basic_autonomy test/test_waypoint_generation.cpp)

  ament_target_dependencies(test_basic_autonomy ${${PROJECT_NAME}_FOUND_TEST_DEPENDS})

  target_link_libraries(test_basic_autonomy ${node_lib})

endif()

# Install
ament_auto_package(
        INSTALL_TO_SHARE resource
)
