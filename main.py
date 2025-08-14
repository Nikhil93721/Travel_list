import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import bcrypt

# --- Constants & Configuration ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
DATABASE_FILE = "users.db"

# Canonical status keys (stored in DB)
STATUS_PACKED = "packed"
STATUS_NOT_PACKED = "not_packed"

# --- Text Content for Localization ---
text_content = {
    "en": {
        "app_title": "Travel Packing App",
        "login_title": "Login",
        "register_title": "Register",
        "welcome_title": "Welcome",
        "items_title": "Your Packing List",
        "delete_title": "Delete Items",
        "help_title": "Help & Instructions",
        "navigation_label": "Navigation",
        "username_label": "Username:",
        "password_label": "Password:",
        "register_label": "Don't have an account?",
        "register_link": "Register here",
        "login_link": "Already have an account? Login here",
        "login_button": "Login",
        "register_button": "Register",
        "logout_button": "Logout",
        "home_button": "Home",
        "items_button": "Packing List",
        "delete_page_button": "Delete Items",
        "help_button": "Help",
        "add_item_button": "Add Item",
        "mark_packed_button": "Mark as Packed",
        "refresh_button": "Refresh List",
        "item_label": "Enter Item to add...",
        "item_heading": "Item",
        "status_heading": "Status",
        "status_packed": "✅ Packed",
        "status_not_packed": "❌ Not Packed",
        "delete_item_button": "Delete",
        "login_failed": "Invalid username or password.",
        "register_success": "Registration successful! You can now log in.",
        "register_failed": "Username already exists. Please choose a different one.",
        "input_warning": "Enter an item name.",
        "input_userpass_warning": "Username and password cannot be empty.",
        "duplicate_warning": "is already in the list.",
        "confirm_delete": "Are you sure you want to delete '{}'?",
        "welcome_message": "Welcome, {}! Have a great trip! ✈️",
        "select_item_warning": "Please select an item first.",
        "select_lang": "Select Language:",
        "help_text": "**Welcome to the Travel Packing List App!**\n\n• Add items\n• Press Space or 'p' to toggle packed\n• Use Delete tab to remove items\n• Switch language any time",
        "no_items_label": "No items to delete."
    },
    "mr": {
        "app_title": "प्रवास पॅकिंग ॲप",
        "login_title": "लॉगिन करा",
        "register_title": "नोंदणी करा",
        "welcome_title": "स्वागत आहे",
        "items_title": "तुमची पॅकिंग सूची",
        "delete_title": "आयटम हटवा",
        "help_title": "मदत आणि सूचना",
        "navigation_label": "नेव्हिगेशन",
        "username_label": "वापरकर्ता नाव:",
        "password_label": "पासवर्ड:",
        "register_label": "खाते नाहीये?",
        "register_link": "येथे नोंदणी करा",
        "login_link": "आधीच खाते आहे? येथे लॉगिन करा",
        "login_button": "लॉगिन",
        "register_button": "नोंदणी करा",
        "logout_button": "लॉगआउट",
        "home_button": "होम",
        "items_button": "पॅकिंग सूची",
        "delete_page_button": "आयटम हटवा",
        "help_button": "मदत",
        "add_item_button": "आयटम जोडा",
        "mark_packed_button": "पॅक केलेले म्हणून चिन्हांकित करा",
        "refresh_button": "सूची रीफ्रेश करा",
        "item_label": "जोडण्यासाठी आयटम प्रविष्ट करा...",
        "item_heading": "आयटम",
        "status_heading": "स्थिती",
        "status_packed": "✅ पॅक केलेले",
        "status_not_packed": "❌ पॅक केलेले नाही",
        "delete_item_button": "हटवा",
        "login_failed": "चुकीचे वापरकर्तानाव किंवा पासवर्ड.",
        "register_success": "नोंदणी यशस्वी! तुम्ही आता लॉगिन करू शकता.",
        "register_failed": "वापरकर्तानाव आधीच अस्तित्वात आहे. कृपया दुसरे निवडा.",
        "input_warning": "आयटमचे नाव प्रविष्ट करा.",
        "input_userpass_warning": "वापरकर्तानाव आणि पासवर्ड रिक्त असू शकत नाहीत.",
        "duplicate_warning": "आधीच यादीत आहे.",
        "confirm_delete": "तुम्हाला '{}' हटवायचे आहे का?",
        "welcome_message": "स्वागत आहे, {}! तुमचा प्रवास सुखकर असो! ✈️",
        "select_item_warning": "कृपया आधी एक आयटम निवडा.",
        "select_lang": "भाषा निवडा:",
        "help_text": "**प्रवास पॅकिंग सूची ॲप मध्ये आपले स्वागत आहे!**\n\n• आयटम जोडा\n• स्पेस किंवा 'p' दाबून टॉगल करा\n• हटवण्यासाठी Delete टॅब\n• कधीही भाषा बदला",
        "no_items_label": "हटवण्यासाठी कोणतेही आयटम नाहीत."
    }
}

