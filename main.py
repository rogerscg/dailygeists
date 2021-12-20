from pynput.keyboard import Key, Listener
from gpiozero import LED

led = LED(17)
LED_KEY = "1"


def on_press(key):
    if key != LED_KEY:
        return True
    print('{0} pressed'.format(key))
    led.on()


def on_release(key):
    if key == Key.esc:
        # Stop listener
        led.off()
        return False
    if key != LED_KEY:
        return True
    print('{0} release'.format(key))
    led.off()


def main():
    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
