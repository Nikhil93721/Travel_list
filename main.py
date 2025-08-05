import tkinter as tk
from tkinter import ttk, messagebox
import json, os

FILE = "packing.json"


def load_data():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []
def save_data():
    json.dump(items, open(FILE, "w"))
    refresh()

def add_item():
    item = item_var.get().strip()
    existing = [it["item"].lower() for it in items]
    if item.lower() in existing:
        messagebox.showinfo("Duplicate", f"'{item}' is already in the list.")
        return
    if item:
        items.append({"item": item, "status": "❌ Not Packed"})
        save_data()
        refresh()
        item_var.set("")
    else:
        messagebox.showwarning("Input", "Enter an item name.")
        item_var.set("")

def mark_packed():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        items[idx]["status"] = "✅ Packed"
        save_data()
        refresh()

def delete_item():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        if messagebox.askyesno("Confirm", f"Delete '{items[idx]['item']}'?"):
            items.pop(idx)
            save_data()
            refresh()

def refresh():
    tree.delete(*tree.get_children())
    for i, it in enumerate(items):
        tree.insert("", "end", iid=i, values=(it["item"], it["status"]))


    

root = tk.Tk()
root.title("Travel Packing List")
root.geometry("400x400")

item_var = tk.StringVar()
items = load_data()


tk.Label(root, text="Enter Item:").pack()
tk.Entry(root, textvariable=item_var).pack(pady=5)
tk.Button(root, text="Add Item", command=add_item).pack(pady=5)


tree = ttk.Treeview(root, columns=("Item", "Status"), show="headings")
tree.heading("Item", text="Item")
tree.heading("Status", text="Status")
tree.column("Item", width=200)
tree.column("Status", width=100)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
tk.Button(root, text="Refresh List", command=refresh).pack(pady=5)


tk.Button(root, text="Mark as Packed", command=mark_packed).pack(pady=3)
tk.Button(root, text="Delete Item", command=delete_item).pack(pady=3)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


root.bind("<Return>", lambda e: add_item())
tree.bind("<BackSpace>", lambda e: delete_item())
tree.bind("<space>", lambda e: mark_packed())
tree.bind("p", lambda e: mark_packed())

refresh()
root.mainloop()



# import tkinter as tk
# from tkinter import ttk, messagebox
# import json, os

# FILE = "packing.json"

# # ---------------- Data ----------------

# def load_data():
#     if os.path.exists(FILE):
#         try:
#             with open(FILE, "r") as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             return []
#     return []

# def save_data():
#     with open(FILE, "w") as f:
#         json.dump(items, f, indent=2)
#     refresh()

# # ---------------- Actions ----------------

# def add_item(event=None):
#     item = item_var.get().strip()
#     existing = [it["item"].lower() for it in items]
#     if not item:
#         messagebox.showwarning("Input", "Enter an item name.")
#         item_var.set("")
#         return
#     if item.lower() in existing:
#         messagebox.showinfo("Duplicate", f"'{item}' is already in the list.")
#         item_var.set("")
#         return
#     items.append({"item": item, "status": "❌ Not Packed"})
#     save_data()
#     item_var.set("")

# def mark_packed(event=None):
#     selected = tree.selection()
#     if selected:
#         idx = int(selected[0])
#         items[idx]["status"] = "✅ Packed"
#         save_data()

# def delete_item(event=None):
#     selected = tree.selection()
#     if selected:
#         idx = int(selected[0])
#         if messagebox.askyesno("Confirm", f"Delete '{items[idx]['item']}'?"):
#             items.pop(idx)
#             save_data()

# def refresh():
#     tree.delete(*tree.get_children())
#     for i, it in enumerate(items):
#         tag = "even" if i % 2 == 0 else "odd"
#         tree.insert("", "end", iid=i, values=(it.get("item", ""), it.get("status", "")), tags=(tag,))

# # ---------------- UI ----------------

# root = tk.Tk()
# root.title("Travel Packing List")
# root.geometry("450x500")
# root.minsize(350, 350)

# item_var = tk.StringVar()
# items = load_data()

# background_color = "#f0f0f0"
# style = ttk.Style()
# style.theme_use("default")

# style.configure(
#     "Custom.Treeview",
#     background=background_color,
#     fieldbackground=background_color,
#     foreground="black",
#     rowheight=24,
#     font=("TkDefaultFont", 10),
# )
# style.configure(
#     "Custom.Treeview.Heading",
#     background="#d9d9d9",
#     font=("TkDefaultFont", 10, "bold"),
# )
# style.map("Custom.Treeview", background=[("selected", "#55595e")], foreground=[("selected", "black")])

# top_frame = ttk.Frame(root, padding=8)
# top_frame.pack(fill="x", padx=10, pady=(10, 4))
# top_frame.columnconfigure(1, weight=1)

# ttk.Label(top_frame, text="Enter Item:").grid(row=0, column=0, sticky="w")
# entry = ttk.Entry(top_frame, textvariable=item_var)
# entry.grid(row=0, column=1, sticky="ew", padx=6)
# ttk.Button(top_frame, text="Add Item", command=add_item).grid(row=0, column=2, padx=(0, 6))

# tree_frame = ttk.Frame(root)
# tree_frame.pack(fill="both", expand=True, padx=20, pady=8)
# tree_frame.columnconfigure(0, weight=1)
# tree_frame.rowconfigure(0, weight=1)

# cols = ("Item", "Status")
# tree = ttk.Treeview(
#     tree_frame,
#     columns=cols,
#     show="headings",
#     selectmode="browse",
#     style="Custom.Treeview",
# )
# tree.heading("Item", text="Item")
# tree.heading("Status", text="Status")
# tree.column("Item", width=250, anchor="w")
# tree.column("Status", width=120, anchor="center")
# tree.grid(row=0, column=0, sticky="nsew")

# vscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
# tree.configure(yscrollcommand=vscroll.set)
# vscroll.grid(row=0, column=1, sticky="ns")

# tree.tag_configure("odd", background="#ffffff")
# tree.tag_configure("even", background="#FDF9F9")

# btn_frame = ttk.Frame(root, padding=6)
# btn_frame.pack(fill="x", padx=10, pady=(4, 12))
# for i in range(3):
#     btn_frame.columnconfigure(i, weight=1)

# ttk.Button(btn_frame, text="Refresh List", command=refresh).grid(row=0, column=0, padx=4, sticky="ew")
# ttk.Button(btn_frame, text="Mark as Packed", command=mark_packed).grid(row=0, column=1, padx=4, sticky="ew")
# ttk.Button(btn_frame, text="Delete Item", command=delete_item).grid(row=0, column=2, padx=4, sticky="ew")

# entry.bind("<Return>", add_item)
# tree.bind("<Delete>", delete_item)
# tree.bind("<BackSpace>", delete_item)
# tree.bind("<space>", mark_packed)
# tree.bind("p", mark_packed)
# root.bind("<Return>", add_item)

# root.configure(bg=background_color)

# entry.focus_set()
# refresh()
# root.mainloop()


