import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import threading
import urllib.request
import webbrowser
import sys
import os
from crypto_helper import CryptoHelper
from ui.add_edit_dialog import AddEditDialog
from models.password_entry import PasswordEntry
from datetime import datetime

BG        = '#0d0d18'
SURFACE   = '#161628'
SURFACE2  = '#1e1e35'
ACCENT    = '#7c5cfc'
ACCENT2   = '#e94560'
SUCCESS   = '#10b981'
WARNING   = '#f59e0b'
DANGER    = '#ef4444'
INFO      = '#3b82f6'
FG        = '#e8e8f0'
FG_DIM    = '#6b7280'
FG_LABEL  = '#a5b4fc'
FONT      = 'Segoe UI'

def _get_current_version() -> str:
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(base, 'version.txt')) as f:
            return f.read().strip()
    except Exception:
        return '0.0.0'

CURRENT_VERSION = _get_current_version()
VERSION_URL     = 'https://raw.githubusercontent.com/bulutkocak/Vault-Password-Manager/refs/heads/main/version.txt'
RELEASES_BASE   = 'https://github.com/bulutkocak/Vault-Password-Manager/releases/tag'


class MainWindow:
    def __init__(self, master_password, database):
        self.master_password = master_password
        self.db = database
        self.crypto = CryptoHelper(master_password)
        self._selected_entry = None

        self.window = tk.Tk()
        self.window.title("Vault — Password Manager")
        self.window.geometry("1160x720")
        self.window.minsize(960, 620)
        self.window.configure(bg=BG)
        self.window.eval('tk::PlaceWindow . center')

        self._setup_styles()
        self._build_ui()
        self.load_entries()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.after(800, self._check_version_async)

    def _check_version_async(self):
        threading.Thread(target=self._fetch_version, daemon=True).start()

    def _fetch_version(self):
        try:
            with urllib.request.urlopen(VERSION_URL, timeout=5) as resp:
                latest = resp.read().decode().strip()
            self.window.after(0, lambda: self._apply_version_result(latest))
        except Exception:
            pass

    def _apply_version_result(self, latest: str):
        self._version_label.config(text=f'v{CURRENT_VERSION}')
        if self._parse_version(latest) > self._parse_version(CURRENT_VERSION):
            release_url = f'{RELEASES_BASE}/{latest}'
            self._version_label.config(fg=WARNING)
            self._version_label.bind('<Button-1>', lambda e: webbrowser.open(release_url))
            self._show_update_banner(latest, release_url)

    @staticmethod
    def _parse_version(v: str):
        try:
            return tuple(int(x) for x in v.strip().lstrip('v').split('.'))
        except Exception:
            return (0,)

    def _show_update_banner(self, latest: str, release_url: str):
        banner = tk.Frame(self._banner_slot, bg=WARNING, cursor='hand2')
        banner.pack(fill='x')

        inner = tk.Frame(banner, bg=WARNING)
        inner.pack(fill='x', padx=16, pady=7)

        def open_url(e=None):
            webbrowser.open(release_url)

        def dismiss(e=None):
            banner.destroy()
            return 'break'

        msg = tk.Label(inner,
                       text=f'⬆  New version available: v{latest}  —  click here to download',
                       font=(FONT, 9, 'bold'), bg=WARNING, fg='#000000',
                       cursor='hand2')
        msg.pack(side='left')
        msg.bind('<Button-1>', open_url)

        close_btn = tk.Button(inner, text='✕', command=dismiss,
                              bg=WARNING, fg='#000000', font=(FONT, 9, 'bold'),
                              relief='flat', cursor='hand2', padx=6,
                              activebackground=WARNING)
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', dismiss)

        banner.bind('<Button-1>', open_url)
        inner.bind('<Button-1>', open_url)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Vault.Treeview',
                        background=SURFACE,
                        foreground=FG,
                        fieldbackground=SURFACE,
                        borderwidth=0,
                        rowheight=34,
                        font=(FONT, 10))
        style.configure('Vault.Treeview.Heading',
                        background=SURFACE2,
                        foreground=FG_LABEL,
                        borderwidth=0,
                        relief='flat',
                        font=(FONT, 10, 'bold'))
        style.map('Vault.Treeview',
                  background=[('selected', ACCENT)],
                  foreground=[('selected', '#ffffff')])
        style.map('Vault.Treeview.Heading',
                  background=[('active', SURFACE)])

        style.configure('Vault.TCombobox',
                        background=SURFACE2,
                        foreground=FG,
                        fieldbackground=SURFACE2,
                        selectbackground=SURFACE2,
                        selectforeground=FG,
                        arrowcolor=FG_LABEL,
                        borderwidth=0)
        style.map('Vault.TCombobox',
                  fieldbackground=[('readonly', SURFACE2)],
                  background=[('readonly', SURFACE2)])

        style.configure('Vault.Vertical.TScrollbar',
                        background=SURFACE2,
                        troughcolor=SURFACE,
                        borderwidth=0,
                        arrowcolor=FG_DIM)

    def _btn(self, parent, text, command, color, **kwargs):
        b = tk.Button(parent, text=text, command=command,
                      bg=color, fg='#ffffff',
                      font=(FONT, 10, 'bold'),
                      relief='flat', cursor='hand2',
                      activebackground=color, activeforeground='#ffffff',
                      **kwargs)
        b.bind('<Enter>', lambda e: b.config(bg=self._lighten(color)))
        b.bind('<Leave>', lambda e: b.config(bg=color))
        return b

    @staticmethod
    def _lighten(hex_color):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r, g, b = min(255, r + 30), min(255, g + 30), min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'

    def _build_ui(self):
        root = tk.Frame(self.window, bg=BG)
        root.pack(fill='both', expand=True, padx=18, pady=16)

        self._build_header(root)

        self._banner_slot = tk.Frame(root, bg=BG)
        self._banner_slot.pack(fill='x', pady=(0, 2))

        self._build_toolbar(root)
        self._build_content(root)
        self._build_statusbar(root)

        self._update_categories()
        self._update_count()

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=BG, height=56)
        header.pack(fill='x', pady=(0, 12))
        header.pack_propagate(False)

        left = tk.Frame(header, bg=BG)
        left.pack(side='left', fill='y')

        tk.Label(left, text='🔐', font=(FONT, 20), bg=BG, fg=ACCENT).pack(side='left', padx=(0, 8))
        tk.Label(left, text='Vault', font=(FONT, 22, 'bold'), bg=BG, fg=FG).pack(side='left')
        tk.Label(left, text='Password Manager', font=(FONT, 11), bg=BG, fg=FG_DIM).pack(side='left', padx=(8, 0), pady=(4, 0))

        self._version_label = tk.Label(left, text='v…', font=(FONT, 8),
                                       bg=BG, fg=FG_DIM, cursor='hand2')
        self._version_label.pack(side='left', padx=(10, 0), pady=(6, 0))
        self._version_label.bind('<Button-1>', lambda e: webbrowser.open(f'{RELEASES_BASE}/{CURRENT_VERSION}'))

        right = tk.Frame(header, bg=BG)
        right.pack(side='right', fill='y')

        self.header_count = tk.Label(right, text='', font=(FONT, 9), bg=BG, fg=FG_DIM)
        self.header_count.pack(side='left', padx=(0, 18))

        self._btn(right, '⏻  Lock & Exit', self.on_close, ACCENT2, padx=16, pady=6).pack(side='left')

    def _build_toolbar(self, parent):
        bar = tk.Frame(parent, bg=SURFACE, height=52)
        bar.pack(fill='x', pady=(0, 12))
        bar.pack_propagate(False)

        inner = tk.Frame(bar, bg=SURFACE)
        inner.pack(fill='both', expand=True, padx=12)

        search_wrap = tk.Frame(inner, bg=SURFACE2, highlightthickness=1,
                               highlightbackground=SURFACE2, highlightcolor=ACCENT)
        search_wrap.pack(side='left', pady=10, ipady=1)

        tk.Label(search_wrap, text='⌕', font=(FONT, 13), bg=SURFACE2, fg=FG_DIM).pack(side='left', padx=(8, 2))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *a: self._filter_entries())
        search_field = tk.Entry(search_wrap, textvariable=self.search_var, width=22,
                                bg=SURFACE2, fg=FG, insertbackground=ACCENT,
                                font=(FONT, 10), relief='flat', highlightthickness=0)
        search_field.pack(side='left', pady=6, padx=(0, 10))
        search_field.bind('<FocusIn>',  lambda e: search_wrap.config(highlightbackground=ACCENT))
        search_field.bind('<FocusOut>', lambda e: search_wrap.config(highlightbackground=SURFACE2))

        tk.Frame(inner, bg=SURFACE2, width=1).pack(side='left', fill='y', pady=10, padx=8)

        tk.Label(inner, text='Category', font=(FONT, 9), bg=SURFACE, fg=FG_DIM).pack(side='left', padx=(0, 5))
        self.category_var = tk.StringVar(value='All')
        self.category_combo = ttk.Combobox(inner, textvariable=self.category_var,
                                           width=16, font=(FONT, 10),
                                           state='readonly', style='Vault.TCombobox')
        self.category_combo.pack(side='left')
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_entries())

        actions = tk.Frame(inner, bg=SURFACE)
        actions.pack(side='right')

        self._btn(actions, '＋ Add',    self.add_entry,      SUCCESS, padx=14, pady=5).pack(side='left', padx=3)
        self._btn(actions, '✎ Edit',    self.edit_entry,     INFO,    padx=14, pady=5).pack(side='left', padx=3)
        self._btn(actions, '✕ Delete',  self.delete_entry,   DANGER,  padx=14, pady=5).pack(side='left', padx=3)
        self._btn(actions, '↺ Reset',   self.reset_all_data, WARNING, padx=14, pady=5).pack(side='left', padx=3)

    def _build_content(self, parent):
        content = tk.Frame(parent, bg=BG)
        content.pack(fill='both', expand=True)

        list_panel = tk.Frame(content, bg=SURFACE)
        list_panel.pack(side='left', fill='both', expand=True, padx=(0, 8))

        cols = ('Platform', 'Username', 'Category', 'Created')
        self.tree = ttk.Treeview(list_panel, columns=cols, show='headings',
                                 style='Vault.Treeview')

        col_cfg = [('Platform', 190, 'w'), ('Username', 170, 'w'),
                   ('Category', 130, 'center'), ('Created', 120, 'center')]
        for col, w, anchor in col_cfg:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=anchor, stretch=col == 'Username')

        vsb = ttk.Scrollbar(list_panel, orient='vertical', command=self.tree.yview,
                             style='Vault.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        self.tree.tag_configure('odd',  background=SURFACE)
        self.tree.tag_configure('even', background=SURFACE2)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', lambda e: self.show_password())

        detail_panel = tk.Frame(content, bg=SURFACE, width=300)
        detail_panel.pack(side='right', fill='y')
        detail_panel.pack_propagate(False)

        dp_header = tk.Frame(detail_panel, bg=SURFACE2, height=42)
        dp_header.pack(fill='x')
        dp_header.pack_propagate(False)
        tk.Label(dp_header, text='Details', font=(FONT, 12, 'bold'),
                 bg=SURFACE2, fg=FG_LABEL).pack(side='left', padx=14, pady=10)

        self.detail_canvas = tk.Frame(detail_panel, bg=SURFACE)
        self.detail_canvas.pack(fill='both', expand=True, padx=14, pady=12)

        self._detail_rows = {}
        fields = [('Platform', '—'), ('Username', '—'), ('Password', '••••••••'),
                  ('Category', '—'), ('Notes', '—'), ('Created', '—'), ('Updated', '—')]

        for key, default in fields:
            tk.Label(self.detail_canvas, text=key.upper(),
                     font=(FONT, 8, 'bold'), bg=SURFACE, fg=FG_LABEL).pack(anchor='w', pady=(8, 1))
            val = tk.Label(self.detail_canvas, text=default,
                           font=(FONT, 10), bg=SURFACE, fg=FG,
                           wraplength=258, justify='left', anchor='w')
            val.pack(anchor='w')
            self._detail_rows[key] = val

        tk.Frame(detail_panel, bg=SURFACE2, height=1).pack(fill='x', padx=14)

        btn_area = tk.Frame(detail_panel, bg=SURFACE)
        btn_area.pack(fill='x', padx=14, pady=12)

        self._btn(btn_area, '⎘  Copy Password', self.show_password, ACCENT,
                  pady=9).pack(fill='x', pady=(0, 6))
        self._btn(btn_area, '✎  Edit Entry', self.edit_entry, INFO,
                  pady=9).pack(fill='x')

    def _build_statusbar(self, parent):
        bar = tk.Frame(parent, bg=BG, height=28)
        bar.pack(fill='x', pady=(10, 0))
        bar.pack_propagate(False)

        self.status_label = tk.Label(bar, text='Ready', font=(FONT, 9),
                                     bg=BG, fg=FG_DIM)
        self.status_label.pack(side='left')

        self.count_label = tk.Label(bar, text='', font=(FONT, 9),
                                    bg=BG, fg=FG_DIM)
        self.count_label.pack(side='right')

    def _update_count(self):
        count = len(self.db.get_all())
        text = f'{count} password{"s" if count != 1 else ""}'
        self.count_label.config(text=text)
        self.header_count.config(text=text)

    def load_entries(self, entries=None):
        self.tree.delete(*self.tree.get_children())
        if entries is None:
            entries = self.db.get_all()
        for i, entry in enumerate(entries):
            created = entry.created_at[:10] if entry.created_at else ''
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert('', 'end', values=(
                entry.platform, entry.username, entry.category, created
            ), tags=(entry.id, tag))

    def _filter_entries(self):
        search = self.search_var.get().strip()
        category = self.category_var.get()
        entries = self.db.search(search)
        if category != 'All':
            entries = [e for e in entries if e.category == category]
        self.load_entries(entries)
        self._update_count()

    def _update_categories(self):
        categories = self.db.get_categories()
        self.category_combo['values'] = ['All'] + categories
        self.category_var.set('All')

    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            self._clear_details()
            return
        item = self.tree.item(selection[0])
        entry_id = item['tags'][0]
        entries = [e for e in self.db.get_all() if e.id == entry_id]
        if entries:
            self._selected_entry = entries[0]
            self._display_details(entries[0])

    def _clear_details(self):
        self._selected_entry = None
        placeholders = {'Platform': '—', 'Username': '—', 'Password': '••••••••',
                        'Category': '—', 'Notes': '—', 'Created': '—', 'Updated': '—'}
        for key, val in placeholders.items():
            self._detail_rows[key].config(text=val, fg=FG)

    def _display_details(self, entry, show_password=False):
        pw = self.crypto.decrypt(entry.encrypted_password) if show_password else '••••••••'
        self._detail_rows['Platform'].config(text=entry.platform, fg=FG)
        self._detail_rows['Username'].config(text=entry.username, fg=FG)
        self._detail_rows['Password'].config(text=pw, fg=SUCCESS if show_password else FG)
        self._detail_rows['Category'].config(text=entry.category, fg=FG)
        self._detail_rows['Notes'].config(text=entry.notes or '—', fg=FG)
        self._detail_rows['Created'].config(text=entry.created_at[:16] if entry.created_at else '—', fg=FG)
        self._detail_rows['Updated'].config(text=entry.updated_at[:16] if entry.updated_at else '—', fg=FG)

    def show_password(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('Warning', 'Please select an entry first.')
            return
        item = self.tree.item(selection[0])
        entry_id = item['tags'][0]
        entries = [e for e in self.db.get_all() if e.id == entry_id]
        if entries:
            entry = entries[0]
            password = self.crypto.decrypt(entry.encrypted_password)
            if password:
                pyperclip.copy(password)
                self._display_details(entry, show_password=True)
                self._set_status('✔  Password copied to clipboard — will hide in 10s')
                self.window.after(10000, lambda: self._display_details(entry, show_password=False))
            else:
                messagebox.showerror('Error', 'Failed to decrypt the password.')

    def add_entry(self):
        dialog = AddEditDialog(self.window, self.db, self.crypto)
        self.window.wait_window(dialog.dialog)
        if dialog.result:
            self.load_entries()
            self._update_categories()
            self._update_count()
            self._set_status('✔  New password added')

    def edit_entry(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('Warning', 'Please select a password to edit.')
            return
        item = self.tree.item(selection[0])
        entry_id = item['tags'][0]
        entries = [e for e in self.db.get_all() if e.id == entry_id]
        if entries:
            dialog = AddEditDialog(self.window, self.db, self.crypto, entries[0])
            self.window.wait_window(dialog.dialog)
            if dialog.result:
                self.load_entries()
                self._update_categories()
                self._update_count()
                self._set_status('✔  Password updated')
                self._on_select(None)

    def delete_entry(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('Warning', 'Please select a password to delete.')
            return
        if messagebox.askyesno('Confirm Delete', 'Permanently delete this password?'):
            item = self.tree.item(selection[0])
            entry_id = item['tags'][0]
            self.db.delete(entry_id)
            self.load_entries()
            self._clear_details()
            self._update_count()
            self._set_status('✔  Password deleted')

    def reset_all_data(self):
        if messagebox.askyesno('Reset All Data',
                               'WARNING: This will permanently delete ALL your passwords.\n\n'
                               'Are you sure you want to continue?'):
            if messagebox.askyesno('Final Confirmation',
                                   'This action cannot be undone.\n\n'
                                   'All saved passwords will be lost forever.\n'
                                   'Proceed?'):
                try:
                    self.db.reset_all_data()
                    self.load_entries()
                    self._update_categories()
                    self._update_count()
                    self._clear_details()
                    self._set_status('All data has been reset')
                    messagebox.showinfo('Done', 'All data has been reset.')
                except Exception as e:
                    messagebox.showerror('Error', f'Reset failed: {e}')

    def on_close(self):
        if messagebox.askyesno('Exit', 'Lock vault and exit?'):
            self.window.quit()
            self.window.destroy()

    def _set_status(self, text, duration=4000):
        self.status_label.config(text=text, fg=SUCCESS)
        self.window.after(duration, lambda: self.status_label.config(text='Ready', fg=FG_DIM))

    def run(self):
        self.window.mainloop()
