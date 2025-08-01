
/*------------------------------------------------------------------------------
* Copyright (C) 2020-2021 LEIDOS.
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

------------------------------------------------------------------------------*/

#include "platooning_strategic_ihp/platooning_manager_ihp.h"
#include "platooning_strategic_ihp/platooning_strategic_ihp.h"
#include "platooning_strategic_ihp/platooning_config_ihp.h"
#include <gtest/gtest.h>
#include <carma_wm/WMListener.hpp>
#include <carma_wm/WorldModel.hpp>
#include <carma_wm/CARMAWorldModel.hpp>
#include <carma_ros2_utils/timers/testing/TestTimerFactory.hpp>

using namespace platooning_strategic_ihp;

TEST(PlatooningManagerTest, test_construct)
{
    PlatooningPluginConfig config;
    std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

    PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {},
        std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
    // Use Getter to retrieve host Platoon Manager class
    PlatooningManager pm_ = plugin.getHostPM();
    pm_.current_platoon_state = PlatoonState::LEADER;
}

TEST(PlatooningManagerTest, test_ecef_encode)
{
    PlatooningPluginConfig config;
    std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

    PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {},
        std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());

    carma_v2x_msgs::msg::LocationECEF ecef_point_test;
    ecef_point_test.ecef_x = 1.0;
    ecef_point_test.ecef_y = 2.0;
    ecef_point_test.ecef_z = 3.0;
    // Update ecef location
    plugin.setHostECEF(ecef_point_test);
    plugin.run_candidate_leader();
}


TEST(PlatooningManagerTest, test_split)
{
    carma_v2x_msgs::msg::MobilityOperation msg;
    std::string strategyParams("INFO|REAR:1,LENGTH:2,SPEED:3,SIZE:4");
    std::vector<std::string> inputsParams;
    boost::algorithm::split(inputsParams, strategyParams, boost::is_any_of(","));
    std::vector<std::string> rearVehicleBsmId_parsed;
    boost::algorithm::split(rearVehicleBsmId_parsed, inputsParams[0], boost::is_any_of(":"));
    std::string rearVehicleBsmId = rearVehicleBsmId_parsed[1];
    std::cout << "rearVehicleBsmId: " << rearVehicleBsmId << std::endl;

    std::vector<std::string> rearVehicleDtd_parsed;
    boost::algorithm::split(rearVehicleDtd_parsed, inputsParams[1], boost::is_any_of(":"));
    double rearVehicleDtd = std::stod(rearVehicleDtd_parsed[1]);
    std::cout << "rearVehicleDtd: " << rearVehicleDtd << std::endl;
}

// These tests has been temporarily disabled to support Continuous Improvement (CI) processes.
// Related GitHub Issue: <https://github.com/usdot-fhwa-stol/carma-platform/issues/2335>

// TEST(PlatooningManagerTest, test_states)
// {
//     PlatooningPluginConfig config;
//     std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

//     PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {});
//     pm_.current_platoon_state = PlatoonState::LEADER;
//     pm_.current_downtrack_distance_ = 20;

//     carma_v2x_msgs::msg::MobilityRequest request;
//     request.plan_type.type = 3;
//     request.strategy_params = "SIZE:1,SPEED:0,DTD:11.5599";

//     plugin.mob_req_cb(request);

//     EXPECT_EQ(pm_.current_platoon_state, PlatoonState::LEADERWAITING);
// }

TEST(PlatooningManagerTest, test_compose)
{
    std::string OPERATION_STATUS_PARAMS = "STATUS|CMDSPEED:%1%,DTD:%2%,SPEED:%3%";
    double cmdSpeed = 1;
    double current_speed = 2;
    double current_downtrack = 4;
    boost::format fmter(OPERATION_STATUS_PARAMS);
    fmter %cmdSpeed;
    fmter %current_downtrack;
    fmter %current_speed;
    std::string statusParams = fmter.str();

    std::cout << "statusParams: " << statusParams << std::endl;
}


TEST(PlatooningStrategicIHPPlugin, mob_resp_cb)
{
    PlatooningPluginConfig config;
    std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

    PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {},
        std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
    // Use Getter to retrieve host Platoon Manager class
    PlatooningManager pm_ = plugin.getHostPM();
    pm_.current_platoon_state = PlatoonState::FOLLOWER;

    plugin.onSpin();

}

// These tests has been temporarily disabled to support Continuous Improvement (CI) processes.
// Related GitHub Issue: <https://github.com/usdot-fhwa-stol/carma-platform/issues/2335>

// TEST(PlatooningStrategicIHPPlugin, platoon_info_pub)
// {
//     PlatooningPluginConfig config;
//     std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

//     PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {},
//         std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
//     // Use Getter to retrieve host Platoon Manager class
//     PlatooningManager pm_ = plugin.getHostPM();
//     pm_.current_platoon_state = PlatoonState::LEADER;

//     carma_planning_msgs::msg::PlatooningInfo info_msg1 = plugin.composePlatoonInfoMsg();
//     EXPECT_EQ(info_msg1.leader_id, "default_id");

//     pm_.current_platoon_state = PlatoonState::FOLLOWER;
//     pm_.isFollower = true;
//     PlatoonMember member = PlatoonMember("1", 1.0, 1.1, 0.1, 0, 100);
//     std::vector<PlatoonMember> cur_pl;
//     cur_pl.push_back(member);
//     pm_.host_platoon_ = cur_pl;

