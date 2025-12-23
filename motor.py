from rocketpy import SolidMotor

MQ90 = SolidMotor(
    thrust_source="src/MQ_90_V0.3.1.eng",
    burn_time=4.69,
    dry_mass=7,
    dry_inertia=(0.01, 0.01, 0.01),
    grain_separation=0.01,
    center_of_dry_mass_position=1.0,
    grains_center_of_mass_position=1.0,
    grain_number=4,
    grain_density=1750.0,
    grain_outer_radius=0.0535,
    grain_initial_height=0.18,
    grain_initial_inner_radius=0.017,
    nozzle_radius=0.0275,
    throat_radius=0.0165,
    nozzle_position=0
)
    
MQ90.info()
