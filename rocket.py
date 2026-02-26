from rocketpy import Rocket, Tail

r = Rocket(
    radius=0.0615,        
    mass=10.0,              
    inertia=(1.0, 1.0, 0.1),
    power_off_drag="src/drag_curve.csv",
    power_on_drag="src/drag_curve.csv",
    center_of_mass_without_motor=3, 
    coordinate_system_orientation="nose_to_tail"
)


r.add_nose(
    length=0.684,
    kind="vonKarman",
    base_radius=0.057, 
    position = 0
)

r.add_tail(
    top_radius=0.057,    
    bottom_radius=0.0615,   
    length=0.50,
    position=1.254
)


r.draw()

