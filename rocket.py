from rocketpy import Rocket, Tail
from motor import MQ90 


r = Rocket(
    radius=0.0615,
    mass=10.0,
    inertia=(1.0, 1.0, 0.1),
    power_off_drag="src/drag_curve.csv",
    power_on_drag="src/drag_curve.csv",
    center_of_mass_without_motor=0.88,
    coordinate_system_orientation="nose_to_tail"
)

    # 添加鼻錐
r.add_nose(
    length=0.684,
    kind="vonKarman",
    base_radius=0.057,
    position=0
)

    # 添加尾部
r.add_tail(
    top_radius=0.057,
    bottom_radius=0.0615,
    length=0.06,
    position=1.252
)

    # 添加尾翼
r.add_trapezoidal_fins(
    n=4,
    root_chord=0.132,
    tip_chord=0.0689,
    span=0.102,
    position=1.96
)

    # 添加引擎（從參數傳入）
r.add_motor(MQ90, position=2.15)
r.draw()

