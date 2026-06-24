# 🔐 Vault — Password Manager

A secure, modern password manager built with Python. All your passwords encrypted locally — no cloud, no tracking.

## Features

- AES-256 encryption for all stored passwords
- Master password protection with SHA-256 hashing
- Add, edit, and delete password entries
- Categorize and filter passwords
- Search across platform, username, category, and notes
- One-click copy to clipboard with auto-hide after 10 seconds
- Strong password generator (18 characters)
- Automatic backup before every save
- Auto update checker on launch

## Installation

```bash
git clone https://github.com/bulutkocak/Vault-Password-Manager.git
cd Vault-Password-Manager
pip install -r requirements.txt
python main.py
```

## Building the Executable

```bash
pyinstaller --onefile --windowed --name="Vault-Manager" --icon="icon.ico" --add-data "version.txt;." main.py
```

The built `.exe` will appear in the `dist/` folder.

## Usage

- **First run:** Set your master password — there is no recovery option, don't forget it
- **Add:** Click `＋ Add` → Fill in details → Save
- **Copy password:** Select an entry → Click `⎘ Copy Password` (auto-hides after 10s)
- **Edit:** Select an entry → Click `✎ Edit` → Modify → Save
- **Delete:** Select an entry → Click `✕ Delete` → Confirm

## Security

- Passwords encrypted with AES-256
- Master password hashed with SHA-256 — never stored in plain text
- 3 failed login attempts closes the application
- All data stored locally — never leaves your machine

## Data Location

Passwords are stored locally on your computer:

| OS | Path |
|----|------|
| Windows | `C:\Users\[Username]\AppData\Roaming\Vault-Pass\vault.json` |
| Linux | `/home/[Username]/.config/Vault-Pass/vault.json` |
| macOS | `/Users/[Username]/Library/Application Support/Vault-Pass/vault.json` |

A backup is automatically saved as `vault.bak.json` in the same folder on every write.

## Requirements

- Python 3.8+
- `cryptography`
- `pyperclip`

## License

MIT
