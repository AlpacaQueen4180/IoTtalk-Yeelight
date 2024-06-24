from miio.integrations.light.yeelight.yeelight import Yeelight
import DAN
import time
import datetime

lamp = Yeelight("IP", "YourToken")

def iottalk_setup():
    DAN.profile['dm_name'] = "MiLamp2"
    DAN.profile['df_list'] = ["Brightness", "Color-Temperature", "Target-Brightness", "CT-Mode", "Brightness-Mode", "Manual-Brightness"]
    DAN.profile['d_name'] = "alpaca.MiLamp2"

    DAN.device_registration_with_retry("https://4.iottalk.tw")

def blink(light: Yeelight):
    light.off()
    time.sleep(0.5)
    light.on()
    time.sleep(0.5)
    light.off()

if __name__ == "__main__":
    iottalk_setup()
    blink(lamp)
    target = 0
    margin = 5
    step = 3
    last_brightness = 0
    current_brightness = 0
    ct_mode = 0
    last_hour = 0
    brightest_time = 9
    brightness_mode = 0

    try:
        while True:
            ct_mode_pull = DAN.pull("CT-Mode")
            if ct_mode_pull:
                ct_mode = ct_mode_pull[0]
                ct_mode = 1 if ct_mode else 0
                print(f"Mode: {ct_mode}")
            
            brightness_mode_pull = DAN.pull("Brightness-Mode")
            if brightness_mode_pull:
                brightness_mode = brightness_mode_pull[0]
                brightness_mode = 1 if brightness_mode else 0
                print(f"Mode: {brightness_mode}")

            target_pull = DAN.pull("Target-Brightness")
            if target_pull:
                target = target_pull[0] + 10
                print(f"Target: {target}")

            if brightness_mode == 0: # auto
                
                br = DAN.pull("Brightness")
                if br is not None:
                    br = br[0]
                    print(f"Get brightness: {br}") 

                    if br < target - margin:
                        current_brightness += step
                    elif br > target + margin:
                        current_brightness -= step
                    current_brightness = max(0, min(100, current_brightness))

                    if last_brightness != current_brightness:

                        print(f"Set brightness: {current_brightness}")

                        if current_brightness < 1:
                            lamp.off()
                        else:
                            lamp.on()
                            lamp.set_brightness(int(current_brightness))
                        last_brightness = current_brightness

            else: # manual
                br = DAN.pull("Manual-Brightness")
                if br:
                    br = br[0]
                
                    print(f"Set brightness: {br}")

                    if br < 1:
                        lamp.off()
                    else:
                        lamp.on()
                        lamp.set_brightness(int(br))
                

            if ct_mode == 0: # auto
                now = datetime.datetime.now()
                hour = now.hour + (now.minute / 60)
                if last_hour != hour and lamp.status().is_on:
                    temp = abs(((hour - brightest_time) % 24) - 12)
                    shift = 3
                    temp = max(temp - shift, 0) / (12 - shift)
                    temp = (4800-2500) * temp + 2500
                    print(f"Auto CT: {temp}")
                    lamp.set_color_temp(temp)
                    last_hour = hour
            else:
                last_hour = 0
                temp = DAN.pull("Color-Temperature")
                if temp is not None:
                    temp = temp[0]
                    print(f"Color-Temperature: {temp}")
                    lamp.set_color_temp(temp)



        
    finally:
        DAN.deregister()
        lamp.off()



