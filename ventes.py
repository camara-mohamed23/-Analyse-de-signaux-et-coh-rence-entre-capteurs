import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

# ===========================
# Fonction radar_factory (identique à ton code)
# ===========================
def radar_factory(num_vars, frame='circle'):
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):
        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown frame: %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown frame: %s" % frame)

    register_projection(RadarAxes)
    return theta

# ===========================
# Charger les données ventes
# ===========================
df = pd.read_csv("ventes.csv")
produits = df['produit']
magasins = df.columns[1:]
data = df[magasins].values

# ===========================
# Créer le radar chart
# ===========================
N = len(produits)
theta = radar_factory(N, frame='polygon')

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='radar'))
fig.subplots_adjust(top=0.85, bottom=0.05)

colors = ['b', 'r', 'g', 'm']
for d, color, magasin in zip(data.T, colors, magasins):
    ax.plot(theta, d, color=color, label=magasin)
    ax.fill(theta, d, facecolor=color, alpha=0.25)

ax.set_varlabels(produits)

# Légende
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

fig.text(0.5, 0.95, 'Ventes des produits par magasin',
         horizontalalignment='center', color='black', weight='bold', size='large')

plt.show()