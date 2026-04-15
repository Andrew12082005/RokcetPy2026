from rocketpy import SolidMotor

MQ90 = SolidMotor(
    thrust_source="src/MQ_90V_0.4.eng",
    coordinate_system_orientation="nozzle_to_combustion_chamber",
    burn_time=4.69,
    dry_mass=7.2,
    dry_inertia=(0.52974, 0.52974, 0.02048),
    grain_separation=0.001,
    center_of_dry_mass_position=0.36087,
    grains_center_of_mass_position=0.423,
    grain_number=4,
    grain_density=1750.0,
    grain_outer_radius=0.0475,
    grain_initial_height=0.18,
    grain_initial_inner_radius=0.017,
    nozzle_radius=0.0275,
    throat_radius=0.0165,
    nozzle_position=0
    )

#MQ90.draw()
