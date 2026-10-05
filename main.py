from pygame_ui import PygameUI


def main():
    interface = PygameUI()

    while not interface.quit:
        interface.update()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
