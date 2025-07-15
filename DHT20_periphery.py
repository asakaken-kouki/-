from periphery import I2C
import time

i2c = I2C("/dev/i2c-1")  # Raspberry PiのI2Cバス

# 書き込み: 測定コマンド [0xAC, 0x33, 0x00]
msgs = [I2C.Message([0xAC, 0x33, 0x00])]
i2c.transfer(0x38, msgs)

# 適切に待機後、7バイト読み取り
time.sleep(0.1)
read = I2C.Message([0x00] * 7, read=True)
i2c.transfer(0x38, [read])
print("Raw data:", read.data)

#データ格納
hum = read.data[1] << 12 | read.data[2] << 4 | ((read.data[3] & 0xF0) >> 4)
tmp = ((read.data[3] & 0x0F) << 16) | read.data[4] << 8 | read.data[5]
      
#湿度変換  
hum = hum / 2**20 * 100
#温度変換
tmp = tmp / 2**20 * 200 - 50
        
print("湿度（しつど）: " + str(hum) + "%")
print("温度（おんど）: " + str(tmp) + "℃")