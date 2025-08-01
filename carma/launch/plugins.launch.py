# Copyright (C) 2022-2023 LEIDOS.
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

import os

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import GroupAction
from launch_ros.actions import set_remap
from launch.actions import DeclareLaunchArgument

# Launch file for launching the nodes in the CARMA guidance stack

def generate_launch_description():

    route_file_folder = LaunchConfiguration('route_file_folder')
    vehicle_calibration_dir = LaunchConfiguration('vehicle_calibration_dir')
    vehicle_characteristics_param_file = LaunchConfiguration('vehicle_characteristics_param_file')
    enable_guidance_plugin_validator = LaunchConfiguration('enable_guidance_plugin_validator')
    strategic_plugins_to_validate = LaunchConfiguration('strategic_plugins_to_validate')
    tactical_plugins_to_validate = LaunchConfiguration('tactical_plugins_to_validate')
    control_plugins_to_validate = LaunchConfiguration('control_plugins_to_validate')

    vehicle_config_param_file = LaunchConfiguration('vehicle_config_param_file')

    inlanecruising_plugin_file_path = os.path.join(
        get_package_share_directory('inlanecruising_plugin'), 'config/parameters.yaml')

    route_following_plugin_file_path = os.path.join(
        get_package_share_directory('route_following_plugin'), 'config/parameters.yaml')

    stop_and_wait_plugin_param_file = os.path.join(
        get_package_share_directory('stop_and_wait_plugin'), 'config/parameters.yaml')

    light_controlled_intersection_tactical_plugin_param_file = os.path.join(
        get_package_share_directory('light_controlled_intersection_tactical_plugin'), 'config/parameters.yaml')

    cooperative_lanechange_param_file = os.path.join(
        get_package_share_directory('cooperative_lanechange'), 'config/parameters.yaml')

    platooning_strategic_ihp_param_file = os.path.join(
        get_package_share_directory('platooning_strategic_ihp'), 'config/parameters.yaml')

    sci_strategic_plugin_file_path = os.path.join(
        get_package_share_directory('sci_strategic_plugin'), 'config/parameters.yaml')

    lci_strategic_plugin_file_path = os.path.join(
        get_package_share_directory('lci_strategic_plugin'), 'config/parameters.yaml')

    stop_and_dwell_strategic_plugin_container_file_path = os.path.join(
        get_package_share_directory('stop_and_dwell_strategic_plugin'), 'config/parameters.yaml')

    yield_plugin_file_path = os.path.join(
        get_package_share_directory('yield_plugin'), 'config/parameters.yaml')

    platoon_tactical_ihp_param_file = os.path.join(
        get_package_share_directory('platooning_tactical_plugin'), 'config/parameters.yaml')

    approaching_emergency_vehicle_plugin_param_file = os.path.join(
        get_package_share_directory('approaching_emergency_vehicle_plugin'), 'config/parameters.yaml')

    stop_controlled_intersection_tactical_plugin_file_path = os.path.join(
        get_package_share_directory('stop_controlled_intersection_tactical_plugin'), 'config/parameters.yaml')

    trajectory_follower_wrapper_param_file = os.path.join(
        get_package_share_directory('trajectory_follower_wrapper'), 'config/parameters.yaml')

    env_log_levels = EnvironmentVariable('CARMA_ROS_LOGGING_CONFIG', default_value='{ "default_level" : "WARN" }')

    pure_pursuit_tuning_parameters = [vehicle_calibration_dir, "/pure_pursuit/calibration.yaml"]

    unique_vehicle_calibration_params = [vehicle_calibration_dir, "/identifiers/UniqueVehicleParams.yaml"]

    platooning_control_param_file = os.path.join(
        get_package_share_directory('platooning_control'), 'config/parameters.yaml')

    carma_inlanecruising_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_lainlanecruising_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='inlanecruising_plugin',
                plugin='inlanecruising_plugin::InLaneCruisingPluginNode',
                name='inlanecruising_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('inlanecruising_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                ],
                parameters=[
                    inlanecruising_plugin_file_path,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_route_following_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_route_following_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[

            ComposableNode(
                package='route_following_plugin',
                plugin='route_following_plugin::RouteFollowingPlugin',
                name='route_following_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('route_following_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("current_velocity", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                    ("maneuver_plan", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/final_maneuver_plan" ] ),
                ],
                parameters=[
                    route_following_plugin_file_path,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_approaching_emergency_vehicle_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_approaching_emergency_vehicle_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[

            ComposableNode(
                package='approaching_emergency_vehicle_plugin',
                plugin='approaching_emergency_vehicle_plugin::ApproachingEmergencyVehiclePlugin',
                name='approaching_emergency_vehicle_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('approaching_emergency_vehicle_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("state", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/state" ] ),
                    ("approaching_erv_status", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/approaching_erv_status" ] ),
                    ("hazard_light_status", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/hazard_light_status" ] ),
                    ("current_velocity", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                    ("incoming_bsm", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_bsm" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("route_state", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route_state" ] ),
                    ("outgoing_emergency_vehicle_response", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_emergency_vehicle_response" ] ),
                    ("incoming_emergency_vehicle_ack", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_emergency_vehicle_ack" ])
                ],
                parameters=[
                    approaching_emergency_vehicle_plugin_param_file,
                    vehicle_characteristics_param_file,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_stop_and_wait_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_stop_and_wait_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[

            ComposableNode(
                package='stop_and_wait_plugin',
                plugin='stop_and_wait_plugin::StopandWaitNode',
                name='stop_and_wait_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('stop_and_wait_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                ],
                parameters=[
                    stop_and_wait_plugin_param_file,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_sci_strategic_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_sci_strategic_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='sci_strategic_plugin',
                plugin='sci_strategic_plugin::SCIStrategicPlugin',
                name='sci_strategic_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('sci_strategic_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("maneuver_plan", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/final_maneuver_plan" ] ),
                    ("outgoing_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_operation" ] ),
                    ("incoming_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_operation" ] ),
                    ("bsm_outbound", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/bsm_outbound" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                ],
                parameters=[
                    sci_strategic_plugin_file_path,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_lci_strategic_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_lci_strategic_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='lci_strategic_plugin',
                plugin='lci_strategic_plugin::LCIStrategicPlugin',
                name='lci_strategic_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('lci_strategic_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("maneuver_plan", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/final_maneuver_plan" ] ),
                    ("outgoing_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_operation" ] ),
                    ("incoming_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_operation" ] ),
                    ("bsm_outbound", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/bsm_outbound" ] ),
                ],
                parameters=[
                    lci_strategic_plugin_file_path,
                    vehicle_config_param_file,
                    unique_vehicle_calibration_params
                ]
            ),
        ]
    )

    carma_stop_controlled_intersection_tactical_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_stop_controlled_intersection_tactical_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='stop_controlled_intersection_tactical_plugin',
                plugin='stop_controlled_intersection_tactical_plugin::StopControlledIntersectionTacticalPlugin',
                name='stop_controlled_intersection_tactical_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('stop_controlled_intersection_tactical_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] )
                ],
                parameters=[
                    stop_controlled_intersection_tactical_plugin_file_path,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_cooperative_lanechange_plugins_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_cooperative_lanechange_plugins_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='cooperative_lanechange',
                plugin='cooperative_lanechange::CooperativeLaneChangePlugin',
                name='cooperative_lanechange',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cooperative_lanechange', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("current_velocity", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                    ("cooperative_lane_change_status", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/cooperative_lane_change_status" ] ),
                    ("bsm_outbound", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/bsm_outbound" ] ),
                    ("outgoing_mobility_request", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_request" ] ),
                    ("incoming_mobility_response", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_response" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] )
                ],
                parameters=[
                    cooperative_lanechange_param_file,
                    vehicle_characteristics_param_file,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_yield_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_yield_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                    package='yield_plugin',
                    plugin='yield_plugin::YieldPluginNode',
                    name='yield_plugin',
                    extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('yield_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("external_object_predictions", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/external_object_predictions" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("outgoing_mobility_response", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_response" ] ),
                    ("incoming_mobility_request", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_request" ] ),
                    ("cooperative_lane_change_status", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/cooperative_lane_change_status" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference"]),
                    ("bsm_outbound", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/bsm_outbound" ] ),
                ],
                parameters=[
                    yield_plugin_file_path,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    carma_light_controlled_intersection_plugins_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_light_controlled_intersection_plugins_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='light_controlled_intersection_tactical_plugin',
                plugin='light_controlled_intersection_tactical_plugin::LightControlledIntersectionTransitPluginNode',
                name='light_controlled_intersection_tactical_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('light_controlled_intersection_tactical_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] )
                ],
                parameters=[
                    vehicle_config_param_file,
                    vehicle_characteristics_param_file,
                    light_controlled_intersection_tactical_plugin_param_file
                ]
            ),
        ]
    )

    carma_pure_pursuit_wrapper_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_pure_pursuit_wrapper_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                    package='pure_pursuit_wrapper',
                    plugin='pure_pursuit_wrapper::PurePursuitWrapperNode',
                    name='pure_pursuit_wrapper',
                    extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('pure_pursuit_wrapper', env_log_levels) }
                ],
                remappings = [
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("ctrl_raw", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/ctrl_raw" ] ),
                    ("pure_pursuit_wrapper/plan_trajectory", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugins/pure_pursuit/plan_trajectory" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("vehicle/twist", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                ],
                parameters=[
                    vehicle_characteristics_param_file, #vehicle_response_lag
                    vehicle_config_param_file,
                    pure_pursuit_tuning_parameters
                ]
            ),
        ]
    )

    trajectory_follower_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='trajectory_follower_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='trajectory_follower_nodes',
                plugin='autoware::motion::control::trajectory_follower_nodes::LatLonMuxer',
                name='latlon_muxer_node',
                extra_arguments=[
                    {'use_intra_process_comms': False},
                    {'--log-level' : GetLogLevel('latlon_muxer', env_log_levels) }
                ],
                remappings = [
                      ("input/lateral/control_cmd", "trajectory_follower/lateral/control_cmd"),
                      ("input/longitudinal/control_cmd", "trajectory_follower/longitudinal/control_cmd"),
                      ("output/control_cmd", "trajectory_follower/control_cmd")
                ],
                parameters=[
                    {'timeout_thr_sec':0.5}
                ]
            ),
            ComposableNode(
                package='trajectory_follower_nodes',
                plugin='autoware::motion::control::trajectory_follower_nodes::LateralController',
                name='lateral_controller_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('lateral_controller', env_log_levels) }
                ],
                remappings = [
                      ("output/lateral/control_cmd", "trajectory_follower/lateral/control_cmd"),
                      ("input/current_kinematic_state", "trajectory_follower/current_kinematic_state"),
                      ("input/reference_trajectory","trajectory_follower/reference_trajectory" )
                ],
                parameters = [
                    [vehicle_calibration_dir, "/trajectory_follower/lateral_controller_defaults.yaml"]
                ]
            ),
            ComposableNode(
                package='trajectory_follower_nodes',
                plugin='autoware::motion::control::trajectory_follower_nodes::LongitudinalController',
                name='longitudinal_controller_node',
                extra_arguments=[
                    {'use_intra_process_comms': False},
                    {'--log-level' : GetLogLevel('longitudinal_controller', env_log_levels) }
                ],
                remappings = [
                      ("output/longitudinal/control_cmd", "trajectory_follower/longitudinal/control_cmd"),
                      ("input/current_trajectory", "trajectory_follower/reference_trajectory"),
                      ("input/current_state", "trajectory_follower/current_kinematic_state")
                ],
                parameters = [
                    [vehicle_calibration_dir, "/trajectory_follower/longitudinal_controller_defaults.yaml"]
                ]
            )
        ]
    )
    carma_trajectory_follower_wrapper_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_trajectory_follower_wrapper_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                    package='trajectory_follower_wrapper',
                    plugin='trajectory_follower_wrapper::TrajectoryFollowerWrapperNode',
                    name='trajectory_follower_wrapper',
                    extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('trajectory_follower_wrapper', env_log_levels) }
                ],
                remappings = [
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("ctrl_raw", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/ctrl_raw" ] ),
                    ("trajectory_follower_wrapper/plan_trajectory", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugins/trajectory_follower_wrapper/plan_trajectory" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("vehicle/twist", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                ],
                parameters=[
                    vehicle_characteristics_param_file,
                    trajectory_follower_wrapper_param_file
                ]
            ),
        ]
    )

    platooning_strategic_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='platooning_strategic_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='platooning_strategic_ihp',
                plugin='platooning_strategic_ihp::Node',
                name='platooning_strategic_ihp_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('platooning_strategic_ihp', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("outgoing_mobility_response", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_response" ] ),
                    ("outgoing_mobility_request", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_request" ] ),
                    ("outgoing_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_operation" ] ),
                    ("incoming_mobility_request", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_request" ] ),
                    ("incoming_mobility_response", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_response" ] ),
                    ("incoming_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_operation" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("twist_raw", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/twist_raw" ] ),
                    ("platoon_info", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/platoon_info" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("current_velocity", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                ],
                parameters=[
                    platooning_strategic_ihp_param_file,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    platooning_tactical_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='platooning_tactical_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='platooning_tactical_plugin',
                plugin='platooning_tactical_plugin::Node',
                name='platooning_tactical_plugin_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('platooning_tactical_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                ],
                parameters=[ platoon_tactical_ihp_param_file, vehicle_config_param_file ]
            ),
        ]
    )

    platooning_control_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='platooning_control_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='platooning_control',
                plugin='platooning_control::PlatooningControlPlugin',
                name='platooning_control',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('platooning_control_plugin', env_log_levels) }
                ],
                remappings = [
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("ctrl_raw", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/ctrl_raw" ] ),
                    ("twist_raw", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/twist_raw" ] ),
                    ("platooning_control/plan_trajectory", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugins/platooning_control/plan_trajectory" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("vehicle/twist", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/vehicle/twist" ] ),
                ],
                parameters=[ platooning_control_param_file, vehicle_config_param_file, unique_vehicle_calibration_params ]
            )
        ]
    )

    carma_stop_and_dwell_strategic_plugin_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='carma_stop_and_dwell_strategic_plugin_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='stop_and_dwell_strategic_plugin',
                plugin='stop_and_dwell_strategic_plugin::StopAndDwellStrategicPlugin',
                name='stop_and_dwell_strategic_plugin',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('stop_and_dwell_strategic_plugin', env_log_levels) }
                ],
                remappings = [
                    ("semantic_map", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/semantic_map" ] ),
                    ("map_update", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/map_update" ] ),
                    ("roadway_objects", [ EnvironmentVariable('CARMA_ENV_NS', default_value=''), "/roadway_objects" ] ),
                    ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                    ("plugin_discovery", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/plugin_discovery" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("maneuver_plan", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/final_maneuver_plan" ] ),
                    ("state", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/state" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                ],
                parameters=[
                    stop_and_dwell_strategic_plugin_container_file_path,
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    intersection_transit_maneuvering_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='intersection_transit_maneuvering_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='intersection_transit_maneuvering',
                plugin='intersection_transit_maneuvering::IntersectionTransitManeuveringNode',
                name='intersection_transit_maneuvering',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('intersection_transit_maneuvering', env_log_levels) }
                ],
                remappings = [],
                parameters=[
                    vehicle_config_param_file
                ]
            ),
        ]
    )

    return LaunchDescription([
        carma_inlanecruising_plugin_container,
        carma_route_following_plugin_container,
        carma_approaching_emergency_vehicle_plugin_container,
        carma_stop_and_wait_plugin_container,
        carma_sci_strategic_plugin_container,
        carma_stop_and_dwell_strategic_plugin_container,
        carma_lci_strategic_plugin_container,
        carma_stop_controlled_intersection_tactical_plugin_container,
        carma_cooperative_lanechange_plugins_container,
        carma_yield_plugin_container,
        carma_light_controlled_intersection_plugins_container,
        carma_pure_pursuit_wrapper_container,
        carma_trajectory_follower_wrapper_container,
        #platooning_strategic_plugin_container,
        platooning_tactical_plugin_container,
        platooning_control_plugin_container,
        intersection_transit_maneuvering_container,
        trajectory_follower_container

    ])
