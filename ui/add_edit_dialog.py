import tkinter as tk
from tkinter import ttk, messagebox
from models.password_entry import PasswordEntry
from datetime import datetime

BG       = '#0d0d18'
SURFACE  = '#161628'
SURFACE2 = '#1e1e35'
ACCENT   = '#7c5cfc'
SUCCESS  = '#10b981'
DANGER   = '#ef4444'
INFO     = '#3b82f6'
FG       = '#e8e8f0'
FG_DIM   = '#6b7280'
FG_LABEL = '#a5b4fc'
FONT     = 'Segoe UI'


class AddEditDialog:
    def __init__(self, parent, database, crypto, entry=None):
        self.parent = parent
        self.db = database
        self.crypto = crypto
        self.entry = entry
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title('Edit Entry' if entry else 'Add New Entry')
        self.dialog.geometry('540x580')
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_ui()
        if entry:
            self._load_entry()

        self.dialog.bind('<Return>', lambda e: self._save())

    def _field(self, parent, label_text, show=None):
        tk.Label(parent, text=label_text, bg=BG, fg=FG_LABEL,
                 font=(FONT, 9, 'bold')).pack(anchor='w', pady=(10, 3))

        wrap = tk.Frame(parent, bg=SURFACE2, highlightthickness=1,
                        highlightbackground=SURFACE2, highlightcolor=ACCENT)
        wrap.pack(fill='x')

        kwargs = dict(bg=SURFACE2, fg=FG, insertbackground=ACCENT,
                      font=(FONT, 11), relief='flat', highlightthickness=0)
        if show is not None:
            kwargs['show'] = show

        entry = tk.Entry(wrap, **kwargs)
        entry.pack(fill='x', padx=10, pady=8)
        entry.bind('<FocusIn>',  lambda e: wrap.config(highlightbackground=ACCENT))
        entry.bind('<FocusOut>', lambda e: wrap.config(highlightbackground=SURFACE2))
        return entry

    def _build_ui(self):
        header = tk.Frame(self.dialog, bg=SURFACE2, height=52)
        header.pack(fill='x')
        header.pack_propagate(False)
        title = 'Edit Entry' if self.entry else 'New Password Entry'
        tk.Label(header, text=title, font=(FONT, 14, 'bold'),
                 bg=SURFACE2, fg=FG).pack(side='left', padx=20, pady=12)

        body = tk.Frame(self.dialog, bg=BG)
        body.pack(fill='both', expand=True, padx=28, pady=16)

        self.platform_entry = self._field(body, 'PLATFORM *')

        self.username_entry = self._field(body, 'USERNAME *')

        tk.Label(body, text='PASSWORD *', bg=BG, fg=FG_LABEL,
                 font=(FONT, 9, 'bold')).pack(anchor='w', pady=(10, 3))

        pw_wrap = tk.Frame(body, bg=SURFACE2, highlightthickness=1,
                           highlightbackground=SURFACE2, highlightcolor=ACCENT)
        pw_wrap.pack(fill='x')

        self.password_entry = tk.Entry(pw_wrap, bg=SURFACE2, fg=FG,
                                       insertbackground=ACCENT,
                                       font=(FONT, 11), show='*',
                                       relief='flat', highlightthickness=0)
        self.password_entry.pack(side='left', fill='x', expand=True, padx=10, pady=8)
        self.password_entry.bind('<FocusIn>',  lambda e: pw_wrap.config(highlightbackground=ACCENT))
        self.password_entry.bind('<FocusOut>', lambda e: pw_wrap.config(highlightbackground=SURFACE2))

        gen_btn = tk.Button(pw_wrap, text='Generate', command=self._generate,
                            bg=INFO, fg='white', font=(FONT, 9, 'bold'),
                            relief='flat', cursor='hand2', padx=12, pady=4)
        gen_btn.pack(side='right', padx=6)

        tk.Label(body, text='CATEGORY', bg=BG, fg=FG_LABEL,
                 font=(FONT, 9, 'bold')).pack(anchor='w', pady=(10, 3))
        categories = self.db.get_categories()
        self.category_var = tk.StringVar(value='General')
        self.category_combo = ttk.Combobox(body, textvariable=self.category_var,
                                           values=['General'] + categories,
                                           font=(FONT, 10), state='readonly')
        self.category_combo.pack(fill='x')

        tk.Label(body, text='NOTES', bg=BG, fg=FG_LABEL,
                 font=(FONT, 9, 'bold')).pack(anchor='w', pady=(10, 3))
        notes_wrap = tk.Frame(body, bg=SURFACE2, highlightthickness=1,
                              highlightbackground=SURFACE2, highlightcolor=ACCENT)
        notes_wrap.pack(fill='x')
        self.notes_text = tk.Text(notes_wrap, height=4, bg=SURFACE2, fg=FG,
                                  font=(FONT, 10), wrap='word',
                                  relief='flat', highlightthickness=0,
                                  padx=10, pady=8)
        self.notes_text.pack(fill='x')
        self.notes_text.bind('<FocusIn>',  lambda e: notes_wrap.config(highlightbackground=ACCENT))
        self.notes_text.bind('<FocusOut>', lambda e: notes_wrap.config(highlightbackground=SURFACE2))

        footer = tk.Frame(self.dialog, bg=SURFACE2, height=60)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)

        cancel_btn = tk.Button(footer, text='Cancel', command=self.dialog.destroy,
                               bg=SURFACE, fg=FG_DIM, font=(FONT, 10),
                               relief='flat', cursor='hand2', padx=20, pady=6,
                               activebackground=SURFACE, activeforeground=FG)
        cancel_btn.pack(side='right', padx=(0, 14), pady=12)

        save_btn = tk.Button(footer, text='Save Entry', command=self._save,
                             bg=SUCCESS, fg='white', font=(FONT, 10, 'bold'),
                             relief='flat', cursor='hand2', padx=22, pady=6,
                             activebackground=SUCCESS, activeforeground='white')
        save_btn.pack(side='right', padx=(0, 6), pady=12)

    def _load_entry(self):
        self.platform_entry.insert(0, self.entry.platform)
        self.username_entry.insert(0, self.entry.username)
        self.password_entry.insert(0, self.crypto.decrypt(self.entry.encrypted_password))
        self.category_var.set(self.entry.category)
        self.notes_text.insert('1.0', self.entry.notes)

    def _generate(self):
        password = self.crypto.generate_strong_password(18)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def _save(self):
        platform = self.platform_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        category = self.category_var.get()
        notes    = self.notes_text.get('1.0', tk.END).strip()

        if not platform or not username or not password:
            messagebox.showwarning('Missing Fields',
                                   'Platform, username, and password are required.')
            return

        if self.entry:
            self.entry.platform           = platform
            self.entry.username           = username
            self.entry.encrypted_password = self.crypto.encrypt(password)
            self.entry.category           = category
            self.entry.notes              = notes
            self.entry.updated_at         = datetime.now().isoformat()
            self.db.update(self.entry)
        else:
            new_entry       = PasswordEntry(platform, username,
                                            self.crypto.encrypt(password), category)
            new_entry.notes = notes
            self.db.add(new_entry)

        self.result = True
        self.dialog.destroy()