# Helpers to map canonical status <-> localized label
def local_status_label(lang, status_key):
    if status_key == STATUS_PACKED:
        return text_content[lang]["status_packed"]
    return text_content[lang]["status_not_packed"]

def infer_status_key(raw_status):
    """Accepts canonical keys or older saved emoji strings and returns a canonical key."""
    if raw_status in (STATUS_PACKED, STATUS_NOT_PACKED):
        return raw_status
    # Fallback for existing DB rows with emojis/strings
    s = str(raw_status)
    return STATUS_PACKED if "✅" in s or "Packed" in s or "पॅक केलेले" in s else STATUS_NOT_PACKED

# --- Database & Data Functions ---
def setup_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash BLOB NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return True

def check_login(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return None
    user_id, stored_hash = result
    # sqlite may return bytes (BLOB) or str; normalize to bytes
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return user_id
    return None

def load_items_from_db(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, item, status FROM items WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "item": r[1], "status": infer_status_key(r[2])} for r in rows]

def add_item_to_db(user_id, item_name, status_key):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (user_id, item, status) VALUES (?, ?, ?)", (user_id, item_name, status_key))
    conn.commit()
    conn.close()

def update_item_status_in_db(item_id, status_key):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET status=? WHERE id=?", (status_key, item_id))
    conn.commit()
    conn.close()

def delete_item_from_db(item_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def get_item_name_from_id(item_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT item FROM items WHERE id=?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# --- Reusable Base Class for Pages ---
class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller, page_name):
        super().__init__(parent)
        self.controller = controller
        self.page_name = page_name
        self.widgets = {}

# --- Application and Page Classes ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        setup_database()
        self.current_lang = "en"
        self.user_id = None
        self.title(text_content[self.current_lang]["app_title"])
        self.geometry("900x600")
        self.minsize(750, 500)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = SidebarFrame(self, self)
        self.main_content_frame = ctk.CTkFrame(self)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.frames = {
            "LoginPage": LoginPage(self.main_content_frame, self),
            "RegistrationPage": RegistrationPage(self.main_content_frame, self),
            "WelcomePage": WelcomePage(self.main_content_frame, self),
            "ItemsPage": ItemsPage(self.main_content_frame, self),
            "DeleteItemPage": DeleteItemPage(self.main_content_frame, self),
            "HelpPage": HelpPage(self.main_content_frame, self)
        }
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def _page_title_for(self, page_name):
        mapping = {
            "LoginPage": "login_title",
            "RegistrationPage": "register_title",
            "WelcomePage": "welcome_title",
            "ItemsPage": "items_title",
            "DeleteItemPage": "delete_title",
            "HelpPage": "help_title",
        }
        key = mapping.get(page_name, "app_title")
        return text_content[self.current_lang][key]

    def show_frame(self, page_name, username=None):
        frame = self.frames[page_name]

        is_auth_page = page_name in ["LoginPage", "RegistrationPage"]
        if is_auth_page:
            self.sidebar_frame.grid_forget()
            self.main_content_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="ns")
            self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.title(f"{text_content[self.current_lang]['app_title']} - {self._page_title_for(page_name)}")
        frame.tkraise()

        if page_name == "WelcomePage" and username:
            frame.update_welcome_message(username)
        elif page_name in ["ItemsPage", "DeleteItemPage"]:
            frame.refresh()

    def set_language(self, lang_name):
        lang_map = {"English": "en", "Marathi": "mr"}
        self.current_lang = lang_map.get(lang_name, "en")
        self.title(text_content[self.current_lang]["app_title"])
        self.sidebar_frame.update_language()
        for frame in self.frames.values():
            if hasattr(frame, "update_language"):
                frame.update_language()

    def logout(self):
        self.user_id = None
        self.show_frame("LoginPage")

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=140, corner_radius=0)
        self.controller = controller
        self.grid_rowconfigure(5, weight=1)

        self.nav_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.nav_label.grid(row=0, column=0, padx=20, pady=20)

        self.buttons = [
            ("home", lambda: self.controller.show_frame("WelcomePage")),
            ("items", lambda: self.controller.show_frame("ItemsPage")),
            ("delete_page", lambda: self.controller.show_frame("DeleteItemPage")),
            ("help", lambda: self.controller.show_frame("HelpPage"))
        ]

        for i, (key, command) in enumerate(self.buttons):
            btn = ctk.CTkButton(self, text=text_content[self.controller.current_lang][f"{key}_button"], command=command)
            btn.grid(row=i + 1, column=0, padx=20, pady=10, sticky="ew")
            setattr(self, f"{key}_button", btn)

        self.logout_button = ctk.CTkButton(self, text=text_content[self.controller.current_lang]["logout_button"], command=self.controller.logout)
        self.logout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        self.update_language()

    def update_language(self):
        self.nav_label.configure(text=text_content[self.controller.current_lang]["navigation_label"])
        for key, _ in self.buttons:
            getattr(self, f"{key}_button").configure(text=text_content[self.controller.current_lang][f"{key}_button"])
        self.logout_button.configure(text=text_content[self.controller.current_lang]["logout_button"])

class LoginPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "LoginPage")
        frame = ctk.CTkFrame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        self.widgets["login_title"] = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.widgets["login_title"].pack(pady=20)

        self.widgets["lang"] = ctk.CTkOptionMenu(frame, values=["English", "Marathi"], command=self.controller.set_language)
        self.widgets["lang"].pack(pady=(0, 15))

        self.widgets["username"] = ctk.CTkEntry(frame, placeholder_text="")
        self.widgets["username"].pack(pady=10, padx=20)

        self.widgets["password_frame"] = ctk.CTkFrame(frame, fg_color="transparent")
        self.widgets["password_frame"].pack(pady=10, padx=15, fill="x")
        self.widgets["password_frame"].columnconfigure(0, weight=1)

        self.widgets["password"] = ctk.CTkEntry(self.widgets["password_frame"], placeholder_text="", show="*")
        self.widgets["password"].grid(row=0, column=0, sticky="ew")

        self.widgets["password_show_button"] = ctk.CTkButton(self.widgets["password_frame"], text="👁️", width=10, command=self.toggle_password_visibility)
        self.widgets["password_show_button"].grid(row=0, column=1, padx=(5, 0))

        self.widgets["login"] = ctk.CTkButton(frame, text="", command=self.handle_login)
        self.widgets["login"].pack(pady=(20, 10))

        self.widgets["register"] = ctk.CTkLabel(frame, text="")
        self.widgets["register"].pack(pady=(0, 5))

        self.widgets["register_link"] = ctk.CTkButton(frame, text="", fg_color="transparent", text_color=("blue", "cyan"), hover_color=("gray80", "gray25"), command=lambda: self.controller.show_frame("RegistrationPage"))
        self.widgets["register_link"].pack(pady=(0, 10))

        self.update_language()

    def update_language(self):
        self.widgets["login_title"].configure(text=text_content[self.controller.current_lang]["login_title"])
        self.widgets["username"].configure(placeholder_text=text_content[self.controller.current_lang]["username_label"])
        self.widgets["password"].configure(placeholder_text=text_content[self.controller.current_lang]["password_label"])
        self.widgets["login"].configure(text=text_content[self.controller.current_lang]["login_button"])
        self.widgets["register"].configure(text=text_content[self.controller.current_lang]["register_label"])
        self.widgets["register_link"].configure(text=text_content[self.controller.current_lang]["register_link"])

    def handle_login(self):
        username = self.widgets["username"].get().strip()
        password = self.widgets["password"].get().strip()
        user_id = check_login(username, password)
        if user_id:
            self.controller.user_id = user_id
            self.controller.show_frame("WelcomePage", username)
        else:
            messagebox.showerror(text_content[self.controller.current_lang]["login_title"], text_content[self.controller.current_lang]["login_failed"])

    def toggle_password_visibility(self):
        show = self.widgets["password"].cget("show")
        new_show, icon = ("", "🔒") if show == "*" else ("*", "👁️")
        self.widgets["password"].configure(show=new_show)
        self.widgets["password_show_button"].configure(text=icon)

class RegistrationPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "RegistrationPage")
        frame = ctk.CTkFrame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        self.widgets["register_title"] = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.widgets["register_title"].pack(pady=20)
        self.widgets["new_username"] = ctk.CTkEntry(frame, placeholder_text="")
        self.widgets["new_username"].pack(pady=10, padx=20)
        self.widgets["new_password"] = ctk.CTkEntry(frame, placeholder_text="", show="*")
        self.widgets["new_password"].pack(pady=10, padx=20)
        self.widgets["register_button"] = ctk.CTkButton(frame, text="", command=self.handle_register)
        self.widgets["register_button"].pack(pady=(20, 10))
        self.widgets["login_link_label"] = ctk.CTkLabel(frame, text="")
        self.widgets["login_link_label"].pack(pady=(0, 5))
        self.widgets["login_link_button"] = ctk.CTkButton(frame, text="", fg_color="transparent", text_color=("blue", "cyan"), hover_color=("gray80", "gray25"), command=lambda: self.controller.show_frame("LoginPage"))
        self.widgets["login_link_button"].pack(pady=(0, 10))

        self.update_language()

    def update_language(self):
        self.widgets["register_title"].configure(text=text_content[self.controller.current_lang]["register_title"])
        self.widgets["new_username"].configure(placeholder_text=text_content[self.controller.current_lang]["username_label"])
        self.widgets["new_password"].configure(placeholder_text=text_content[self.controller.current_lang]["password_label"])
        self.widgets["register_button"].configure(text=text_content[self.controller.current_lang]["register_button"])
        self.widgets["login_link_label"].configure(text=text_content[self.controller.current_lang]["login_link"])
        self.widgets["login_link_button"].configure(text=text_content[self.controller.current_lang]["login_link"])

    def handle_register(self):
        username = self.widgets["new_username"].get().strip()
        password = self.widgets["new_password"].get().strip()
        if not username or not password:
            messagebox.showwarning(text_content[self.controller.current_lang]["register_title"], text_content[self.controller.current_lang]["input_userpass_warning"])
            return
        if register_user(username, password):
            messagebox.showinfo(text_content[self.controller.current_lang]["register_title"], text_content[self.controller.current_lang]["register_success"])
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror(text_content[self.controller.current_lang]["register_title"], text_content[self.controller.current_lang]["register_failed"])

class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "WelcomePage")
        frame = ctk.CTkFrame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        self.widgets["welcome"] = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.widgets["welcome"].pack(pady=20, padx=40)
        self.widgets["items"] = ctk.CTkButton(frame, text="", command=lambda: self.controller.show_frame("ItemsPage"))
        self.widgets["items"].pack(pady=10)
        self.widgets["help"] = ctk.CTkButton(frame, text="", command=lambda: self.controller.show_frame("HelpPage"))
        self.widgets["help"].pack(pady=10)
        self.update_language()

    def update_welcome_message(self, username):
        self.widgets["welcome"].configure(text=text_content[self.controller.current_lang]["welcome_message"].format(username))

    def update_language(self):
        self.widgets["items"].configure(text=text_content[self.controller.current_lang]["items_button"])
        self.widgets["help"].configure(text=text_content[self.controller.current_lang]["help_button"])

class ItemsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "ItemsPage")
        self.items = []

        # Treeview style to look nicer with CTk
        style = ttk.Style()
        try:
            style.theme_use(style.theme_use())  # keep current theme
        except Exception:
            pass
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        self.widgets["items_title"] = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.widgets["items_title"].pack(pady=10)

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=(0, 20), padx=20, fill="x")
        input_frame.grid_columnconfigure(0, weight=1)

        self.item_var = ctk.StringVar()
        self.widgets["item_entry"] = ctk.CTkEntry(input_frame, placeholder_text="", textvariable=self.item_var)
        self.widgets["item_entry"].grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.widgets["add_item"] = ctk.CTkButton(input_frame, text="", command=self.add_item)
        self.widgets["add_item"].grid(row=0, column=1, padx=(0, 10))

        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Item", "Status"), show="headings")
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.column("Item", width=300, anchor="w")
        self.tree.column("Status", width=150, anchor="center")

        scrollbar = ctk.CTkScrollbar(self.tree_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(pady=20, padx=20, fill="x")

        self.widgets["mark_packed"] = ctk.CTkButton(actions_frame, text="", command=self.mark_packed)
        self.widgets["mark_packed"].pack(side="left", padx=(0, 10))
        self.widgets["refresh"] = ctk.CTkButton(actions_frame, text="", command=self.refresh)
        self.widgets["refresh"].pack(side="left")

        # Key bindings limited to the tree; prevent default behavior with "break"
        self.widgets["item_entry"].bind("<Return>", self.add_item)
        self.tree.bind("<space>", self.mark_packed)
        self.tree.bind("p", self.mark_packed)

        self.update_language()

    def update_language(self):
        self.widgets["items_title"].configure(text=text_content[self.controller.current_lang]["items_title"])
        self.widgets["item_entry"].configure(placeholder_text=text_content[self.controller.current_lang]["item_label"])
        self.widgets["add_item"].configure(text=text_content[self.controller.current_lang]["add_item_button"])
        self.widgets["mark_packed"].configure(text=text_content[self.controller.current_lang]["mark_packed_button"])
        self.widgets["refresh"].configure(text=text_content[self.controller.current_lang]["refresh_button"])
        self.tree.heading("Item", text=text_content[self.controller.current_lang]["item_heading"])
        self.tree.heading("Status", text=text_content[self.controller.current_lang]["status_heading"])
        self.refresh()

    def refresh(self):
        self.items = load_items_from_db(self.controller.user_id)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.items:
            self.tree.insert("", "end", iid=item["id"],
                             values=(item["item"], local_status_label(self.controller.current_lang, item["status"])))

    def add_item(self, event=None):
        item_name = self.item_var.get().strip()
        if not item_name:
            messagebox.showwarning(text_content[self.controller.current_lang]["items_title"], text_content[self.controller.current_lang]["input_warning"])
            return "break" if event else None
        if item_name.lower() in [i["item"].lower() for i in self.items]:
            messagebox.showinfo(text_content[self.controller.current_lang]["items_title"], f"'{item_name}' {text_content[self.controller.current_lang]['duplicate_warning']}")
            return "break" if event else None
        add_item_to_db(self.controller.user_id, item_name, STATUS_NOT_PACKED)
        self.item_var.set("")
        self.refresh()
        return "break" if event else None

    def mark_packed(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(text_content[self.controller.current_lang]["items_title"], text_content[self.controller.current_lang]["select_item_warning"])
            return "break"
        item_id = int(selected[0])
        # Find current status from memory (already canonical)
        current = next((i for i in self.items if i["id"] == item_id), None)
        new_status = STATUS_PACKED if not current or current["status"] == STATUS_NOT_PACKED else STATUS_NOT_PACKED
        update_item_status_in_db(item_id, new_status)
        self.refresh()
        return "break"

class DeleteItemPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.delete_title_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.delete_title_label.pack(pady=10)

        self.item_list_frame = ctk.CTkScrollableFrame(self)
        self.item_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.items = []
        self.update_language()

    def refresh(self):
        for widget in self.item_list_frame.winfo_children():
            widget.destroy()

        self.items = load_items_from_db(self.controller.user_id)

        if not self.items:
            ctk.CTkLabel(self.item_list_frame, text=text_content[self.controller.current_lang]["no_items_label"], font=ctk.CTkFont(size=14)).pack(pady=20)
            return

        for item in self.items:
            item_frame = ctk.CTkFrame(self.item_list_frame)
            item_frame.pack(fill="x", padx=10, pady=5)
            item_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(item_frame, text=item["item"], anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="ew")

            ctk.CTkButton(
                item_frame,
                text=text_content[self.controller.current_lang]["delete_item_button"],
                fg_color="red", hover_color="darkred",
                width=80,
                command=lambda item_id=item["id"], item_name=item["item"]: self.delete_item(item_id, item_name)
            ).grid(row=0, column=1, padx=10, pady=5)

    def delete_item(self, item_id, item_name):
        if messagebox.askyesno(text_content[self.controller.current_lang]["delete_title"],
                               text_content[self.controller.current_lang]["confirm_delete"].format(item_name)):
            delete_item_from_db(item_id)
            self.refresh()

    def update_language(self):
        self.delete_title_label.configure(text=text_content[self.controller.current_lang]["delete_title"])

class HelpPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "HelpPage")
        self.widgets["help_title"] = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.widgets["help_title"].pack(pady=20)
        self.widgets["help_text"] = ctk.CTkLabel(self, text="", justify="left", wraplength=550, font=ctk.CTkFont(size=14))
        self.widgets["help_text"].pack(pady=10, padx=20, fill="x")
        self.update_language()

    def update_language(self):
        self.widgets["help_title"].configure(text=text_content[self.controller.current_lang]["help_title"])
        self.widgets["help_text"].configure(text=text_content[self.controller.current_lang]["help_text"])

# --- Main Application Execution ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
