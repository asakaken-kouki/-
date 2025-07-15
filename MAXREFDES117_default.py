import time
from smbus2 import SMBus

# 定数
MAX30102_ADDRESS = 0x57
REG_INTR_STATUS_1 = 0x00
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
    except Exception as e:
        print(f"読み取り失敗: {e}")
        return None, None

# メイン
def main():
    with SMBus(1) as bus:
        max30102_init(bus)
        print("MAX30102 初期化完了")

        while True:
            red, ir = read_fifo(bus)
            if red is not None and ir is not None:
                print(f"赤外線: {ir}, 赤色: {red}")
            time.sleep(0.1)

if __name__ == "__main__":
    main()
