import smbus
import time

i2c = smbus.SMBus(1)
address = 0x38

trigger = [0xAC, 0x33, 0x00]
#送るバイト  役割
#0xAC      コマンドコード：「測定を開始してデータを準備せよ」
#0x33      測定モードの指定（温湿度を測定）
#0x00      予約（常に0でOK）

dat = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

#初期チェック
time.sleep(0.1)
ret = i2c.read_byte_data(address, 0x71)

if ret != 0x18:
    exit()
    
print("初期化完了")

try:
    while True:
        #測定開始
        time.sleep(0.1)
        i2c.write_i2c_block_data(address, 0xAC, [0x33, 0x00])
        time.sleep(1)
        
        # ステータス確認ループ
        for _ in range(10):
            if (i2c.read_byte_data(0x38, 0x71) & 0x80) == 0:
                print("確認完了")
                break
            time.sleep(0.02)
            print("待機")

        
        #データ読み取り
        dat = i2c.read_i2c_block_data(address, 0x00, 7)
        
        print(dat)
        
        #データ格納
        hum = dat[1] << 12 | dat[2] << 4 | ((dat[3] & 0xF0) >> 4)
        tmp = ((dat[3] & 0x0F) << 16) | dat[4] << 8 | dat[5]
      
        #湿度変換  
        hum = hum / 2**20 * 100
        #温度変換
        tmp = tmp / 2**20 * 200 - 50
        
        print("湿度（しつど）: " + str(hum) + "%")
        print("温度（おんど）: " + str(tmp) + "℃")
        
        time.sleep(2) 

except KeyboardInterrupt:
    pass