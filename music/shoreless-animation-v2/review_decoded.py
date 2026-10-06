from pathlib import Path
import cv2

H = Path(__file__).resolve().parent
for layer, second in [('lights', 4), ('foam', 6), ('antennas', 6.7), ('room', 7), ('sunlight', 7)]:
    path = H / f'{layer}-isolated-v2-8s.mp4'
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
    ok, frame = cap.read()
    cap.release()
    assert ok, path
    cv2.imwrite(str(H / f'decoded-{layer}-{second}s.png'), frame)
print('Five isolated decoded review frames saved')
