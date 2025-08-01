#pragma once

/*
 * Copyright (C) 2022 LEIDOS.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */

#include <iostream>
#include <vector>

namespace light_controlled_intersection_tactical_plugin
{

  /**
   * \brief Stuct containing the algorithm configuration values for light_controlled_intersection_tactical_plugin
   */
  struct Config
  {
    double centerline_sampling_spacing = 1.0;
    double trajectory_time_length = 12.0;
    int default_downsample_ratio = 10;
    int turn_downsample_ratio = 5;
    double curve_resample_step_size = 1.0;
    int curvature_moving_average_window_size = 9;
    int speed_moving_average_window_size = 5;
    double back_distance = 20.0;
    double buffer_ending_downtrack = 40.0;
    double vehicle_decel_limit_multiplier = 1.0;
    double vehicle_accel_limit_multiplier = 1.0;
    double lat_accel_multiplier = 1.0;
    double stop_line_buffer = 0.50;
    double minimum_speed = 4.4704;
    double dist_before_intersection_to_force_last_traj = 35.0;
    double period_before_intersection_to_force_last_traj = 4.5;
    double lateral_accel_limit = 2.5;
    double vehicle_accel_limit = 2.0;
    double vehicle_decel_limit = 2.0;
    double vehicle_response_lag = 1.0;
    int tactical_plugin_service_call_timeout = 100;
    bool enable_object_avoidance = false;

    // Stream operator for this config
    friend std::ostream &operator<<(std::ostream &output, const Config &c)
    {
      output << "light_controlled_intersection_tactical_plugin::Config { " << std::endl
           << "centerline_sampling_spacing: " << c.centerline_sampling_spacing << std::endl
           << "trajectory_time_length: " << c.trajectory_time_length << std::endl
           << "default_downsample_ratio: " << c.default_downsample_ratio << std::endl
           << "turn_downsample_ratio: " << c.turn_downsample_ratio << std::endl
           << "curve_resample_step_size: " << c.curve_resample_step_size << std::endl
           << "curvature_moving_average_window_size: " << c.curvature_moving_average_window_size << std::endl
           << "speed_moving_average_window_size: " << c.speed_moving_average_window_size << std::endl
           << "back_distance: " << c.back_distance << std::endl
           << "buffer_ending_downtrack: " << c.buffer_ending_downtrack << std::endl
           << "vehicle_decel_limit_multiplier: " << c.vehicle_decel_limit_multiplier << std::endl
           << "vehicle_accel_limit_multiplier: " << c.vehicle_accel_limit_multiplier << std::endl
           << "lat_accel_multiplier: " << c.lat_accel_multiplier << std::endl
           << "stop_line_buffer: " << c.stop_line_buffer << std::endl
           << "minimum_speed: " << c.minimum_speed << std::endl
           << "dist_before_intersection_to_force_last_traj: " << c.dist_before_intersection_to_force_last_traj << std::endl
           << "period_before_intersection_to_force_last_traj: " << c.period_before_intersection_to_force_last_traj << std::endl
           << "lateral_accel_limit: " << c.lateral_accel_limit << std::endl
           << "vehicle_accel_limit: " << c.vehicle_accel_limit << std::endl
           << "vehicle_decel_limit: " << c.vehicle_decel_limit << std::endl
           << "vehicle_response_lag: " << c.vehicle_response_lag << std::endl
           << "tactical_plugin_service_call_timeout: " << c.tactical_plugin_service_call_timeout << std::endl
           << "enable_object_avoidance: " << c.enable_object_avoidance << std::endl
           << "}" << std::endl;
      return output;
    }
  };

} // light_controlled_intersection_tactical_plugin
