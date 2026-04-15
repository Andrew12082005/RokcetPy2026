"""
Monte Carlo Simulation for MQ90 Rocket
Based on RocketPy's MonteCarlo class (v1.2.0+)
"""

import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# 確保 log 資料夾存在，避免存檔報錯
os.makedirs("log", exist_ok=True)

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
    StochasticNoseCone,     
    StochasticTail          
)

# ── 【終極修復】全域攔截 RocketPy v1.2.0+ 尾翼 Bug ──
# 確保在 Windows 多核心環境下，所有 Worker 都不會觸發 sweep_length 衝突
_original_create_object = StochasticTrapezoidalFins.create_object

def _patched_create_object(self):
    original_sweep = getattr(self, 'sweep_length', [None])
    self.sweep_length = [None] # 強制屏蔽 sweep_length
    try:
        return _original_create_object(self)
    finally:
        self.sweep_length = original_sweep

StochasticTrapezoidalFins.create_object = _patched_create_object
# ───────────────────────────────────────────────────────────────────────────────

from env import env
from motor import MQ90
from rocket import JRI

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
    grain_outer_radius=(0.0475, 0.00005),            
    grain_initial_height=(0.18, 0.0005),             
    grain_initial_inner_radius=(0.017, 0.0003),     
    nozzle_radius=(0.0275, 0.0005),                 
    throat_radius=(0.0165, 0.0003),                 
    dry_mass=(7.2, 0.3),
    total_impulse=(10652.67 , 1500),                            
    grains_center_of_mass_position=(0.423, 0.01),   
    center_of_dry_mass_position=(0.36087, 0.01),      
)
#stochastic_motor.visualize_attributes()
# ── Stochastic Rocket ──
stochastic_rocket = StochasticRocket(
    rocket=JRI,
    radius=(0.0615, 0.0005),                        
    mass=(10.0, 0.2),                               
    center_of_mass_without_motor=(0.88, 0.01),      
    power_off_drag_factor=(1.0, 0.05), 
    power_on_drag_factor=(1.0, 0.05)
)

stochastic_rocket.add_motor(stochastic_motor, position=(2.15, 0.005))



# ── 氣動元件的隨機包裝 (Nose, Tail, Fins) ──
# 1. 鼻錐
deterministic_nose = JRI.aerodynamic_surfaces[0][0]
stoch_nose = StochasticNoseCone(
    nosecone=deterministic_nose,
    length=0.002,          
    base_radius=0.0005     
)
stochastic_rocket.add_nose(stoch_nose, position=(0, 0.001)) 

# 2. 尾段 (Tail 1 & 2)
deterministic_tail_1 = JRI.aerodynamic_surfaces[1][0]
stoch_tail_1 = StochasticTail(
    tail=deterministic_tail_1,
    top_radius=0.0005,
    bottom_radius=0.0005,
    length=0.001
)
stochastic_rocket.add_tail(stoch_tail_1, position=(1.29, 0.001))

deterministic_tail_2 = JRI.aerodynamic_surfaces[2][0]
stoch_tail_2 = StochasticTail(
    tail=deterministic_tail_2,
    top_radius=0.0005,
    bottom_radius=0.0005,
    length=0.001
)
stochastic_rocket.add_tail(stoch_tail_2, position=(2.15, 0.001))

# 3. 尾翼 (Fins)
deterministic_fins = JRI.aerodynamic_surfaces[3][0] 
stoch_fins = StochasticTrapezoidalFins(
    trapezoidal_fins=deterministic_fins,
    span=0.001,       
    root_chord=0.001, 
    tip_chord=0.001   
)
stochastic_rocket.add_trapezoidal_fins(stoch_fins, position=(2.02, 0.01))

# ── Stochastic Flight ──
stochastic_flight = StochasticFlight(
    flight=Flight(
        rocket=JRI,
        environment=env,
        rail_length=4,
        inclination=86,
        heading=90,
    ),
    inclination=(86, 1),       
    heading=(90, 2),           
)


