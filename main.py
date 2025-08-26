import json
import logging
import time

import qbittorrentapi
import schedule


logging.basicConfig(
    filename="qbit-issue-tracker.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)


class QbitIssueHandler:
    def __init__(self, **conn_info):
        self.qbt_client = qbittorrentapi.Client(**conn_info)

    def tag_torrents_with_issues(self):
        tag_count = 0
        removed_count = 0

        logging.info("Started checking for issues")
        for torrent in self.qbt_client.torrents_info():
            for tracker in torrent.trackers:
                if tracker.status == 4 and "issue" in torrent.tags:
                    # Tracker has been contacted, but it is not working (or doesn't send proper replies)
                    torrent.setTags("issue")
                    logging.debug(f"{torrent.name} - {torrent.hash} tagged with issue")
                    tag_count += 1
                elif tracker.status == 2 and "issue" in torrent.tags:
                    # Tracker is working again so remove the issue tag
                    torrent.remove_tags("issue")
                    logging.debug(f"{torrent.name} - {torrent.hash} issue tag removed")
                    removed_count += 1
        logging.info(
            f"Finished. Tagged {tag_count} torrents and removed {removed_count} tags from torrents"
        )

    def qbit_logout(self):
        self.qbt_client.auth_log_out()


def get_login_data(filename: str) -> dict:
    with open(filename) as f:
        return json.loads(f.read())


def job():
    conn_info = get_login_data("/config/config.json")

    ih = QbitIssueHandler(**conn_info)
    ih.tag_torrents_with_issues()
    ih.qbit_logout()


def main():
    job()

    schedule.every(24).hours.do(job)
    while True:
        schedule.run_pending()
        time.sleep(60 * 60)  # check every hour


if __name__ == "__main__":
    main()
