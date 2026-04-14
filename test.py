"""
Monte Carlo Simulation for MQ90 Rocket
Based on RocketPy's MonteCarlo class (v1.2.0+)
"""

import datetime
import numpy as np
import matplotlib.pyplot as plt

# ── RocketPy core ──────────────────────────────────────────────────────────────
from rocketpy import (
    Environment,
    SolidMotor,
    Rocket,
    Flight,
    MonteCarlo,
)
from rocketpy.stochastic import (
    StochasticEnvironment,
    StochasticSolidMotor,
    StochasticRocket,
    StochasticFlight,
    StochasticTrapezoidalFins,
    StochasticNoseCone,     # 新增：隨機鼻錐類別
    StochasticTail          # 新增：隨機尾段類別
)

# ==============================================================================
# 1.  DETERMINISTIC BASELINE (確定性基礎模型)
# ==============================================================================

# ── Environment ──
env = Environment(latitude=22.182484, longitude=120.890888, elevation=2)
env.set_date(datetime.datetime(2026, 1, 25, 12, 0, 0))
env.set_atmospheric_model(type="standard_atmosphere")

# ── Motor ──
MQ90 = SolidMotor(
    thrust_source="MQ_90V_0.4.eng",          # 請確認路徑正確
    coordinate_system_orientation="nozzle_to_combustion_chamber",
    burn_time=4.69,
    dry_mass=4.0,
    dry_inertia=(0.01, 0.01, 0.01),
    grain_separation=0.01,
    center_of_dry_mass_position=0.35,
    grains_center_of_mass_position=0.35,
    grain_number=4,
    grain_density=1750.0,
    grain_outer_radius=0.0475,
    grain_initial_height=0.18,
    grain_initial_inner_radius=0.017,
    nozzle_radius=0.0275,
    throat_radius=0.0165,
    nozzle_position=0,
)

# ── Rocket ──
rocket = Rocket(
    radius=0.0615,
    mass=10.0,
    inertia=(1.0, 1.0, 0.1),
    power_off_drag="powerOffDragCurve.csv",
    power_on_drag="powerOnDragCurve.csv",
    center_of_mass_without_motor=0.88,
    coordinate_system_orientation="nose_to_tail",
)

rocket.add_nose(length=0.684, kind="vonKarman", base_radius=0.057, position=0)
rocket.add_tail(top_radius=0.057, bottom_radius=0.0615, length=0.06, position=1.252)
rocket.add_trapezoidal_fins(n=4, root_chord=0.132, tip_chord=0.0689, span=0.102, position=1.96)
rocket.add_motor(MQ90, position=2.15)

# ==============================================================================
# 2.  STOCHASTIC WRAPPERS (隨機擾動模型)
# ==============================================================================

# ── Stochastic Environment ──
stochastic_env = StochasticEnvironment(
    environment=env,
    elevation=(2, 1),              
)

# ── Stochastic Motor ──
stochastic_motor = StochasticSolidMotor(
    solid_motor=MQ90,
    grain_density=(1750.0, 50.0),                   
    grain_outer_radius=(0.0475, 0.0005),            
    grain_initial_height=(0.18, 0.002),             
    grain_initial_inner_radius=(0.017, 0.0003),     
    nozzle_radius=(0.0275, 0.0005),                 
    throat_radius=(0.0165, 0.0003),                 
    dry_mass=(4.0, 0.1),                            
    grains_center_of_mass_position=(0.35, 0.005),   
    center_of_dry_mass_position=(0.35, 0.005),      
)

# ── Stochastic Rocket ──
stochastic_rocket = StochasticRocket(
    rocket=rocket,
    radius=(0.0615, 0.0005),                        
    mass=(10.0, 0.2),                               
    center_of_mass_without_motor=(0.88, 0.01),      
    power_off_drag_factor=(1.0, 0.05), 
    power_on_drag_factor=(1.0, 0.05)
)

stochastic_rocket.add_motor(stochastic_motor, position=(2.15, 0.005))

# ── 氣動元件的隨機包裝 (Nose, Tail, Fins) ──
# 1. 鼻錐
deterministic_nose = rocket.aerodynamic_surfaces[0][0]
stoch_nose = StochasticNoseCone(
    nosecone=deterministic_nose,
    length=0.002,          # 給定 2mm 長度公差
    base_radius=0.0005     # 給定 0.5mm 底部半徑公差
)
stochastic_rocket.add_nose(stoch_nose, position=(0, 0.001)) # 鼻錐安裝位置公差 1mm

