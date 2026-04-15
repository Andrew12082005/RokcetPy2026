from rocketpy import Flight
from env import env
from rocket import JRI


# ========== 執行模擬 ==========
test = Flight(
    rocket=JRI,
    environment=env,
    rail_length=4,
    inclination=86,
    heading=90
)

# ========== 輸出結果 ==========

# 匯出 KML（可選）

test.export_kml(
    file_name="trajectory.kml",
    extrude=True,
    altitude_mode="relative_to_ground",
)


# 繪圖與資訊輸出
#r.draw()
env.info()
test.plots.trajectory_3d()

# 其他可用的輸出（取消註解使用）:
# env.info()
# test.prints.initial_conditions()
# test.prints.launch_rail_conditions()
# test.prints.out_of_rail_conditions()
# test.prints.burn_out_conditions()
test.prints.apogee_conditions()
# test.prints.events_registered()
# test.prints.impact_conditions()
# test.prints.maximum_values()
# test.speed.plot(0, test.max_time)
# test.plots.angular_kinematics_data()
# test.plots.stability_and_control_data()
# test.plots.linear_kinematics_data()
# test.plots.flight_path_angle_data()