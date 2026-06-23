# 🔐 Password Manager

A secure password manager built with Python to store and manage all your passwords safely.

## Features

- AES-256 encryption
- Master password protection
- Add, edit, delete passwords
- Categorize passwords
- Search and filter
- Copy passwords to clipboard
- Strong password generator

## Installation

```bash
# Clone the repository
git clone https://github.com/bulutkocak/Password-Manager.git
cd Password-Manager

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Usage

- First run: Set your master password
- Add: Click "Add New" -> Fill in details -> Save
- View: Select password -> Click "Show & Copy"
- Edit: Select -> Click "Edit" -> Modify -> Save
- Delete: Select -> Click "Delete" -> Confirm

## Security

- AES-256 encryption
- SHA-256 master password hashing
- 3 failed attempts = program closes

## Saved Passwords Location

Passwords are stored locally in your computer:

```
Windows: C:\Users\[Username]\AppData\Roaming\PasswordManager\
Linux:   /home/[Username]/.config/PasswordManager/
macOS:   /Users/[Username]/Library/Application Support/PasswordManager/
```

## Requirements

- Python 3.8+
- cryptography
- pyperclip

## License

MIT
