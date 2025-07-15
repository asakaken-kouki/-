import time
import numpy as np
from scipy.signal import find_peaks
from smbus2 import SMBus

# I2C定義とレジスタ
MAX30102_ADDRESS = 0x57
REG_INTR_ENABLE_1 = 0x02
REG_INTR_ENABLE_2 = 0x03
REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C
REG_LED2_PA = 0x0D

# 初期化
def max30102_init(bus):
    bus.write_byte_data(MAX30102_ADDRESS, REG_INTR_ENABLE_1, 0x00)
    bus.write_byte_data(MAX30102_ADDRESS, REG_INTR_ENABLE_2, 0x00)
    bus.write_byte_data(MAX30102_ADDRESS, REG_FIFO_WR_PTR, 0x00)
    bus.write_byte_data(MAX30102_ADDRESS, REG_OVF_COUNTER, 0x00)
    bus.write_byte_data(MAX30102_ADDRESS, REG_FIFO_RD_PTR, 0x00)
    bus.write_byte_data(MAX30102_ADDRESS, REG_MODE_CONFIG, 0x03)
    bus.write_byte_data(MAX30102_ADDRESS, REG_SPO2_CONFIG, 0x27)
    bus.write_byte_data(MAX30102_ADDRESS, REG_LED1_PA, 0x24)
    bus.write_byte_data(MAX30102_ADDRESS, REG_LED2_PA, 0x24)

# FIFO読み取り
def read_fifo(bus):
    try:
        data = bus.read_i2c_block_data(MAX30102_ADDRESS, REG_FIFO_DATA, 6)
        red = (data[0] << 16 | data[1] << 8 | data[2]) & 0x3FFFF
        ir = (data[3] << 16 | data[4] << 8 | data[5]) & 0x3FFFF
        return red, ir
    except:
        return None, None

# 心拍数を計算
def calculate_bpm(ir_data, sample_rate):
    ir_array = np.array(ir_data)
    ir_array = ir_array - np.mean(ir_array)  # DC除去
    ir_array = np.convolve(ir_array, np.ones(5)/5, mode='same')  # 簡易ローパス

    peaks, _ = find_peaks(ir_array, distance=sample_rate * 0.5, prominence=1000)

    if len(peaks) > 1:
        peak_intervals = np.diff(peaks) / sample_rate  # 秒
        avg_interval = np.mean(peak_intervals)
        bpm = 60 / avg_interval
        return int(bpm)
    else:
        return None

# メイン
def main():
    SAMPLE_RATE = 100  # 100Hz
    WINDOW_SECONDS = 5
    WINDOW_SIZE = SAMPLE_RATE * WINDOW_SECONDS

    ir_buffer = []

    with SMBus(1) as bus:
        max30102_init(bus)
        print("MAX30102 初期化完了")

        while True:
            _, ir = read_fifo(bus)
            if ir is not None:
                ir_buffer.append(ir)
                if len(ir_buffer) > WINDOW_SIZE:
                    ir_buffer = ir_buffer[-WINDOW_SIZE:]  # 最新のN秒間だけ保持

                    bpm = calculate_bpm(ir_buffer, SAMPLE_RATE)
                    if bpm:
                        print(f"心拍数: {bpm} BPM")
                    else:
                        print("心拍を検出できません")
                else:
                    print(f"赤外線: {ir} - 測定中...")

            time.sleep(1.0 / SAMPLE_RATE)

if __name__ == "__main__":
    main()
