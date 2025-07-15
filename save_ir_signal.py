# save_ir_signal.py
import pigpio
import time
import json

RECV_GPIO = 12
MIN_GAP = 80000  # μs

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
        return self.recording

rec = IRRecorder(RECV_GPIO)
record = rec.wait_and_get_record()

with open("ir_data.json", "w") as f:
    json.dump(record, f)

print("受信完了。信号を ir_data.json に保存しました。")
print(f"\n学習した信号長（μs）：{record}")