//     carma_planning_msgs::msg::PlatooningInfo info_msg2 = plugin.composePlatoonInfoMsg();
//     EXPECT_EQ(info_msg2.leader_id, "1");
// }

// TEST(PlatooningStrategicIHPPlugin, test_follower)
// {
//     PlatooningPluginConfig config;
//     std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

//     PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {},
//         std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
//     // Use Getter to retrieve host Platoon Manager class
//     PlatooningManager pm_ = plugin.getHostPM();
//     pm_.current_platoon_state = PlatoonState::CANDIDATEFOLLOWER;
//     pm_.current_plan.valid = true;
//     EXPECT_EQ(pm_.isFollower, false);

//     auto resp = std::make_unique<carma_v2x_msgs::msg::MobilityResponse>();
//     resp->m_header.plan_id = "resp";
//     resp->is_accepted = true;
//     plugin.mob_resp_cb(std::move(resp));
//     EXPECT_EQ(pm_.current_platoon_state, PlatoonState::FOLLOWER);
//     EXPECT_EQ(pm_.isFollower, true);
// }

TEST(PlatooningStrategicIHPPlugin, test_get_leader)
{
    PlatooningPluginConfig config;
    std::shared_ptr<carma_wm::CARMAWorldModel> wm = std::make_shared<carma_wm::CARMAWorldModel>();

    PlatooningStrategicIHPPlugin plugin(wm, config, [&](auto) {}, [&](auto) {}, [&](auto) {}, [&](auto) {},
        std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
    // Use Getter to retrieve host Platoon Manager class
    PlatooningManager pm_ = plugin.getHostPM();
    pm_.current_platoon_state = PlatoonState::FOLLOWER;

    PlatoonMember member = PlatoonMember("1", 1.0, 1.1, 0.1, 0, 100);
    std::vector<PlatoonMember> cur_pl;
    cur_pl.push_back(member);

    pm_.host_platoon_ = cur_pl;

    EXPECT_EQ(pm_.host_platoon_.size(), 1ul);

    PlatoonMember member1 = pm_.host_platoon_[0];

    pm_.isFollower = true;
    PlatoonMember platoon_leader = pm_.getDynamicLeader();

    EXPECT_EQ(member1.staticId, "1");
    EXPECT_EQ(platoon_leader.staticId, "1");
}


TEST(PlatooningManagerTest, test2)
{
    platooning_strategic_ihp::PlatoonMember* member = new platooning_strategic_ihp::PlatoonMember("1", 1.0, 1.1, 0.1, 0, 100);
    std::vector<platooning_strategic_ihp::PlatoonMember> cur_pl;

    cur_pl.push_back(*member);

    platooning_strategic_ihp::PlatooningManager pm(std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
    pm.host_platoon_ = cur_pl;

    pm.isFollower = true;
    pm.platoonLeaderID = "0";
    pm.currentPlatoonID = "a";

    std::string params = "CMDSPEED:11,DOWNTRACK:01,SPEED:11";

    pm.updatesOrAddMemberInfo(cur_pl, "2", 2.0, 1.0, 0.0, 2.5); //HERE

    EXPECT_EQ(2ul, cur_pl.size());
    EXPECT_EQ("2", cur_pl[0].staticId);
}


TEST(PlatooningManagerTest, test3)
{
    platooning_strategic_ihp::PlatoonMember* member1 = new platooning_strategic_ihp::PlatoonMember("1", 1.0, 1.1, 0.1, 0, 100);
    platooning_strategic_ihp::PlatoonMember* member2 = new platooning_strategic_ihp::PlatoonMember("2", 2.0, 2.1, 0.2, 0, 200);
    std::vector<platooning_strategic_ihp::PlatoonMember> cur_pl;

    cur_pl.push_back(*member1);
    cur_pl.push_back(*member2);

    platooning_strategic_ihp::PlatooningManager pm(std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
    pm.host_platoon_ = cur_pl;

    pm.isFollower = false;
    pm.platoonLeaderID = "0";
    pm.currentPlatoonID = "a";

    int res = pm.getHostPlatoonSize();

    EXPECT_EQ(2, res);

}

TEST(PlatooningManagerTest, test4)
{
    platooning_strategic_ihp::PlatoonMember* member1 = new platooning_strategic_ihp::PlatoonMember("1", 1.0, 1.1, 0.1, 0, 100);
    platooning_strategic_ihp::PlatoonMember* member2 = new platooning_strategic_ihp::PlatoonMember("2", 2.0, 2.1, 0.2, 0, 200);
    std::vector<platooning_strategic_ihp::PlatoonMember> cur_pl;

    cur_pl.push_back(*member1);
    cur_pl.push_back(*member2);

    platooning_strategic_ihp::PlatooningManager pm(std::make_shared<carma_ros2_utils::timers::testing::TestTimerFactory>());
    pm.host_platoon_ = cur_pl;

    pm.isFollower = true;
    pm.platoonLeaderID = "0";
    pm.currentPlatoonID = "a";

    int res = pm.allPredecessorFollowing();

    EXPECT_EQ(0, res);
}
