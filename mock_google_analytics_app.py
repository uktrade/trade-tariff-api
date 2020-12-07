from gevent import monkey  # noqa: E402  #  pylint: disable=C0411, C0412, C0413

monkey.patch_all()  # noqa: E402  # pylint: disable=C0411, C0413

import signal

from flask import Flask
import gevent
from gevent.pywsgi import WSGIServer


def google_analytics_app():

    calls = 0

    def start():
        server.serve_forever()

    def stop():
        server.stop()

    def _store():
        nonlocal calls
        calls += 1
        return 'OK'

    def _calls():
        nonlocal calls
        last_calls = calls
        calls = 0
        return str(last_calls)

    app = Flask('app')

    app.add_url_rule('/collect', methods=['POST'], view_func=_store)

    app.add_url_rule('/calls', methods=['POST'], view_func=_calls)

    server = WSGIServer(('0.0.0.0', 9002), app, log=app.logger)

    return start, stop


def main():

    start, stop = google_analytics_app()

    gevent.signal_handler(signal.SIGTERM, stop)
    start()
    gevent.get_hub().join()


if __name__ == '__main__':
    main()
