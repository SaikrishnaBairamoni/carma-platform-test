# Copyright (C) 2021-2022 LEIDOS.
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
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression
from pathlib import PurePath
import os


def generate_launch_description():
    """
    Launch perception nodes.
    """
    vehicle_calibration_dir = LaunchConfiguration('vehicle_calibration_dir')

    vehicle_config_param_file = LaunchConfiguration('vehicle_config_param_file')
    declare_vehicle_config_param_file_arg = DeclareLaunchArgument(
        name = 'vehicle_config_param_file',
        default_value = "/opt/carma/vehicle/config/VehicleConfigParams.yaml",
        description = "Path to file contain vehicle configuration parameters"
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    declare_use_sim_time_arg = DeclareLaunchArgument(
        name = 'use_sim_time',
        default_value = "False",
        description = "True if simulation mode is on"
    )

    vehicle_characteristics_param_file = LaunchConfiguration('vehicle_characteristics_param_file')
    declare_vehicle_characteristics_param_file_arg = DeclareLaunchArgument(
        name = 'vehicle_characteristics_param_file',
        default_value = "/opt/carma/vehicle/calibration/identifiers/UniqueVehicleParams.yaml",
        description = "Path to file containing unique vehicle calibrations"
    )

    vector_map_file = LaunchConfiguration('vector_map_file')
    declare_vector_map_file = DeclareLaunchArgument(name='vector_map_file', default_value = 'vector_map.osm', description = "Path to the map osm file if using the noupdate load type")

    # When enabled, the vehicle fuses incoming SDSM with its own sensor data to create a more accurate representation of the environment
    # When turned off, topics get remapped to solely rely on its own sensor data
    is_cp_mot_enabled = LaunchConfiguration('is_cp_mot_enabled')
    declare_is_cp_mot_enabled = DeclareLaunchArgument(
        name='is_cp_mot_enabled',
        default_value = 'False',
        description = 'True if user wants Cooperative Perception capability using Multiple Object Tracking to be enabled'
    )

    # When enabled, the vehicle has lidar detected objects in its external objects list
    # TODO: Currently the stack is not shutting down automatically https://usdot-carma.atlassian.net.mcas-gov.us/browse/CAR-6109
    is_autoware_lidar_obj_detection_enabled = LaunchConfiguration('is_autoware_lidar_obj_detection_enabled')
    declare_is_autoware_lidar_obj_detection_enabled = DeclareLaunchArgument(
        name='is_autoware_lidar_obj_detection_enabled',
        default_value = 'False',
        description = 'True if user wants Autoware Lidar Object Detection to be enabled'
    )

    autoware_auto_launch_pkg_prefix = get_package_share_directory(
        'autoware_auto_launch')

    euclidean_cluster_param_file = os.path.join(
        autoware_auto_launch_pkg_prefix, 'param/component_style/euclidean_cluster.param.yaml')

    ray_ground_classifier_param_file = os.path.join(
        autoware_auto_launch_pkg_prefix, 'param/component_style/ray_ground_classifier.param.yaml')

    tracking_nodes_param_file = os.path.join(
        autoware_auto_launch_pkg_prefix, 'param/component_style/tracking_nodes.param.yaml')

    object_detection_tracking_param_file = os.path.join(
        get_package_share_directory('object_detection_tracking'), 'config/parameters.yaml')

    subsystem_controller_default_param_file = os.path.join(
        get_package_share_directory('subsystem_controllers'), 'config/environment_perception_controller_config.yaml')

    subsystem_controller_param_file = LaunchConfiguration('subsystem_controller_param_file')
    declare_subsystem_controller_param_file_arg = DeclareLaunchArgument(
        name = 'subsystem_controller_param_file',
        default_value = subsystem_controller_default_param_file,
        description = "Path to file containing override parameters for the subsystem controller"
    )

    frame_transformer_param_file = os.path.join(
        get_package_share_directory('frame_transformer'), 'config/parameters.yaml')

    object_visualizer_param_file = os.path.join(
        get_package_share_directory('object_visualizer'), 'config/parameters.yaml')

    points_map_filter_param_file = os.path.join(
        get_package_share_directory('points_map_filter'), 'config/parameters.yaml')

    motion_computation_param_file = os.path.join(
        get_package_share_directory('motion_computation'), 'config/parameters.yaml')

    env_log_levels = EnvironmentVariable('CARMA_ROS_LOGGING_CONFIG', default_value='{ "default_level" : "WARN" }')

    carma_wm_ctrl_param_file = os.path.join(
        get_package_share_directory('carma_wm_ctrl'), 'config/parameters.yaml')

    cp_multiple_object_tracker_node_file = str(
        PurePath(get_package_share_directory("carma_cooperative_perception"),
                 "config/cp_multiple_object_tracker_node.yaml"))
    cp_host_vehicle_filter_node_file = str(
        PurePath(get_package_share_directory("carma_cooperative_perception"),
                 "config/cp_host_vehicle_filter_node.yaml"))
    cp_sdsm_to_detection_list_node_file = str(
        PurePath(get_package_share_directory("carma_cooperative_perception"),
                 "config/cp_sdsm_to_detection_list_node.yaml"))
    # lidar_perception_container contains all nodes for lidar based object perception
    # a failure in any one node in the chain would invalidate the rest of it, so they can all be
    # placed in the same container without reducing fault tolerance
    # a lifecycle wrapper container is used to ensure autoware.auto nodes adhere to the subsystem_controller's signals
    # TODO: Currently, the container is shutting down on its own https://usdot-carma.atlassian.net.mcas-gov.us/browse/CAR-6109
    lidar_perception_container = ComposableNodeContainer(
        condition=IfCondition(is_autoware_lidar_obj_detection_enabled),
        package='carma_ros2_utils', # rclcpp_components
        name='perception_points_filter_container',
        executable='lifecycle_component_wrapper_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='frame_transformer',
                plugin='frame_transformer::Node',
                name='lidar_to_map_frame_transformer',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('frame_transformer', env_log_levels) },
                    {'is_lifecycle_node': True} # Flag to allow lifecycle node loading in lifecycle wrapper
                ],
                remappings=[
                    ("input", [ EnvironmentVariable('CARMA_INTR_NS', default_value=''), "/lidar/points_raw" ] ),
                    ("output", "points_in_map"),
                    ("change_state", "disabled_change_state"), # Disable lifecycle topics since this is a lifecycle wrapper container
                    ("get_state", "disabled_get_state")        # Disable lifecycle topics since this is a lifecycle wrapper container
                ],
                parameters=[
                    { "target_frame" : "map"},
                    { "message_type" : "sensor_msgs/PointCloud2"},
                    { "queue_size" : 1},
                    { "timeout" : 50 },
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='points_map_filter',
                plugin='points_map_filter::Node',
                name='points_map_filter',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('points_map_filter', env_log_levels) },
                    {'is_lifecycle_node': True} # Flag to allow lifecycle node loading in lifecycle wrapper
                ],
                remappings=[
                    ("points_raw", "points_in_map" ),
                    ("filtered_points", "map_filtered_points"),
                    ("lanelet2_map", "semantic_map"),
                    ("change_state", "disabled_change_state"), # Disable lifecycle topics since this is a lifecycle wrapper container
                    ("get_state", "disabled_get_state")        # Disable lifecycle topics since this is a lifecycle wrapper container
                ],
                parameters=[ points_map_filter_param_file, vehicle_config_param_file ]
            ),
            ComposableNode(
                package='frame_transformer',
                plugin='frame_transformer::Node',
                name='lidar_frame_transformer',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('frame_transformer', env_log_levels) },
                    {'is_lifecycle_node': True} # Flag to allow lifecycle node loading in lifecycle wrapper
                ],
                remappings=[
                    ("input", "map_filtered_points" ),
                    ("output", "points_in_base_link"),
                    ("change_state", "disabled_change_state"), # Disable lifecycle topics since this is a lifecycle wrapper container
                    ("get_state", "disabled_get_state")        # Disable lifecycle topics since this is a lifecycle wrapper container
                ],
                parameters=[ frame_transformer_param_file, vehicle_config_param_file ]
            ),
            ComposableNode(
                package='ray_ground_classifier_nodes',
                name='ray_ground_filter',
                plugin='autoware::perception::filters::ray_ground_classifier_nodes::RayGroundClassifierCloudNode',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('ray_ground_classifier_nodes', env_log_levels) }
                ],
                remappings=[
                    ("points_in", "points_in_base_link"),
                    ("points_nonground", "points_no_ground")
                ],
                parameters=[ ray_ground_classifier_param_file, vehicle_config_param_file]
            ),
            ComposableNode(
                package='euclidean_cluster_nodes',
                name='euclidean_cluster',
                plugin='autoware::perception::segmentation::euclidean_cluster_nodes::EuclideanClusterNode',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('euclidean_cluster_nodes', env_log_levels) }
                ],
                remappings=[
                    ("points_in", "points_no_ground")
                ],
                parameters=[ euclidean_cluster_param_file, vehicle_config_param_file]
            ),
            ComposableNode(
                package='object_detection_tracking',
                plugin='bounding_box_to_detected_object::Node',
                name='bounding_box_converter',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('object_detection_tracking', env_log_levels) },
                    {'is_lifecycle_node': True} # Flag to allow lifecycle node loading in lifecycle wrapper
                ],
                remappings=[
                    ("bounding_boxes", "lidar_bounding_boxes"),
                    ("lidar_detected_objects", "detected_objects"),
                ],
                parameters=[vehicle_config_param_file]
            ),
            ComposableNode(
                    package='tracking_nodes',
                    plugin='autoware::tracking_nodes::MultiObjectTrackerNode',
                    name='tracking_nodes_node',
                    extra_arguments=[
                        {'use_intra_process_comms': True},
                        {'--log-level' : GetLogLevel('tracking_nodes', env_log_levels) }
                    ],
                    remappings=[
                        ("ego_state", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose_with_covariance" ] ),
                        # TODO note classified_rois1 is the default single camera input topic
                        # TODO when camera detection is added, we will wan to separate this node into a different component to preserve fault tolerance
                    ],
                    parameters=[ tracking_nodes_param_file, vehicle_config_param_file]
            )
        ]
    )


    # carma_external_objects_container contains nodes for object detection and tracking
    # since these nodes can use different object inputs they are a separate container from the lidar_perception_container
    # to preserve fault tolerance
    carma_external_objects_container = ComposableNodeContainer(
        package='carma_ros2_utils',
        name='external_objects_container',
        executable='carma_component_container_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='carma_wm_ctrl',
                plugin='carma_wm_ctrl::WMBroadcasterNode',
                name='carma_wm_broadcaster',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('carma_wm_ctrl', env_log_levels) }
                ],
                remappings=[
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("geofence", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_geofence_control" ] ),
                    ("incoming_map", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_map" ] ),
                    ("current_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] ),
                    ("outgoing_geofence_ack", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_mobility_operation" ] ),
                    ("outgoing_geofence_request", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_geofence_request" ] )
                ],
                parameters=[ carma_wm_ctrl_param_file, vehicle_config_param_file, vehicle_characteristics_param_file ]
            ),
            ComposableNode(
                    package='object_detection_tracking',
                    plugin='object::ObjectDetectionTrackingNode',
                    name='external_object',
                    extra_arguments=[
                        {'use_intra_process_comms': True},
                        {'--log-level' : GetLogLevel('object_detection_tracking', env_log_levels) }
                    ],
                    remappings=[
                        ("detected_objects", "tracked_objects"),
                    ],
                    parameters=[ object_detection_tracking_param_file, vehicle_config_param_file]
            ),
            ComposableNode(
                    package='object_visualizer',
                    plugin='object_visualizer::Node',
                    name='object_visualizer_node',
                    extra_arguments=[
                        {'use_intra_process_comms': True},
                        {'--log-level' : GetLogLevel('object_visualizer', env_log_levels) }
                    ],
                    remappings=[
                        ("external_objects", "external_object_predictions"),
                        ("external_objects_viz", "fused_external_objects_viz")
                    ],
                    parameters=[object_visualizer_param_file, vehicle_config_param_file,
                                {'pedestrian_icon_path': ['file:///', vehicle_calibration_dir, '/visualization_meshes/pedestrian.stl']}
                                ]
            ),
            ComposableNode(
                package='motion_computation',
                plugin='motion_computation::MotionComputationNode',
                name='motion_computation_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('motion_computation', env_log_levels) }
                ],
                remappings=[
                    ("incoming_mobility_path", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_path" ] ),
                    ("incoming_psm", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_psm" ] ),
                    ("incoming_bsm", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_bsm" ] ),
                    ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    # if CP is enabled, use fused objects to predict movements, otherwise use own sensor's objects
                    ("external_objects", PythonExpression(['"fused_external_objects" if "', is_cp_mot_enabled, '" == "True" else "external_objects"'])),
                ],
                parameters=[
                    motion_computation_param_file, vehicle_config_param_file
                ]
            ),
            ComposableNode( #CARMA Motion Prediction Visualizer Node
                    package='motion_prediction_visualizer',
                    plugin='motion_prediction_visualizer::Node',
                    name='motion_prediction_visualizer',
                    extra_arguments=[
                        {'use_intra_process_comms': True},
                        {'--log-level' : GetLogLevel('motion_prediction_visualizer', env_log_levels) }
                    ],
                    remappings=[
                        ("external_objects", "external_object_predictions" ),
                    ],
                    parameters=[ vehicle_config_param_file ]
            ),
            ComposableNode(
                    package='traffic_incident_parser',
                    plugin='traffic_incident_parser::TrafficIncidentParserNode',
                    name='traffic_incident_parser_node',
                    extra_arguments=[
                        {'use_intra_process_comms': True},
                        {'--log-level' : GetLogLevel('traffic_incident_parser', env_log_levels) }
                    ],
                    remappings=[
                        ("georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                        ("geofence", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_geofence_control" ] ),
                        ("incoming_mobility_operation", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_mobility_operation" ] ),
                        ("incoming_spat", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_spat" ] ),
                        ("route", [ EnvironmentVariable('CARMA_GUIDE_NS', default_value=''), "/route" ] )
                    ],
                    parameters = [
                        vehicle_config_param_file
                    ]

            ),
        ]
    )

    # Vector map loader
    lanelet2_map_loader_container = ComposableNodeContainer(
        package='carma_ros2_utils', # rclcpp_components
        name='lanelet2_map_loader_container',
        executable='lifecycle_component_wrapper_mt',
        namespace=GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='map_file_ros2',
                plugin='lanelet2_map_loader::Lanelet2MapLoader',
                name='lanelet2_map_loader',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('lanelet2_map_loader', env_log_levels) },
                    {'is_lifecycle_node': True} # Flag to allow lifecycle node loading in lifecycle wrapper
                ],
                remappings=[
                    ("lanelet_map_bin", "base_map"),
                    ("change_state", "disabled_change_state"), # Disable lifecycle topics since this is a lifecycle wrapper container
                    ("get_state", "disabled_get_state")        # Disable lifecycle topics since this is a lifecycle wrapper container
                ],
                parameters=[
                    { "lanelet2_filename" : vector_map_file},
                    vehicle_config_param_file
                ]
            )
        ]
    )

    # Vector map visualization
    lanelet2_map_visualization_container = ComposableNodeContainer(
        package='carma_ros2_utils', # rclcpp_components
        name='lanelet2_map_visualization_container',
        executable='lifecycle_component_wrapper_mt',
        namespace= GetCurrentNamespace(),
        composable_node_descriptions=[
            ComposableNode(
                package='map_file_ros2',
                plugin='lanelet2_map_visualization::Lanelet2MapVisualization',
                name='lanelet2_map_visualization',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('lanelet2_map_visualization', env_log_levels) },
                    {'is_lifecycle_node': True} # Flag to allow lifecycle node loading in lifecycle wrapper
                ],
                remappings=[
                    ("lanelet_map_bin", "semantic_map"),
                    ("change_state", "disabled_change_state"), # Disable lifecycle topics since this is a lifecycle wrapper container
                    ("get_state", "disabled_get_state")        # Disable lifecycle topics since this is a lifecycle wrapper container
                ],
                parameters=[
                    vehicle_config_param_file
                ]
            )
        ]
    )

    # Cooperative Perception Stack
    carma_cooperative_perception_container = ComposableNodeContainer(
        condition=IfCondition(is_cp_mot_enabled),
        package='carma_ros2_utils', # rclcpp_components
        name='carma_cooperative_perception_container',
        executable='carma_component_container_mt',
        namespace= GetCurrentNamespace(),
        output='screen',
        composable_node_descriptions=[
            ComposableNode(
                package='carma_cooperative_perception',
                plugin='carma_cooperative_perception::ExternalObjectListToDetectionListNode',
                name='cp_external_object_list_to_detection_list_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cp_external_object_list_to_detection_list_node', env_log_levels) },
                ],
                remappings=[
                    ("input/georeference", [EnvironmentVariable("CARMA_LOCZ_NS", default_value=""), "/map_param_loader/georeference"]),
                    ("output/detections", "full_detection_list"),
                    ("input/external_objects", "external_objects"),
                ],
                parameters=[
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='carma_cooperative_perception',
                plugin='carma_cooperative_perception::ExternalObjectListToSdsmNode',
                name='cp_external_object_list_to_sdsm_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cp_external_object_list_to_sdsm_node', env_log_levels) },
                ],
                remappings=[
                    ("input/georeference", [EnvironmentVariable("CARMA_LOCZ_NS", default_value=""), "/map_param_loader/georeference"]),
                    ("output/sdsms", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/outgoing_sdsm" ] ),
                    ("input/pose_stamped", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("input/external_objects", "external_objects"),
                ],
                parameters=[
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='carma_cooperative_perception',
                plugin='carma_cooperative_perception::HostVehicleFilterNode',
                name='cp_host_vehicle_filter_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cp_host_vehicle_filter_node', env_log_levels) },
                ],
                remappings=[
                    ("input/host_vehicle_pose", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/current_pose" ] ),
                    ("input/detection_list", "full_detection_list"),
                    ("output/detection_list", "filtered_detection_list")
                ],
                parameters=[
                    cp_host_vehicle_filter_node_file,
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='carma_cooperative_perception',
                plugin='carma_cooperative_perception::SdsmToDetectionListNode',
                name='cp_sdsm_to_detection_list_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cp_sdsm_to_detection_list_node', env_log_levels) },
                ],
                remappings=[
                    ("input/georeference", [ EnvironmentVariable('CARMA_LOCZ_NS', default_value=''), "/map_param_loader/georeference" ] ),
                    ("input/sdsm", [ EnvironmentVariable('CARMA_MSG_NS', default_value=''), "/incoming_sdsm" ] ),
                    ("input/cdasim_clock", "/sim_clock"),
                    ("output/detections", "full_detection_list"),
                ],
                parameters=[
                    vehicle_config_param_file,
                    cp_sdsm_to_detection_list_node_file
                ]
            ),
            ComposableNode(
                package='carma_cooperative_perception',
                plugin='carma_cooperative_perception::TrackListToExternalObjectListNode',
                name='cp_track_list_to_external_object_list_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cp_track_list_to_external_object_list_node', env_log_levels) },
                ],
                remappings=[
                    ("input/track_list", "cooperative_perception_track_list"),
                    ("output/external_object_list", "fused_external_objects"),
                ],
                parameters=[
                    vehicle_config_param_file
                ]
            ),
            ComposableNode(
                package='carma_cooperative_perception',
                plugin='carma_cooperative_perception::MultipleObjectTrackerNode',
                name='cp_multiple_object_tracker_node',
                extra_arguments=[
                    {'use_intra_process_comms': True},
                    {'--log-level' : GetLogLevel('cp_multiple_object_tracker_node', env_log_levels) },
                ],
                remappings=[
                    ("output/track_list", "cooperative_perception_track_list"),
                    ("input/detection_list", "filtered_detection_list"),
                ],
                parameters=[
                    cp_multiple_object_tracker_node_file,
                    vehicle_config_param_file
                ]

            ),

        ]
    )

    # subsystem_controller which orchestrates the lifecycle of this subsystem's components
    subsystem_controller = Node(
        package='subsystem_controllers',
        name='environment_perception_controller',
        executable='environment_perception_controller',
        parameters=[
            subsystem_controller_default_param_file,
            subsystem_controller_param_file,
            {"use_sim_time" : use_sim_time}],
        on_exit= Shutdown(), # Mark the subsystem controller as required
        arguments=['--ros-args', '--log-level', GetLogLevel('subsystem_controllers', env_log_levels)]
    )

    return LaunchDescription([
        declare_vehicle_characteristics_param_file_arg,
        declare_vehicle_config_param_file_arg,
        declare_use_sim_time_arg,
        declare_is_autoware_lidar_obj_detection_enabled,
        declare_is_cp_mot_enabled,
        declare_subsystem_controller_param_file_arg,
        declare_vector_map_file,
        lidar_perception_container,
        carma_external_objects_container,
        lanelet2_map_loader_container,
        lanelet2_map_visualization_container,
        carma_cooperative_perception_container,
        subsystem_controller
    ])
