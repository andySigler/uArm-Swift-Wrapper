import random
import time

from pythonosc import udp_client


if __name__ == "__main__":

    port = 8008

    client = udp_client.SimpleUDPClient('127.0.0.1', 5005)

    while True:
        r_pos = [random.randint(0, 100) for _ in 'xyz']
        client.send_message("/move_to", [port] + r_pos)
        time.sleep(1)
        client.send_message("/position", [port])
        time.sleep(1)
        client.send_message("/port", [port])
        time.sleep(1)
        client.send_message("/speed", [port])
        time.sleep(1)
