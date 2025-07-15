# send_ir_signal.py
import pigpio
import time
import json

SEND_GPIO = 21  # 赤外線LEDの制御ピン

with open("ir_data.json", "r") as f:
    pulses = json.load(f)

pi = pigpio.pi()
if not pi.connected:
    exit()

# 波形を作成
pi.set_mode(SEND_GPIO, pigpio.OUTPUT)
pi.wave_clear()

carrier = 38000  # 38kHz キャリア周波数
cycles = int(1000000 / carrier)  # 1周期の長さ（μs）

def carrier_pulse(duration):
    # duration中にON/OFFを繰り返す（キャリア波生成）
    waveform = []
    on_time = int(cycles * 0.33)  # ON時間（33%デューティ）
    off_time = cycles - on_time
    total = 0
    while total + cycles <= duration:
        waveform.append(pigpio.pulse(1 << SEND_GPIO, 0, on_time))
        waveform.append(pigpio.pulse(0, 1 << SEND_GPIO, off_time))
        total += cycles
    # 最後に余った分をOFFで埋める
    if total < duration:
        waveform.append(pigpio.pulse(0, 1 << SEND_GPIO, duration - total))
    return waveform

wave = []

for i in range(len(pulses)):
    if i % 2 == 0:
        # ON期間：キャリア送信
        wave += carrier_pulse(pulses[i])
    else:
        # OFF期間：LED消灯
        wave.append(pigpio.pulse(0, 0, pulses[i]))

pi.wave_add_generic(wave)
wid = pi.wave_create()

print("信号を送信します...")
pi.wave_send_once(wid)

while pi.wave_tx_busy():
    time.sleep(0.1)

pi.wave_delete(wid)
pi.stop()
print("送信完了。")