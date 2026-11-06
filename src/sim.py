import numpy as np, math, colorsys

W, H, FPS = 1080, 1920, 30
CX, CY, RING = W / 2, 1000, 450
SUB = 8
G = 2600.0           # px/s^2
R0, GROW = 26.0, 3.2  # start radius, growth per bounce
VMIN = 1500.0


def simulate(seed=7, max_t=30.0):
    rng = np.random.default_rng(seed)
    p = np.array([60.0, -150.0])
    v = np.array([420.0, 0.0])
    r = R0
    dt = 1.0 / FPS / SUB
    frames, bounces = [], []
    t = 0.0
    hue = 0.0
    end_t = None
    while t < max_t:
        for _ in range(SUB):
            v[1] += G * dt
            p += v * dt
            d = math.hypot(*p)
            if d + r >= RING:
                n = p / d
                vn = v @ n
                if vn > 0:
                    v -= 2 * vn * n
                    tang = np.array([-n[1], n[0]])
                    v += tang * rng.uniform(-90, 90)
                    sp = math.hypot(*v)
                    if sp < VMIN:
                        v *= VMIN / sp
                    contact = n * RING
                    hue = (hue + 0.047) % 1.0
                    r += GROW
                    bounces.append(dict(t=t, pt=contact.copy(), hue=hue, idx=len(bounces)))
                p = n * (RING - r - 0.5)
            t += dt
        frames.append(dict(t=t, p=p.copy(), r=r, hue=hue, nb=len(bounces)))
        if r >= RING - 6 and end_t is None:
            end_t = t
            break
    return frames, bounces, end_t


if __name__ == "__main__":
    f, b, e = simulate()
    print("bounces", len(b), "end", e, "frames", len(f))
