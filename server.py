from git import Repo
from rich import print
import json
import arrow

import subprocess

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

MESSAGES_REPO = "/Users/abassett/Projects/gitchat-messages/"

repo = Repo(MESSAGES_REPO)


class DashboardHandler(tornado.websocket.WebSocketHandler):

    connected_clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        print("Client connected")
        self.write_message(DashboardHandler.get_recent_messages())
        DashboardHandler.connected_clients.add(self)

    def on_close(self):
        print("Client disconnected")
        DashboardHandler.connected_clients.remove(self)

    def on_message(self, message):
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", message], cwd=MESSAGES_REPO
        )
        repo.remotes.origin.push()

    @classmethod
    def get_recent_messages(cls):
        return json.dumps(
            [
                {
                    "hash": str(x),
                    "author": str(x.author),
                    "authored_on": arrow.get(x.authored_datetime).humanize(),
                    "message": x.message,
                }
                for x in list(repo.iter_commits("main", max_count=500))
            ]
        )

    @classmethod
    def send_updates(cls, chat_message):
        for connected_client in cls.connected_clients:
            connected_client.write_message(chat_message)


def fetch_chat_messages():
    repo.remotes.origin.pull()
    DashboardHandler.send_updates(DashboardHandler.get_recent_messages())


if __name__ == "__main__":
    application = tornado.web.Application(
        [
            (r"/chat", DashboardHandler),
        ]
    )

    http_server = tornado.httpserver.HTTPServer(application)
    fetch_chat_job = tornado.ioloop.PeriodicCallback(fetch_chat_messages, 1000, 0.1)
    fetch_chat_job.start()
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()