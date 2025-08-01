// Copyright 2023 Leidos
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef CARMA_COOPERATIVE_PERCEPTION__MSG_CONVERSION_HPP_
#define CARMA_COOPERATIVE_PERCEPTION__MSG_CONVERSION_HPP_

#include <units.h>

#include <carma_cooperative_perception_interfaces/msg/detection_list.hpp>
#include <carma_cooperative_perception_interfaces/msg/track.hpp>
#include <carma_cooperative_perception_interfaces/msg/track_list.hpp>
#include <carma_perception_msgs/msg/external_object.hpp>
#include <carma_perception_msgs/msg/external_object_list.hpp>
#include <carma_v2x_msgs/msg/sensor_data_sharing_message.hpp>

#include "carma_cooperative_perception/geodetic.hpp"
#include "carma_cooperative_perception/j2735_types.hpp"
#include "carma_cooperative_perception/j3224_types.hpp"

#include <geometry_msgs/msg/pose_stamped.hpp>

#include <lanelet2_core/geometry/Lanelet.h>
#include <lanelet2_extension/projection/local_frame_projector.h>

#include <tf2/LinearMath/Quaternion.h>

#include <memory>
#include <string>
#include <string_view>

namespace carma_cooperative_perception
{
class SdsmToDetectionListConfig
{
public:
  SdsmToDetectionListConfig() = default;
  bool overwrite_covariance{false};
  double pose_covariance_x{0.125};
  double pose_covariance_y{0.125};
  double pose_covariance_z{0.125};
  double pose_covariance_yaw{0.005};
  double twist_covariance_x{0.005};
  double twist_covariance_z{0.005};
  double twist_covariance_yaw{0.005};
  bool adjust_pose{false};
  double x_offset{0.0};
  double y_offset{0.0};
  double yaw_offset{0.0};

  // Stream operator for logging
  friend std::ostream & operator<<(std::ostream & os, const SdsmToDetectionListConfig & config)
  {
    os << "SdsmToDetectionListConfig{"
       << "\n  overwrite_covariance: " << config.overwrite_covariance
       << "\n  pose_covariance_x: " << config.pose_covariance_x
       << "\n  pose_covariance_y: " << config.pose_covariance_y
       << "\n  pose_covariance_z: " << config.pose_covariance_z
       << "\n  pose_covariance_yaw: " << config.pose_covariance_yaw
       << "\n  twist_covariance_x: " << config.twist_covariance_x
       << "\n  twist_covariance_z: " << config.twist_covariance_z
       << "\n  twist_covariance_yaw: " << config.twist_covariance_yaw
       << "\n  adjust_pose: " << config.adjust_pose
       << "\n  x_offset: " << config.x_offset
       << "\n  y_offset: " << config.y_offset
       << "\n  yaw_offset: " << config.yaw_offset
       << "\n}";
    return os;
  }
};

// NOTE: If incoming SDSM message doesn't have timezone enabled,
// it automatically uses the local timezone. If the node is running in a container,
// it would mean the container's default timezone (most likely UTC), unless otherwise set.
// Make sure the container's timezone is same as the implicit timezone of the SDSM's timestamp
auto to_time_msg(
  const DDateTime & d_date_time, bool is_simulation) -> builtin_interfaces::msg::Time;

auto calc_detection_time_stamp(DDateTime d_date_time, const MeasurementTimeOffset & offset)
  -> DDateTime;

auto to_ddate_time_msg(const builtin_interfaces::msg::Time & builtin_time)
  -> j2735_v2x_msgs::msg::DDateTime;

auto calc_sdsm_time_offset(
  const builtin_interfaces::msg::Time & external_object_list_time,
  const builtin_interfaces::msg::Time & external_object_time)
  -> carma_v2x_msgs::msg::MeasurementTimeOffset;

auto to_position_msg(const UtmCoordinate & position_utm) -> geometry_msgs::msg::Point;

auto heading_to_enu_yaw(const units::angle::degree_t & heading) -> units::angle::degree_t;

auto calc_relative_position(
  const geometry_msgs::msg::PoseStamped & current_pose,
  const carma_v2x_msgs::msg::PositionOffsetXYZ & detected_object_data)
  -> carma_v2x_msgs::msg::PositionOffsetXYZ;

auto transform_pose_from_map_to_wgs84(
  const geometry_msgs::msg::PoseStamped & source_pose,
  const std::shared_ptr<lanelet::projection::LocalFrameProjector> & map_projection)
  -> carma_v2x_msgs::msg::Position3D;

auto to_detection_list_msg(
  const carma_v2x_msgs::msg::SensorDataSharingMessage & sdsm, std::string_view georeference,
  bool is_simulation, const std::optional<SdsmToDetectionListConfig>& conversion_adjustment)
  -> carma_cooperative_perception_interfaces::msg::DetectionList;

struct MotionModelMapping
{
  std::uint8_t small_vehicle_model{
    carma_cooperative_perception_interfaces::msg::Detection::MOTION_MODEL_CTRV};
  std::uint8_t large_vehicle_model{
    carma_cooperative_perception_interfaces::msg::Detection::MOTION_MODEL_CTRV};
  std::uint8_t motorcycle_model{
    carma_cooperative_perception_interfaces::msg::Detection::MOTION_MODEL_CTRV};
  std::uint8_t pedestrian_model{
    carma_cooperative_perception_interfaces::msg::Detection::MOTION_MODEL_CTRV};
  std::uint8_t unknown_model{
    carma_cooperative_perception_interfaces::msg::Detection::MOTION_MODEL_CTRV};
};

auto to_detection_msg(
  const carma_perception_msgs::msg::ExternalObject & object,
  const MotionModelMapping & motion_model_mapping)
  -> carma_cooperative_perception_interfaces::msg::Detection;

auto to_detection_list_msg(
  const carma_perception_msgs::msg::ExternalObjectList & object_list,
  const MotionModelMapping & motion_model_mapping)
  -> carma_cooperative_perception_interfaces::msg::DetectionList;

auto to_external_object_msg(const carma_cooperative_perception_interfaces::msg::Track & track)
  -> carma_perception_msgs::msg::ExternalObject;

auto to_external_object_list_msg(
  const carma_cooperative_perception_interfaces::msg::TrackList & track_list)
  -> carma_perception_msgs::msg::ExternalObjectList;

auto to_sdsm_msg(
  const carma_perception_msgs::msg::ExternalObjectList & external_object_list,
  const geometry_msgs::msg::PoseStamped & current_pose,
  const std::shared_ptr<lanelet::projection::LocalFrameProjector> & map_projection)
  -> carma_v2x_msgs::msg::SensorDataSharingMessage;

auto to_detected_object_data_msg(
  const carma_perception_msgs::msg::ExternalObject & external_object,
  const std::shared_ptr<lanelet::projection::LocalFrameProjector> & map_projection)
  -> carma_v2x_msgs::msg::DetectedObjectData;

auto enu_orientation_to_true_heading(
  double yaw, const lanelet::BasicPoint3d & obj_pose,
  const std::shared_ptr<lanelet::projection::LocalFrameProjector> & map_projection)
  -> units::angle::degree_t;

}  // namespace carma_cooperative_perception

#endif  // CARMA_COOPERATIVE_PERCEPTION__MSG_CONVERSION_HPP_