# ==============================================================================
# 3.  MONTE CARLO RUNNER & PLOTS (Windows 多核心保護區塊)
# ==============================================================================
# ==============================================================================
# 3.  MONTE CARLO RUNNER & PLOTS (Windows 多核心保護區塊)
# ==============================================================================
if __name__ == '__main__':
    import os
    from datetime import datetime
    
    N_SIMULATIONS = 500

    # 1. 確保使用絕對路徑，防止 Worker 核心路徑迷失
    base_dir = os.path.abspath("log")
    os.makedirs(base_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 使用 os.path.join 自動處理 Windows 的斜線反斜線問題
    base_filename = os.path.join(base_dir, f"monte_carlo_mq90_{timestamp}")
    open(f"{base_filename}.outputs.txt", "w", encoding="utf-8").close()
    open(f"{base_filename}.errors.txt", "w", encoding="utf-8").close()

    mc = MonteCarlo(
        filename=base_filename,          
        environment=stochastic_env,
        rocket=stochastic_rocket,
        flight=stochastic_flight,
    )

    print(f"\n{'='*60}")
    print(f"  Starting Monte Carlo simulation — {N_SIMULATIONS} runs")
    print(f"{'='*60}\n")

    # 開啟多核心運算 (n_workers 設為 6)
    mc.simulate(number_of_simulations=N_SIMULATIONS, parallel=True, n_workers=10)

    print("\n── Summary Statistics ──────────────────────────────────────")
    mc.prints.all()

    results = mc.results

    # ── 1. 自訂統計直方圖 ──
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle(f"MQ90 Monte Carlo — Flight Parameter Distributions ({N_SIMULATIONS} runs)", fontsize=14)

    fields = [
        ("apogee",               "Apogee (m AGL)",         axes[0, 0]),
        ("impact_velocity",      "Impact Velocity (m/s)",  axes[0, 1]),
        ("max_mach_number",      "Max Mach Number",        axes[0, 2]),
        ("out_of_rail_velocity", "Out-of-Rail Vel. (m/s)", axes[1, 0]),
        ("apogee_time",          "Time to Apogee (s)",     axes[1, 1]), 
        ("t_final",              "Total Flight Time (s)",  axes[1, 2]), 
    ]

    for key, label, ax_hist in fields:
        data = results.get(key, [])
        if not data or len(data) == 0:
            ax_hist.set_title(f"{label}\n(no data)")
            continue
        ax_hist.hist(data, bins=max(1, int(len(data) ** 0.5)), color="steelblue", edgecolor="white")
        ax_hist.axvline(np.mean(data), color="red",    linestyle="--", label=f"Mean: {np.mean(data):.2f}")
        ax_hist.axvline(np.percentile(data, 5),  color="orange", linestyle=":",  label=f"5th pct: {np.percentile(data, 5):.2f}")
        ax_hist.axvline(np.percentile(data, 95), color="orange", linestyle=":",  label=f"95th pct: {np.percentile(data, 95):.2f}")
        ax_hist.set_title(label)
        ax_hist.set_xlabel(label)
        ax_hist.set_ylabel("Count")
        ax_hist.legend(fontsize=7)

    plt.tight_layout()
    plt.savefig(f"{base_filename}_histograms.png", dpi=150, bbox_inches="tight")
    plt.show()

    # ── 2. 繪製 1σ, 2σ, 3σ 散佈橢圓與落點分析圖 ──
    print("\n── Generating Dispersion Ellipses Plot ─────────────────────")

    apogee_x = np.array(results.get("apogee_x", []))
    apogee_y = np.array(results.get("apogee_y", []))
    impact_x = np.array(results.get("x_impact", []))
    impact_y = np.array(results.get("y_impact", []))

    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:, order]

    if len(impact_x) > 1 and len(apogee_x) > 1: 
        fig_ell, ax_ell = plt.subplots(figsize=(10, 8), dpi=150, facecolor="w", edgecolor="k")

        # --- 落點誤差橢圓 ---
        impactCov = np.cov(impact_x, impact_y)
        impactVals, impactVecs = eigsorted(impactCov)
        impactTheta = np.degrees(np.arctan2(*impactVecs[:, 0][::-1]))
        impactW, impactH = 2 * np.sqrt(impactVals)

        for j in [1, 2, 3]:
            impactEll = Ellipse(
                xy=(np.mean(impact_x), np.mean(impact_y)),
                width=impactW * j,
                height=impactH * j,
                angle=impactTheta,
                color="black",
            )
            impactEll.set_facecolor((0, 0, 1, 0.15)) 
            ax_ell.add_artist(impactEll)

        # --- 最高點誤差橢圓 ---
        apogeeCov = np.cov(apogee_x, apogee_y)
        apogeeVals, apogeeVecs = eigsorted(apogeeCov)
        apogeeTheta = np.degrees(np.arctan2(*apogeeVecs[:, 0][::-1]))
        apogeeW, apogeeH = 2 * np.sqrt(apogeeVals)

        for j in [1, 2, 3]:
            apogeeEll = Ellipse(
                xy=(np.mean(apogee_x), np.mean(apogee_y)),
                width=apogeeW * j,
                height=apogeeH * j,
                angle=apogeeTheta,
                color="black",
            )
            apogeeEll.set_facecolor((0, 1, 0, 0.15)) 
            ax_ell.add_artist(apogeeEll)

        # --- 繪製散佈點 ---
        ax_ell.scatter(0, 0, s=100, marker="*", color="black", zorder=5, label="Launch Point")
        ax_ell.scatter(apogee_x, apogee_y, s=10, marker="^", color="green", zorder=4, label="Simulated Apogee")
        ax_ell.scatter(impact_x, impact_y, s=10, marker="v", color="blue", zorder=4, label="Simulated Landing Point")

        # --- 嘗試載入背景地圖 ---
        map_path = "monte_carlo_analysis_inputs/Valetudo_basemap_final.jpg"
        if os.path.exists(map_path):
            img = plt.imread(map_path)
            dx, dy = 0, 0 
            ax_ell.imshow(img, zorder=0, extent=[-1000 - dx, 1000 - dx, -1000 - dy, 1000 - dy])
        else:
            ax_ell.grid(True, linestyle="--", alpha=0.5)

        # --- 圖表設定 ---
        ax_ell.axhline(0, color="black", linewidth=0.5)
        ax_ell.axvline(0, color="black", linewidth=0.5)
        ax_ell.set_title(f"1$\sigma$, 2$\sigma$ and 3$\sigma$ Dispersion Ellipses ({N_SIMULATIONS} runs)")
        ax_ell.set_ylabel("North (m)")
        ax_ell.set_xlabel("East (m)")
        ax_ell.legend()
        
        ax_ell.set_aspect("equal")
        ax_ell.set_xlim(-200, 3000)
        ax_ell.set_ylim(-1600, 1600)

        print(f"[Debug] 實際落點分佈: East {np.min(impact_x):.1f} ~ {np.max(impact_x):.1f}, North {np.min(impact_y):.1f} ~ {np.max(impact_y):.1f}")

        plt.tight_layout()
        plt.savefig(f"{base_filename}_dispersion_ellipses.pdf", bbox_inches="tight", pad_inches=0.1)
        plt.savefig(f"{base_filename}_dispersion_ellipses.png", bbox_inches="tight", pad_inches=0.1)
        plt.show()
    else:
        print("\n[警告] 模擬成功的資料點不足 (需要 >= 2)，無法計算共變異數矩陣與繪製橢圓。")

    # ── 3. 高度對時間分析 (Altitude vs Time) ──
    print("\n── Generating Altitude vs Time plot ────────────────────────")
    try:
        fig_z, ax_z = plt.subplots(figsize=(10, 5))
        
        nominal_flight = stochastic_flight.obj
        time_data = nominal_flight.z.x_array
        alt_data = nominal_flight.z.y_array
        
        ax_z.plot(time_data, alt_data, color="darkgreen", linewidth=2, label="Nominal Trajectory")
        
        ax_z.set_title("Nominal Flight Trajectory: Altitude vs Time")
        ax_z.set_xlabel("Time (s)")
        ax_z.set_ylabel("Altitude (m AGL)")
        ax_z.legend()
        ax_z.grid(True, linestyle="--", alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(f"{base_filename}_altitude_vs_time.png", dpi=150, bbox_inches="tight")
        plt.show()

    except Exception as e:
        print(f"繪製高度圖時發生錯誤: {e}")

    print(f"\nDone! 所有分析圖表已儲存至 log/ 目錄下。")