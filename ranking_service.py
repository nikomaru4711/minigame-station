from queue import Empty, Queue
from threading import Thread

from firebase_config import COLLECTIONS


class RankingService:
    """通信は専用スレッド、画面用データの更新はpollを呼ぶメインスレッドで行う。"""

    def __init__(self, client):
        self.client = client
        self.rankings = {category: [] for category in COLLECTIONS}
        self.status = {category: "" if client.enabled else "Firebase未設定" for category in COLLECTIONS}
        self.pending = {}
        self.jobs, self.results = Queue(), Queue()
        self.worker = None

    def _enqueue(self, action, payload):
        self.jobs.put((action, payload))
        if self.worker is None:
            self.worker = Thread(target=self._work, daemon=True, name="firestore-rankings")
            self.worker.start()

    def _work(self):
        while True:
            action, payload = self.jobs.get()
            try:
                if action == "submit":
                    self.client.submit(*payload)
                entries = self.client.fetch(payload[0])
                self.results.put((action, payload, entries, False))
            except Exception:
                # 認証トークンやAPIキーを画面やログに出さない。
                self.results.put((action, payload, None, True))
            finally:
                self.jobs.task_done()

    def submit(self, category, player_id, name, score):
        if not self.client.enabled:
            return
        job = (category, player_id, name, score)
        current = self.pending.get(category)
        if current is None or score > current[3]:
            self.pending[category] = job
        self.status[category] = "記録を送信中…"
        self._enqueue("submit", job)

    def refresh(self, category):
        if not self.client.enabled:
            return
        self.status[category] = "読み込み中…"
        self._enqueue("fetch", (category,))

    def retry_pending(self):
        for job in list(self.pending.values()):
            self._enqueue("submit", job)

    def poll(self):
        while True:
            try:
                action, payload, entries, failed = self.results.get_nowait()
            except Empty:
                return
            category = payload[0]
            if failed:
                self.status[category] = "通信失敗：更新ボタンで再試行"
            else:
                self.rankings[category] = entries
                if action == "submit" and self.pending.get(category) == payload:
                    del self.pending[category]
                self.status[category] = "未送信の記録あり：更新で再試行" if category in self.pending else ""
