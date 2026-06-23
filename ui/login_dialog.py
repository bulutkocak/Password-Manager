import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import json

BG       = '#0d0d18'
SURFACE  = '#161628'
SURFACE2 = '#1e1e35'
ACCENT   = '#7c5cfc'
ACCENT2  = '#e94560'
SUCCESS  = '#10b981'
FG       = '#e8e8f0'
FG_DIM   = '#6b7280'
FG_LABEL = '#a5b4fc'
FONT     = 'Segoe UI'


class LoginDialog:
    def __init__(self):
        self.dialog = tk.Tk()
        self.dialog.title('Vault — Secure Password Manager')
        self.dialog.geometry('440x540')
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=BG)
        self.dialog.eval('tk::PlaceWindow . center')

        self.password       = None
        self.login_attempts = 0
        self.max_attempts   = 3

        self.master_hash_file = os.path.join(
            os.environ['APPDATA'], 'PasswordManager', 'master.hash')
        self.is_first_run = not os.path.exists(self.master_hash_file)

        self._build_ui()
        self.dialog.protocol('WM_DELETE_WINDOW', self.dialog.quit)

    def _build_ui(self):
        outer = tk.Frame(self.dialog, bg=BG)
        outer.pack(fill='both', expand=True, padx=44, pady=36)

        logo_frame = tk.Frame(outer, bg=BG)
        logo_frame.pack(pady=(0, 28))

        tk.Label(logo_frame, text='🔐', font=(FONT, 38), bg=BG).pack()
        tk.Label(logo_frame, text='Vault', font=(FONT, 26, 'bold'),
                 bg=BG, fg=FG).pack()
        tk.Label(logo_frame, text='Secure Password Manager', font=(FONT, 10),
                 bg=BG, fg=FG_DIM).pack(pady=(2, 0))

        if self.is_first_run:
            pill = tk.Frame(outer, bg='#10b98122')
            pill.pack(fill='x', pady=(0, 16))
            tk.Label(pill, text='✦  First run — set your master password',
                     font=(FONT, 9), bg='#10b98122', fg=SUCCESS,
                     pady=8).pack()

        tk.Label(outer, text='MASTER PASSWORD', font=(FONT, 9, 'bold'),
                 bg=BG, fg=FG_LABEL).pack(anchor='w', pady=(0, 6))

        pw_wrap = tk.Frame(outer, bg=SURFACE2, highlightthickness=2,
                           highlightbackground=SURFACE2, highlightcolor=ACCENT)
        pw_wrap.pack(fill='x')

        self.password_entry = tk.Entry(pw_wrap, show='*', width=28,
                                       bg=SURFACE2, fg=FG,
                                       insertbackground=ACCENT,
                                       font=(FONT, 14), relief='flat',
                                       highlightthickness=0)
        self.password_entry.pack(padx=14, pady=13)
        self.password_entry.bind('<FocusIn>',  lambda e: pw_wrap.config(highlightbackground=ACCENT))
        self.password_entry.bind('<FocusOut>', lambda e: pw_wrap.config(highlightbackground=SURFACE2))
        self.password_entry.bind('<Return>', lambda e: self._login())
        self.password_entry.focus()

        toggle_row = tk.Frame(outer, bg=BG)
        toggle_row.pack(fill='x', pady=(10, 0))
        self.show_var = tk.IntVar()
        tk.Checkbutton(toggle_row, text='Show password', variable=self.show_var,
                       command=self._toggle_show, bg=BG, fg=FG_DIM,
                       selectcolor=BG, activebackground=BG, activeforeground=FG_DIM,
                       font=(FONT, 9), relief='flat', cursor='hand2').pack(side='left')

        self.error_label = tk.Label(outer, text='', font=(FONT, 9),
                                    bg=BG, fg='#ef4444', wraplength=300)
        self.error_label.pack(pady=(14, 0))

        login_btn = tk.Button(outer, text='Unlock Vault',
                              command=self._login,
                              bg=ACCENT, fg='#ffffff',
                              font=(FONT, 13, 'bold'),
                              relief='flat', cursor='hand2',
                              activebackground=ACCENT, activeforeground='#ffffff',
                              pady=12)
        login_btn.pack(fill='x', pady=(8, 0))

        footer = tk.Frame(outer, bg=BG)
        footer.pack(side='bottom', fill='x', pady=(24, 0))
        hint = ('Remember this password — there is no recovery option.' if self.is_first_run
                else 'All entries are end-to-end encrypted.')
        tk.Label(footer, text=hint, font=(FONT, 8), bg=BG, fg=FG_DIM,
                 wraplength=300).pack()

    def _toggle_show(self):
        self.password_entry.config(show='' if self.show_var.get() else '*')

    def _login(self):
        password = self.password_entry.get()

        if not password:
            self._show_error('Please enter your master password.')
            return

        if self.is_first_run:
            if len(password) < 4:
                self._show_error('Password must be at least 4 characters.')
                return
            os.makedirs(os.path.dirname(self.master_hash_file), exist_ok=True)
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            with open(self.master_hash_file, 'w') as f:
                json.dump({'hash': pw_hash}, f)
            self.password = password
            self.dialog.quit()
            self.dialog.destroy()
            return

        try:
            with open(self.master_hash_file, 'r') as f:
                stored_hash = json.load(f).get('hash')
        except Exception:
            self._show_error('Could not read the master password file.')
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest()

        if pw_hash == stored_hash:
            self.password = password
            self.dialog.quit()
            self.dialog.destroy()
        else:
            self.login_attempts += 1
            remaining = self.max_attempts - self.login_attempts
            if remaining <= 0:
                messagebox.showerror('Locked', 'Too many failed attempts. The application will close.')
                self.dialog.quit()
                self.dialog.destroy()
                return
            self._show_error(f'Incorrect password. {remaining} attempt{"s" if remaining != 1 else ""} remaining.')
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def _show_error(self, message):
        self.error_label.config(text=f'⚠  {message}')
        self.dialog.after(4000, lambda: self.error_label.config(text=''))

    def run(self):
        self.dialog.mainloop()
        return self.password
