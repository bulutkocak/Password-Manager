import json
import os
import shutil
from datetime import datetime
from models.password_entry import PasswordEntry

APP_NAME  = 'Vault-Pass'
DATA_DIR  = os.path.join(os.environ['APPDATA'], APP_NAME)
DATA_FILE = os.path.join(DATA_DIR, 'vault.json')
BAK_FILE  = os.path.join(DATA_DIR, 'vault.bak.json')


class Database:
    def __init__(self, master_password):
        self.master_password = master_password
        self.data_dir        = DATA_DIR
        self.data_file       = DATA_FILE
        self.entries: list[PasswordEntry] = []
        self._ensure_directory()
        self._load()

    def _ensure_directory(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load(self):
        if not os.path.exists(self.data_file):
            self.entries = []
            self._save()
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            self.entries = [PasswordEntry.from_dict(item) for item in payload.get('entries', [])]
        except Exception:
            self.entries = []

    def _save(self):
        if os.path.exists(self.data_file):
            shutil.copy2(self.data_file, BAK_FILE)
        payload = {
            'app':      APP_NAME,
            'version':  1,
            'saved_at': datetime.now().isoformat(),
            'entries':  [e.to_dict() for e in self.entries],
        }
        tmp = self.data_file + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.data_file)

    def get_all(self) -> list[PasswordEntry]:
        return sorted(self.entries, key=lambda e: e.platform.lower())

    def search(self, term: str) -> list[PasswordEntry]:
        if not term:
            return self.get_all()
        t = term.lower()
        return sorted(
            [e for e in self.entries
             if t in e.platform.lower() or t in e.username.lower()
             or t in (e.category or '').lower() or t in (e.notes or '').lower()],
            key=lambda e: e.platform.lower()
        )

    def get_categories(self) -> list[str]:
        return sorted({e.category for e in self.entries if e.category})

    def add(self, entry: PasswordEntry) -> None:
        self.entries.append(entry)
        self._save()

    def update(self, entry: PasswordEntry) -> bool:
        for i, e in enumerate(self.entries):
            if e.id == entry.id:
                self.entries[i] = entry
                self._save()
                return True
        return False

    def delete(self, entry_id: str) -> bool:
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.id != entry_id]
        if len(self.entries) < before:
            self._save()
            return True
        return False

    def reset_all_data(self) -> None:
        self.entries = []
        for path in (self.data_file, BAK_FILE):
            if os.path.exists(path):
                os.remove(path)
        self._save()
