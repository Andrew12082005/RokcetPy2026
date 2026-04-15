from rocketpy import Rocket, Tail
from motor import MQ90 


JRI = Rocket(
    radius=0.0615,
    mass=8.44,
    inertia=(1.0, 1.0, 0.1),
    power_off_drag="src/powerOffDragCurve.csv",
    power_on_drag="src/powerOnDragCurve.csv",
    center_of_mass_without_motor=0.888,
    coordinate_system_orientation="nose_to_tail"
)

    # 添加鼻錐
JRI.add_nose(
    length=0.684,
    kind="vonKarman",
    base_radius=0.057,
    position=0
)

    # 添加尾部
JRI.add_tail(
    top_radius=0.057,
    bottom_radius=0.0615,
    length=0.06,
    position=1.29
)

JRI.add_tail(
    top_radius=0.0615,
    bottom_radius=0.052,
    length=0.05,
    position=2.15
    )

    # 添加尾翼
JRI.add_trapezoidal_fins(
    n=4,
    root_chord=0.132,
    tip_chord=0.0689,
    span=0.108,
    position=2.02,
    sweep_angle=38.5
)

    # 添加引擎（從參數傳入）
JRI .add_motor(MQ90, position=2.15)
#r.draw()

