#[IN]
from smbus2 import SMBus
import time

class DHT20:
    def __init__(self, bus_number):
        self.bus = SMBus(bus_number)
        self.address = 0x38
        if (self.dht20_read_status() & 0x80) == 0x80:
            self.dht20_init()

    #運転状態の読み込み（確認）
    def dht20_read_status(self):
        return self.bus.read_byte_data(self.address, 0x71)

    #初期化※実行前にセンサーがBusy状態の場合
    def dht20_init(self):
        self.bus.write_i2c_block_data(self.address, 0xa8, [0x00, 0x00])
        time.sleep(0.01)
        self.bus.write_i2c_block_data(self.address, 0xbe, [0x08, 0x00])

    #データの読み込み
    def read_dht20(self):
        # 2バイトのデータを書き込むためにwrite_i2c_block_dataを使用
        self.bus.write_i2c_block_data(self.address, 0xac, [0x33, 0x00])
        time.sleep(0.08)  # 80ms待機
        cnt = 0
        while (self.dht20_read_status() & 0x80) == 0x80:
            time.sleep(0.001)  # 1ms待機
            cnt += 1
            if cnt >= 100:
                break
        data = self.bus.read_i2c_block_data(self.address, 0x00, 7)  # 7バイト読み込み
        return data

    #CRC8計算(CRC:巡回冗長検査)
    def calc_crc8(self, data):
        crc = 0xff
        for i in data[:-1]:
            crc ^= i
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc <<= 1
                crc &= 0xff
        return crc

    #温度計算
    def dht20_temperature(self):
        data = self.read_dht20()
        #ビット演算でデータを結合
        Temper = 0
        Temper = (Temper | data[3]) << 8
        Temper = (Temper | data[4]) << 8
        Temper = Temper | data[5]
        Temper = Temper & 0xFFFFF  #ビットマスキングで下位20ビットを取得
        return (Temper * 200 / 1024 / 1024) - 50

    #湿度計算
    def dht20_humidity(self):
        data = self.read_dht20()
        #ビット演算でデータを結合
        humidity = 0
        humidity = (humidity | data[1]) << 8
        humidity = (humidity | data[2]) << 8
        humidity = humidity | data[3] 
        humidity = humidity >> 4 #下位4ビットを削除
        return humidity / 1024/ 1024 * 100

# I2Cの設定
bus_number = 1
sensor = DHT20(bus_number)

while True:
    data = sensor.read_dht20()
    print(f'Data: {data}')
    temperature = sensor.dht20_temperature()
    humidity = sensor.dht20_humidity()
    print(f'Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%')
    time.sleep(1)