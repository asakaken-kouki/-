from smbus2 import SMBus
import time
import sys

DHT20_ADDR = 0x38

# センサー初期化確認
with SMBus(1) as bus:
    status = bus.read_byte_data(DHT20_ADDR, 0x71)
    if status & 0x18 != 0x18:
        print("初期化エラー: status=0x{:02X}".format(status))
        sys.exit()
    else:
        print("初期化成功: status=0x{:02X}".format(status))

def read_dht20():
    with SMBus(1) as bus:
        # 初期化後に一度待つ（重要）
        time.sleep(0.1)

        # 測定開始コマンド送信
        try:
            bus.write_i2c_block_data(DHT20_ADDR, 0xAC, [0x33, 0x00])
            time.sleep(0.1)
        except OSError as e:
            print("書き込み失敗:", e)
            return None

        time.sleep(0.1)  # 測定待機時間（100ms）

        try:
            time.sleep(0.01)
            data = bus.read_i2c_block_data(DHT20_ADDR, 0x00, 7)
        except OSError as e:
            print("読み取り失敗:", e)
            return None

        print(data)

        humidity_raw = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) & 0xFFFFF
        temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        humidity = (humidity_raw / 1048576.0) * 100
        temperature = (temperature_raw / 1048576.0) * 200 - 50

        return temperature, humidity

result = read_dht20()
if result:
    temp, hum = result
    print(f"温度: {temp:.2f}℃, 湿度: {hum:.2f}%")
else:
    print("DHT20の読み取りに失敗しました。")