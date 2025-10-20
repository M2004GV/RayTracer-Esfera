# Enhanced Phong visualization with multiple colored spheres (ambient, diffuse, specular)
# Saves a side-by-side image similar to the user's reference.
import numpy as np
import matplotlib.pyplot as plt

# ---------- Camera & image ----------
W, H = 512, 320  # wide layout
aspect = W / H
eye = np.array([-8.0, 0.0, 0.0], dtype=float)
fov = np.deg2rad(60)
df = 6.0
half_h = df * np.tan(fov * 0.5)
half_v = half_h / aspect

# ---------- Scene: three spheres ----------
# Big red, small blue, small green
spheres = [
    {"center": np.array([3.0, 0.0, 0.0]), "radius": 1.6, "color": np.array([0.95, 0.1, 0.1]),
     "ka": 0.15, "kd": 0.85, "ks": 0.25, "shininess": 64},
    {"center": np.array([2.3, -0.55, 0.4]), "radius": 0.5, "color": np.array([0.1, 0.35, 0.95]),
     "ka": 0.18, "kd": 0.85, "ks": 0.3, "shininess": 96},
    {"center": np.array([4.1, 0.65, -0.15]), "radius": 0.4, "color": np.array([0.3, 0.95, 0.3]),
     "ka": 0.18, "kd": 0.85, "ks": 0.35, "shininess": 32},
]

# ---------- Light ----------
light_pos = np.array([-2.0, 2.5, 2.0])
light_int = 1.2

bg_color = np.array([0.02, 0.02, 0.02])

def normalize(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    n = np.where(n==0, 1.0, n)
    return v / n

def intersect_sphere(ro, rd, center, radius):
    # returns t or np.inf
    oc = ro - center
    b = np.sum(rd * oc, axis=-1)
    c = np.sum(oc * oc, axis=-1) - radius * radius
    disc = b*b - c
    hit = disc >= 0
    t = np.where(hit, -b - np.sqrt(np.maximum(disc, 0.0)), np.inf)
    t2 = np.where(hit, -b + np.sqrt(np.maximum(disc, 0.0)), np.inf)
    # pick closest positive
    t = np.where((t > 1e-4), t, np.where((t2 > 1e-4), t2, np.inf))
    return t

# Build primary rays
ys = np.linspace(-half_v, half_v, H)
zs = np.linspace(half_h, -half_h, W)
py, pz = np.meshgrid(ys, zs, indexing='ij')
px = np.full_like(py, eye[0] + df)
pixels = np.stack([px, py, pz], axis=-1)
rays = normalize(pixels - eye)

# Trace against all spheres
tmin = np.full((H, W), np.inf)
sid = np.full((H, W), -1, dtype=int)

for i, s in enumerate(spheres):
    t = intersect_sphere(eye, rays, s["center"], s["radius"])
    mask = t < tmin
    tmin = np.where(mask, t, tmin)
    sid[mask] = i

hit = sid >= 0
P = eye + rays * tmin[..., None]  # hit points
N = np.zeros_like(P)
color = np.zeros((H, W, 3))
ka = np.zeros((H, W, 1))
kd = np.zeros((H, W, 1))
ks = np.zeros((H, W, 1))
shin = np.zeros((H, W, 1))

# Fill per-hit material and normal
for i, s in enumerate(spheres):
    m = hit & (sid == i)
    if not np.any(m):
        continue
    N[m] = normalize(P[m] - s["center"])
    color[m] = s["color"]
    ka[m] = s["ka"]
    kd[m] = s["kd"]
    ks[m] = s["ks"]
    shin[m] = s["shininess"]

# Lighting vectors
L = normalize(light_pos - P)
V = normalize(eye - P)
R = normalize(2.0 * (np.sum(N*L, axis=-1, keepdims=True)) * N - L)

# Components
Iamb = ka * color
Idif = kd * color * np.maximum(0.0, np.sum(N*L, axis=-1, keepdims=True)) * light_int
Ispe = ks * (np.maximum(0.0, np.sum(R*V, axis=-1, keepdims=True)) ** np.maximum(shin,1.0)) * light_int

# Shadow (simple hard shadow): cast ray from P toward light; if occluded, zero out dif/spec
# move origin slightly along normal to avoid self-intersection
shadow = np.ones((H, W, 1), dtype=float)
Po = P + N * 1e-3
to_light = normalize(light_pos - Po)
for i, s in enumerate(spheres):
    # do not self-occlude check via sid
    t = intersect_sphere(Po, to_light, s["center"], s["radius"])
    # where t is finite and less than light distance, it's in shadow
    dist_l = np.linalg.norm(light_pos - Po, axis=-1, keepdims=True)
    occ = (t[..., None] < dist_l) & (t[..., None] < np.inf) & (sid[..., None] != i)
    shadow = np.where(occ, 0.0, shadow)

Idif *= shadow
Ispe *= shadow

# Compose passes
img_ambient  = np.where(hit[..., None], Iamb, bg_color)
img_diffuse  = np.where(hit[..., None], Iamb + Idif, bg_color)
img_specular = np.where(hit[..., None], Iamb + Ispe, bg_color)
img_full     = np.where(hit[..., None], Iamb + Idif + Ispe, bg_color)

# Simple tone mapping/gamma
def post(x):
    x = np.clip(x, 0, 1.0)
    return np.power(x, 1/2.2)

img_ambient  = post(img_ambient)
img_diffuse  = post(img_diffuse)
img_specular = post(img_specular)
img_full     = post(img_full)

# Plot similar to reference: three panels + title labels
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
titles = ["Ambiente", "Difuso", "Especular"]
for ax, im, t in zip(axes, [img_ambient, img_diffuse, img_specular], titles):
    ax.imshow(im, origin='upper')
    ax.set_title(t, fontsize=16, fontweight='bold')
    ax.axis('off')

plt.tight_layout()
plt.savefig('phong_ambient_diffuse_specular.png', dpi=160, bbox_inches='tight')

# Also save a 4th full image
plt.figure(figsize=(4,4))
plt.imshow(img_full, origin='upper')
plt.title("Phong Completo", fontsize=14, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('phong_full.png', dpi=160, bbox_inches='tight')

