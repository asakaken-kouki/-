import pigpio
import time

RECV_GPIO = 12
MIN_GAP = 80000      # μs、信号終了とみなす無信号時間
ROUND_STEP = 100    # μs単位での丸め
MAX_MISMATCH_RATE = 0.1  # 10%までの違いは許容

class IRRecorder:
    def __init__(self, gpio):
        self.pi = pigpio.pi()
        self.gpio = gpio
        self.last_tick = 0
        self.recording = []
        self.finished = False

        self.pi.set_mode(gpio, pigpio.INPUT)
        self.cb = self.pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):
        if self.last_tick != 0:
            duration = pigpio.tickDiff(self.last_tick, tick)
            self.recording.append(duration)
            if duration > MIN_GAP:
                self.finished = True
        self.last_tick = tick

    def wait_and_get_record(self):
        print("赤外線信号を受信してください...")
        while not self.finished:
            time.sleep(0.01)
        self.cb.cancel()
        self.pi.stop()
        if len(self.recording) < 20:
            print("⚠️ 信号が短すぎます。送信失敗の可能性があります。")
        return self.recording

def round_signal(sig, step=ROUND_STEP):
    return [round(x / step) * step for x in sig]

def is_similar_signal(sig1, sig2):
    r1 = round_signal(sig1)
    r2 = round_signal(sig2)

    if abs(len(r1) - len(r2)) > 2:
        return False

    min_len = min(len(r1), len(r2))
    mismatch = 0
    for a, b in zip(r1[:min_len], r2[:min_len]):
        if a != b:
            mismatch += 1

    mismatch_rate = mismatch / min_len
    return mismatch_rate < MAX_MISMATCH_RATE

# === メイン処理 ===
print("1回目の信号受信")
rec1 = IRRecorder(RECV_GPIO)
sig1 = rec1.wait_and_get_record()
print("1回目の受信完了。")

time.sleep(1)

print("2回目の信号受信")
rec2 = IRRecorder(RECV_GPIO)
sig2 = rec2.wait_and_get_record()
print("2回目の受信完了。")

print("\n--- 比較結果 ---")
if is_similar_signal(sig1, sig2):
    print("✅ 2回の信号は同じと判定されました")
else:
    print("❌ 2回の信号は異なると判定されました")

print(f"\n1回目の信号長（μs）：{sig1}")
print(f"2回目の信号長（μs）：{sig2}")