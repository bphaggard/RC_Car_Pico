from dcmotor import DCMotor
from machine import Pin, PWM, UART
from time import sleep

frequency = 1000

pin1 = Pin(3, Pin.OUT)
pin2 = Pin(4, Pin.OUT)
pin3 = Pin(7, Pin.OUT)
pin4 = Pin(8, Pin.OUT)
enable1 = PWM(Pin(2), frequency)
enable2 = PWM(Pin(6), frequency)

dc_motors = DCMotor(pin1, pin2, pin3, pin4, enable1, enable2)

# Initialize LED on pin 13
leds = Pin(13, Pin.OUT)

# Set min duty cycle (15000) and max duty cycle (65535) 
#dc_motor = DCMotor(pin1, pin2, enable, 15000, 65535)

# Initialize UART0
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Initialize PWM on pin 16 for servo control
servo = PWM(Pin(16))
servo.freq(50)  # Set PWM frequency to 50Hz, common for servo motors

def interval_mapping(x, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another.
    This function is useful for converting servo angle to pulse width.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_write(pin, angle):
    """
    Moves the servo to a specific angle.
    The angle is converted to a suitable duty cycle for the PWM signal.
    """
    pulse_width = interval_mapping(
        angle, 0, 180, 0.5, 2.5
    )  # Map angle to pulse width in ms
    duty = int(
        interval_mapping(pulse_width, 0, 20, 0, 65535)
    )  # Map pulse width to duty cycle
    pin.duty_u16(duty)  # Set PWM duty cycle
        
def parse_command(command):
    # Strip whitespace and newline characters
    cmd = command.strip()
    
    if cmd == "dc:motor.forward":
        dc_motors.forward(100)
    elif cmd == "dc:motor.backward":
        dc_motors.backwards(100)
    elif cmd == "dc:motor.stop":
        dc_motors.stop()
    elif cmd == "servo.left":
        servo_write(servo, 71)
    elif cmd == "servo.center":
        servo_write(servo, 85)
    elif cmd == "servo.right":
        servo_write(servo, 99)
    elif cmd == "lights.on":
        leds.value(1)
    elif cmd == "lights.off":
        leds.value(0)
    else:
        print("Unknown command:", cmd)

# Main loop
while True:
    if uart.any():
        received = uart.readline()  # Read entire line
        try:
            cmd_str = received.decode('utf-8')
            print("Received:", cmd_str)
            parse_command(cmd_str)
        except Exception as e:
            print("Error decoding:", e)

    sleep(0.1)
