from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# ================= DATABASE CONNECTION ================= #

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="102938",   
        database="expense_tracker_db"
    )

    cursor = conn.cursor()

except mysql.connector.Error as err:
    messagebox.showerror("Database Error", str(err))
    exit()

# ================= CREATE TABLE IF NOT EXISTS ================= #

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    amount DECIMAL(10,2),
    category VARCHAR(100),
    expense_date VARCHAR(50)
)
""")

conn.commit()

# ================= FUNCTIONS ================= #

def add_expense():

    title = title_entry.get()
    amount = amount_entry.get()
    category = category_combo.get()

    if title == "" or amount == "" or category == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        amount = float(amount)

    except:
        messagebox.showerror("Error", "Amount must be numeric!")
        return

    date = datetime.now().strftime("%d-%m-%Y")

    sql = """
    INSERT INTO expenses(title, amount, category, expense_date)
    VALUES(%s,%s,%s,%s)
    """

    values = (title, amount, category, date)

    cursor.execute(sql, values)
    conn.commit()

    messagebox.showinfo("Success", "Expense Added Successfully!")

    clear_fields()
    show_expenses()
    update_total()


def show_expenses():

    tree.delete(*tree.get_children())

    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", END, values=row)


def clear_fields():

    title_entry.delete(0, END)
    amount_entry.delete(0, END)
    category_combo.set("")


def delete_expense():

    selected = tree.focus()

    if not selected:
        messagebox.showerror("Error", "Select an expense first!")
        return

    data = tree.item(selected)
    expense_id = data["values"][0]

    cursor.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
    conn.commit()

    messagebox.showinfo("Deleted", "Expense Deleted!")

    show_expenses()
    update_total()


def update_total():

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    total_label.config(text=f"Total Expense: Rs. {total}")


def search_expense():

    keyword = search_entry.get()

    tree.delete(*tree.get_children())

    sql = """
    SELECT * FROM expenses
    WHERE title LIKE %s OR category LIKE %s
    """

    value = (f"%{keyword}%", f"%{keyword}%")

    cursor.execute(sql, value)

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", END, values=row)


# ================= GUI ================= #

root = Tk()

root.title("Professional Expense Tracker")
root.geometry("1000x650")
root.config(bg="#1e272e")

# ================= STYLE ================= #

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#2f3640",
    foreground="white",
    rowheight=28,
    fieldbackground="#2f3640",
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background="#0984e3",
    foreground="white",
    font=("Segoe UI", 11, "bold")
)

# ================= HEADER ================= #

header = Frame(root, bg="#0984e3", height=80)
header.pack(fill=X)

title = Label(
    header,
    text="Expense Tracker Dashboard",
    bg="#0984e3",
    fg="white",
    font=("Segoe UI", 24, "bold")
)

title.pack(pady=20)

# ================= LEFT FRAME ================= #

left_frame = Frame(root, bg="#1e272e")
left_frame.place(x=20, y=100, width=300, height=520)

Label(
    left_frame,
    text="Add New Expense",
    bg="#1e272e",
    fg="white",
    font=("Segoe UI", 18, "bold")
).pack(pady=10)

# Title
Label(
    left_frame,
    text="Expense Title",
    bg="#1e272e",
    fg="white",
    font=("Segoe UI", 11)
).pack(anchor=W, padx=10)

title_entry = Entry(
    left_frame,
    font=("Segoe UI", 11),
    width=28,
    bd=2
)

title_entry.pack(pady=8)

# Amount
Label(
    left_frame,
    text="Amount",
    bg="#1e272e",
    fg="white",
    font=("Segoe UI", 11)
).pack(anchor=W, padx=10)

amount_entry = Entry(
    left_frame,
    font=("Segoe UI", 11),
    width=28,
    bd=2
)

amount_entry.pack(pady=8)

# Category
Label(
    left_frame,
    text="Category",
    bg="#1e272e",
    fg="white",
    font=("Segoe UI", 11)
).pack(anchor=W, padx=10)

category_combo = ttk.Combobox(
    left_frame,
    font=("Segoe UI", 11),
    width=25,
    state="readonly"
)

category_combo["values"] = (
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Other"
)

category_combo.pack(pady=8)

# Buttons
Button(
    left_frame,
    text="Add Expense",
    bg="#00b894",
    fg="white",
    font=("Segoe UI", 11, "bold"),
    width=22,
    command=add_expense
).pack(pady=10)

Button(
    left_frame,
    text="Delete Selected",
    bg="#d63031",
    fg="white",
    font=("Segoe UI", 11, "bold"),
    width=22,
    command=delete_expense
).pack(pady=5)

Button(
    left_frame,
    text="Clear Fields",
    bg="#636e72",
    fg="white",
    font=("Segoe UI", 11, "bold"),
    width=22,
    command=clear_fields
).pack(pady=5)

# ================= RIGHT FRAME ================= #

right_frame = Frame(root, bg="#2d3436")
right_frame.place(x=340, y=100, width=630, height=520)

# Search
search_entry = Entry(
    right_frame,
    font=("Segoe UI", 11),
    width=30
)

search_entry.place(x=20, y=20)

Button(
    right_frame,
    text="Search",
    bg="#0984e3",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    command=search_expense
).place(x=300, y=18)

# Total
total_label = Label(
    right_frame,
    text="Total Expense: Rs. 0",
    bg="#2d3436",
    fg="#00cec9",
    font=("Segoe UI", 16, "bold")
)

total_label.place(x=400, y=18)

# ================= TABLE ================= #

columns = (
    "ID",
    "Title",
    "Amount",
    "Category",
    "Date"
)

tree = ttk.Treeview(
    right_frame,
    columns=columns,
    show="headings"
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110)

tree.place(x=20, y=70, width=580, height=420)

# ================= FOOTER ================= #

footer = Label(
    root,
    text="Admin Panel | Expense Tracker System",
    bg="#0984e3",
    fg="white",
    font=("Segoe UI", 10)
)

footer.pack(side=BOTTOM, fill=X)

# ================= LOAD DATA ================= #

show_expenses()
update_total()

# ================= RUN APP ================= #

root.mainloop()