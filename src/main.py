from tracker import Tracker
from app import App

def main():

    # New Tracker object
    tracker = Tracker()

    # This starts the routine
    app = App(tracker)
    app.loop_gui()

if __name__ == '__main__':
    main()