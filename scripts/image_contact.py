import sys, cv2, numpy as np
names = sys.argv[2:]
ims = []
for n in names:
    a = cv2.imread(n + ".png"); h, w = a.shape[:2]
    if abs(w / h - 2) > 0.01:
        if w / h < 2: c = round(w / 2); a = a[(h - c) // 2:(h - c) // 2 + c]
        else: c = round(h * 2); a = a[:, (w - c) // 2:(w - c) // 2 + c]
    a = cv2.resize(a, (1774, 887))
    for k in range(0, 1774, 200): cv2.line(a, (k, 0), (k, 887), (0, 0, 255), 2)
    for k in range(0, 887, 200): cv2.line(a, (0, k), (1774, k), (0, 0, 255), 2)
    cv2.putText(a, n, (10, 60), 0, 1.8, (0, 255, 255), 4)
    ims.append(cv2.resize(a, (600, 300)))
while len(ims) % 3: ims.append(np.zeros_like(ims[0]))
rows = [np.hstack(ims[i:i + 3]) for i in range(0, len(ims), 3)]
cv2.imwrite(sys.argv[1], np.vstack(rows))
