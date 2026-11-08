# 2D Dynamic River Landscape Simulation

An interactive 2D dynamic river landscape simulation built with Python and Pygame. This project demonstrates core computer graphics algorithms written from scratch, including DDA line drawing, Bresenham line drawing, Midpoint circle drawing, and Bézier curves.

## 📸 Screenshots

| Day Mode | Sunset / Night Mode |
| :---: | :---: |
| ![Day Mode](screenshots/day_mode.png) | ![Sunset Mode](screenshots/sunset_mode.png) |

---

## ⚙️ Algorithms Implemented

- **DDA Line Drawing Algorithm:** Used for sun rays, river surface reflections, and dynamic rain ripples.
- **Bresenham's Line Drawing Algorithm:** Used for palm tree trunks, distant forest trunks, bird wings, and boat details.
- **Midpoint Circle Algorithm:** Used for sun, cloud segments, distant tree crowns, and boat rider details.
- **Quadratic Bézier Curves:** Applied for smooth curvature and dynamic sway of palm tree trunks, fronds, and foreground Kashful plumes.

---

## 🎮 Interactive Controls

| Key | Action |
| :--- | :--- |
| `N` | Toggle Day / Night (Sunset) Mode |
| `R` | Toggle Rain On / Off |
| `C` | Toggle Clouds On / Off |
| `SPACE` | Pause / Resume Scene Animation |
| `UP` / `DOWN` | Move Sun Up / Down |
| `LEFT` / `RIGHT` | Adjust River Flow Speed |
| `A` / `D` | Adjust Wind Force (Left / Right sway) |
| `Q` / `W` | Change Birds' Flight Direction |

---

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/2D-River-Landscape-Simulation.git](https://github.com/your-username/2D-River-Landscape-Simulation.git)
   cd 2D-River-Landscape-Simulation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the simulation:**
   ```bash
   python main.py
   ```