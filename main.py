import schedule
from app import create_app, socketio

from threading import Thread
# from multiprocessing import Process
import time
from app.controller.socket import socketrun1second


def scheduled_job():
    try:
        schedule.every(1).minute.do(socketrun1second)

        while True:
            print("asd12")
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting the loop.")


app = create_app()

Thread(target=scheduled_job).start()
Thread(target=socketio.run(app, debug=True)).start()

# import time

# # def func1():
# #     while True:
# #         print('Working')
# #         time.sleep(10)

# # def func2():
# #     while True:
# #         print('Workin2')
# #         time.sleep(1)

# # if __name__ == '__main__':
# #     Thread(target = func1).start()
# #     Thread(target = func2).start()