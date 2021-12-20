import keyboard
from gpiozero import LED

led = LED(17)
LED_KEY = "1"
ESC = "esc"
enabled = True

key_state = {
    LED_KEY: False,
}


def handle_key_presses():
    global enabled
    if keyboard.is_pressed(ESC):
        enabled = False
        return
    for key in key_state:
        key_state[key] = keyboard.is_pressed(key)


def handle_key_states():
    if key_state[LED_KEY]:
        led.on()
    else:
        led.off()


def main():
    global enabled
    while enabled:
        handle_key_presses()
        handle_key_states()
        continue


if __name__ == "__main__":
    main()
