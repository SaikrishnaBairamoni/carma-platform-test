# Copyright (C) 2022 LEIDOS.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ament_index_python import get_package_share_directory
from launch.actions import Shutdown
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.substitutions import EnvironmentVariable
from carma_ros2_utils.launch.get_log_level import GetLogLevel
from carma_ros2_utils.launch.get_current_namespace import GetCurrentNamespace
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition

import os
import subprocess

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import GroupAction
from launch_ros.actions import set_remap



def generate_launch_description():

    """
    Launch V2X subsystem nodes.
    """

    env_log_levels = EnvironmentVariable('CARMA_ROS_LOGGING_CONFIG', default_value='{ "default_level" : "WARN" }')

    subsystem_controller_default_param_file = os.path.join(
        get_package_share_directory('subsystem_controllers'), 'config/v2x_controller_config.yaml')

    mobilitypath_publisher_param_file = os.path.join(
        get_package_share_directory('mobilitypath_publisher'), 'config/parameters.yaml')

    bsm_generator_param_file = os.path.join(
        get_package_share_directory('bsm_generator'), 'config/parameters.yaml')

    vehicle_characteristics_param_file = LaunchConfiguration('vehicle_characteristics_param_file')
    declare_vehicle_characteristics_param_file_arg = DeclareLaunchArgument(
        name = 'vehicle_characteristics_param_file',
        default_value = "/opt/carma/vehicle/calibration/identifiers/UniqueVehicleParams.yaml",
        description = "Path to file containing unique vehicle calibrations"
    )


    vehicle_config_param_file = LaunchConfiguration('vehicle_config_param_file')
    declare_vehicle_config_param_file_arg = DeclareLaunchArgument(
        name = 'vehicle_config_param_file',
        default_value = "/opt/carma/vehicle/config/VehicleConfigParams.yaml",
        description = "Path to file contain vehicle configuration parameters"
    )

    subsystem_controller_param_file = LaunchConfiguration('subsystem_controller_param_file')
    declare_subsystem_controller_param_file_arg = DeclareLaunchArgument(
        name = 'subsystem_controller_param_file',
        default_value = subsystem_controller_default_param_file,
        description = "Path to file containing override parameters for the subsystem controller"
    )

    # Declare enable_opening_tunnels
    enable_opening_tunnels = LaunchConfiguration('enable_opening_tunnels')
    declare_enable_opening_tunnels = DeclareLaunchArgument(
        name = 'enable_opening_tunnels',
        default_value= 'True',
        description='Flag to enable opening http tunnesl to CARMA Cloud'
    )

    carma_cloud_client_param_file = os.path.join(
        get_package_share_directory('carma_cloud_client'), 'config/parameters.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    declare_use_sim_time_arg = DeclareLaunchArgument(
        name = 'use_sim_time',
        default_value = "False",
        description = "True if simulation mode is on"
    )

    # Nodes
    carma_v2x_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_v2x_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[

            ComposableNode(
                package='mobilitypath_publisher',
                plugin='mobilitypath_publisher::MobilityPathPublication',
                name='mobilitypath_publisher_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('mobilitypath_publisher', env_log_levels) }
                ],
                remappings=[
                    ("plan_trajectory", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plan_trajectory" ] ),
                    ("guidance_state", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/state" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("mobility_path_msg", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_path" ] )
                ],
                parameters=[
                    mobilitypath_publisher_param_file,
                    vehicle_characteristics_param_file,
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='bsm_generator',
                plugin='bsm_generator::BSMGenerator',
                name='bsm_generator_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('bsm_generator', env_log_levels) }
                ],
                remappings=[
                    ("velocity_accel_cov", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/velocity_accel_cov" ] ),
                    ("ekf_twist", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                    ("imu_raw", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/imu_raw" ] ),
                    ("transmission_state", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/can/transmission_state" ] ),
                    ("brake_position", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/can/brake_position" ] ),
                    ("steering_wheel_angle", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/can/steering_wheel_angle" ] ),
                    ("gnss_fix_fused", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/gnss_fix_fused" ] ),
                    ("pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] )
                ],
                parameters=[
                    bsm_generator_param_file,
                    vehicle_characteristics_param_file,
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='cpp_message',
                plugin='cpp_message::Node',
                name='cpp_message_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cpp_message', env_log_levels) }
                ],
                remappings=[
                    ("inbound_binary_msg", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/comms/inbound_binary_msg" ] ),
                    ("outbound_binary_msg", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/comms/outbound_binary_msg" ] ),
                ],
                parameters=[
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='j2735_convertor',
                plugin='j2735_convertor::Node',
                name='j2735_convertor_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('j2735_convertor', env_log_levels) }
                ],
                remappings=[
                    ("outgoing_bsm", "bsm_outbound" )
                ],
                parameters=[
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='carma_cloud_client',
                plugin='carma_cloud_client::CarmaCloudClient',
                name='carma_cloud_client_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('carma_cloud_client', env_log_levels) }
                ],
                remappings=[
                    ("incoming_geofence_control", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_geofence_control" ] ),
                ],
                parameters = [
                    vehicle_config_param_file, carma_cloud_client_param_file
                ]

            ),
        ]
    )

    # subsystem_controller which orchestrates the lifecycle of this subsystem's components
    subsystem_controller = Node(
        package='subsystem_controllers',
        name='v2x_controller',
        executable='v2x_controller',
        parameters=[
            subsystem_controller_default_param_file,
            subsystem_controller_param_file,
            {"use_sim_time" : use_sim_time}], # Default file is loaded first followed by config file
        on_exit= Shutdown(), # Mark the subsystem controller as required
        arguments=['--ros-args', '--log-level', GetLogLevel('subsystem_controllers', env_log_levels)]
    )

    # Info needed for opening the tunnels
    # TODO: Investigate if this can be further cleaned up
    REMOTE_USER="ubuntu"
    REMOTE_ADDR="carma-cloud.com" # Dev instance is www.carma-cloud.com, prod instance is carma-cloud.com
    KEY_FILE="carma-cloud-1.pem" # Dev key is carma-cloud-test-1.pem, prod key is carma-cloud-1.pem
    HOST_PORT="33333" # This port is forwarded to remote host (carma-cloud)
    REMOTE_PORT="22222" # This port is forwarded to local host
    param_launch_path = os.path.join(
        get_package_share_directory('carma_cloud_client'), 'launch/scripts')

    script = param_launch_path + '/open_tunnels.sh'

    subprocess.check_call(['chmod','u+x', script])

    key_path =  "/opt/carma/vehicle/calibration/cloud_permission"

    keyfile = key_path + '/' + KEY_FILE

    subprocess.check_call(['sudo','chmod','400', keyfile])


    open_tunnels_action = ExecuteProcess(

        condition=IfCondition(enable_opening_tunnels),
        cmd = ['sudo',  script, '-u', REMOTE_USER, '-a', REMOTE_ADDR, '-k', keyfile, '-p', REMOTE_PORT,  '-r', HOST_PORT],
        output = 'screen'
    )


    return LaunchDescription([
        declare_vehicle_config_param_file_arg,
        declare_use_sim_time_arg,
        declare_vehicle_characteristics_param_file_arg,
        declare_subsystem_controller_param_file_arg,
        declare_enable_opening_tunnels,
        open_tunnels_action,
        carma_v2x_container,
        subsystem_controller
    ])
