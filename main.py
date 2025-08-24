import qbittorrentapi
import json


class QbitIssueHandler:
    def __init__(self, **conn_info):
        self.qbt_client = qbittorrentapi.Client(**conn_info)

    def tag_torrents_with_issues(self):
        for torrent in self.qbt_client.torrents_info():
            for tracker in torrent.trackers:
                if tracker.status == 4:
                    # Tracker has been contacted, but it is not working (or doesn't send proper replies)
                    torrent.setTags("issue")
                elif tracker.status == 2 and "issue" in torrent.tags:
                    # Tracker is working again so remove the issue tag
                    torrent.remove_tags("issue")

    def qbit_logout(self):
        self.qbt_client.auth_log_out()

def get_login_data() -> dict:
    with open("login.json") as f:
        return json.loads(f.read())

def main():
    conn_info = get_login_data()

    ih = QbitIssueHandler(**conn_info)
    ih.tag_torrents_with_issues()
    ih.qbit_logout()

if __name__ == "__main__":
    main()
