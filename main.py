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
    # TODO: Handle keys switching states, not updating every loop.
    # TODO: Send API request to Sheets based on button data.
    # TODO: Handle cases where a key was pressed too quickly after another/simultaneously with another.
    if key_state[LED_KEY]:
        led.on()
    else:
        led.off()


def main():
    global enabled
    # TODO: Don't do this. Record every n ms instead of looping continuously for the sake of energy/heat.
    while enabled:
        handle_key_presses()
        handle_key_states()
        continue


if __name__ == "__main__":
    main()