# 2. 尾段 (Tail)
deterministic_tail = rocket.aerodynamic_surfaces[1][0]
stoch_tail = StochasticTail(
    tail=deterministic_tail,
    top_radius=0.0005,
    bottom_radius=0.0005,
    length=0.001
)
stochastic_rocket.add_tail(stoch_tail, position=(1.252, 0.005)) # 安裝位置公差 5mm

# 3. 尾翼 (Fins)
deterministic_fins = rocket.aerodynamic_surfaces[2][0] 
stoch_fins = StochasticTrapezoidalFins(
    trapezoidal_fins=deterministic_fins,
    span=0.001,       
    root_chord=0.001, 
    tip_chord=0.001   
)
stochastic_rocket.add_trapezoidal_fins(stoch_fins, position=(1.96, 0.01))

# ── Stochastic Flight ──
stochastic_flight = StochasticFlight(
    flight=Flight(
        rocket=rocket,
        environment=env,
        rail_length=4,
        inclination=86,
        heading=90,
    ),
    inclination=(86, 1),       
    heading=(90, 2),           
)

# ==============================================================================
# 3.  MONTE CARLO RUNNER
# ==============================================================================
N_SIMULATIONS = 5

mc = MonteCarlo(
    filename="monte_carlo_mq90",          
    environment=stochastic_env,
    rocket=stochastic_rocket,
    flight=stochastic_flight,
    # 移除 export_list，讓 RocketPy V1.2.0 自動抓取預設的安全屬性清單
)

print(f"\n{'='*60}")
print(f"  Starting Monte Carlo simulation — {N_SIMULATIONS} runs")
print(f"{'='*60}\n")

# 開啟平行運算 (parallel=True) 加速！
mc.simulate(number_of_simulations=N_SIMULATIONS)

# ==============================================================================
# 4.  RESULTS & PLOTS
# ==============================================================================

print("\n── Summary Statistics ──────────────────────────────────────")
mc.prints.all()

print("\n── Generating dispersion plots ─────────────────────────────")
mc.plots.ellipses(
    xlim=(-200, 3500), ylim=(-200, 200)
)
mc.plots.ellipses()


fig, axes = plt.subplots(2, 3, figsize=(15, 9))
fig.suptitle("MQ90 Monte Carlo — Flight Parameter Distributions", fontsize=14)

# 【修正點】: 將舊版變數名稱 (time_to_apogee, flight_time) 改為 V1.2.0+ 正確鍵值
fields = [
    ("apogee",               "Apogee (m AGL)",         axes[0, 0]),
    ("max_velocity",         "Max Velocity (m/s)",      axes[0, 1]),
    ("max_mach_number",      "Max Mach Number",         axes[0, 2]),
    ("out_of_rail_velocity", "Out-of-Rail Vel. (m/s)",  axes[1, 0]),
    ("apogee_time",          "Time to Apogee (s)",      axes[1, 1]), # 修改鍵值
    ("impact_time",          "Total Flight Time (s)",   axes[1, 2]), # 修改鍵值
]

results = mc.results          

for key, label, ax in fields:
    data = results.get(key, [])
    if len(data) == 0:
        ax.set_title(f"{label}\n(no data)")
        continue
    ax.hist(data, bins=int(len(data) ** 0.5), color="steelblue", edgecolor="white")
    ax.axvline(np.mean(data), color="red",    linestyle="--", label=f"Mean: {np.mean(data):.2f}")
    ax.axvline(np.percentile(data, 5),  color="orange", linestyle=":",  label=f"5th pct: {np.percentile(data, 5):.2f}")
    ax.axvline(np.percentile(data, 95), color="orange", linestyle=":",  label=f"95th pct: {np.percentile(data, 95):.2f}")
    ax.set_title(label)
    ax.set_xlabel(label)
    ax.set_ylabel("Count")
    ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig("monte_carlo_histograms.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Landing dispersion scatter ──
impact_x = np.array(results.get("impact_x", []))
impact_y = np.array(results.get("impact_y", []))

if len(impact_x) > 0:
    fig2, ax2 = plt.subplots(figsize=(7, 7))
    ax2.scatter(impact_x, impact_y, alpha=0.4, s=10, label="Simulated landings")
    ax2.scatter(0, 0, marker="*", s=200, color="red", zorder=5, label="Launch point")
    ax2.set_xlabel("East (m)")
    ax2.set_ylabel("North (m)")
    ax2.set_title("Landing Point Dispersion — MQ90")
    ax2.legend()
    ax2.set_aspect("equal")
    plt.tight_layout()
    plt.savefig("monte_carlo_landing_dispersion.png", dpi=150, bbox_inches="tight")
    plt.show()

print("\nDone!  Results saved to:")
print("  monte_carlo_mq90.outputs.txt  (raw simulation data)")
print("  monte_carlo_histograms.png")
print("  monte_carlo_landing_dispersion.png")