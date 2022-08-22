import os, importlib,time
import raspi_update
import raspi_dcbot

base_path = os.path.dirname(os.path.abspath(__file__))
dcbot_path = base_path + '/raspi_dcbot.py'

while True:
    os.system('cls||clear')
    importlib.reload(raspi_update)
    raspi_update.update()

    os.system('cls||clear')
    importlib.reload(raspi_dcbot)
    print('discord bot connect...')
    raspi_dcbot.run()

    os.system('cls||clear')
    print('discord bot stop!')

    time.sleep(60)

    importlib.reload(raspi_update)
    raspi_update.update()
    break
