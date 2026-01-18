"""
SWEETS'n JOY - Tkinter Frontend for Bakery Management System

Improved version with:
- Better layout and aesthetics (fonts, padding, themes)
- Fixed prediction output formatting
- Corrected database procedure calls
- Improved error handling and navigation
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import mysql.connector
from datetime import date, timedelta
from sklearn.ensemble import RandomForestRegressor
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Style Configurations
COLORS = {
    "primary": "#6D4C41",    # Brown (Bakery feel)
    "secondary": "#FFF3E0",  # Light cream
    "accent": "#FFAB40",     # Orange/Gold
    "text": "#3E2723",
    "white": "#FFFFFF"
}

FONTS = {
    "title": ("Helvetica", 24, "bold"),
    "header": ("Helvetica", 16, "bold"),
    "normal": ("Helvetica", 10),
    "button": ("Helvetica", 10, "bold")
}

class BakeryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SWEETS'N JOY - Bakery Management")
        self.geometry("1100x750")
        self.configure(bg=COLORS["secondary"])

        # Set theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLORS["secondary"])
        style.configure("TLabel", background=COLORS["secondary"], foreground=COLORS["text"], font=FONTS["normal"])
        style.configure("TButton", font=FONTS["button"], padding=5)
        style.configure("Header.TLabel", font=FONTS["header"], foreground=COLORS["primary"])

        # DB connection
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Aaradhya4252",
                database="bakery1"
            )
            self.cursor = self.mydb.cursor()
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not connect to DB: {e}")

        self.inventory_items = []
        self.employees = []
        try:
            self.load_inventory()
            self.load_employees()
        except:
            pass

        self.cart = pd.DataFrame(columns=["item", "flavour", "quantity", "price", "total"])

        self.create_widgets()

    def load_inventory(self):
        self.cursor.execute("SELECT DISTINCT item FROM inventory12")
        self.inventory_items = [i[0] for i in self.cursor.fetchall()]

    def load_employees(self):
        self.cursor.execute("SELECT DISTINCT id FROM employee")
        self.employees = [i[0] for i in self.cursor.fetchall()]

    def create_widgets(self):
        # Banner
        banner = tk.Frame(self, bg=COLORS["primary"], height=80)
        banner.pack(fill="x")
        tk.Label(banner, text="SWEETS 'N JOY BAKERY", bg=COLORS["primary"], fg=COLORS["white"], font=FONTS["title"]).pack(pady=15)

        # Sidebar / Navigation
        nav_frame = tk.Frame(self, bg=COLORS["primary"], width=200)
        nav_frame.pack(side="left", fill="y")

        nav_buttons = [
            ("🏠 Menu", self.show_menu),
            ("🛒 Purchase", self.show_purchase),
            ("📄 Latest Bill", self.show_bill),
            ("💬 Feedback", self.show_feedback),
            ("📊 Sales Login", self.show_sales_login),
        ]

        for text, cmd in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=cmd, bg=COLORS["primary"], fg=COLORS["white"], 
                            font=FONTS["button"], bd=0, padx=20, pady=15, anchor="w", activebackground=COLORS["accent"])
            btn.pack(fill="x")

        tk.Button(nav_frame, text="🚪 Exit", command=self.quit, bg="#C62828", fg=COLORS["white"], 
                  font=FONTS["button"], bd=0, padx=20, pady=15, anchor="w").pack(side="bottom", fill="x")

        # Main Content Area
        self.container = ttk.Frame(self)
        self.container.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.frames = {}
        for F in (MenuFrame, PurchaseFrame, BillFrame, FeedbackFrame, SalesLoginFrame, SalesReportFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_menu(self):
        self.frames['MenuFrame'].refresh()
        self.show_frame('MenuFrame')

    def show_purchase(self):
        self.frames['PurchaseFrame'].refresh()
        self.show_frame('PurchaseFrame')

    def show_bill(self):
        self.frames['BillFrame'].refresh()
        self.show_frame('BillFrame')

    def show_feedback(self):
        self.frames['FeedbackFrame'].refresh()
        self.show_frame('FeedbackFrame')

    def show_sales_login(self):
        self.frames['SalesLoginFrame'].reset()
        self.show_frame('SalesLoginFrame')

    def show_sales_report(self):
        self.frames['SalesReportFrame'].reset()
        self.show_frame('SalesReportFrame')

    def get_flavours_for_item(self, item):
        self.cursor.execute("SELECT flavour, price, stock FROM inventory12 WHERE item=%s", (item,))
        rows = self.cursor.fetchall()
        return [{'flavour': r[0], 'price': r[1], 'stock': r[2]} for r in rows]

    def update_stock_and_record_sale(self, item, flavour, qty, price):
        self.cursor.execute("SELECT stock FROM inventory12 WHERE item=%s AND flavour=%s", (item, flavour))
        res = self.cursor.fetchone()
        if not res: raise ValueError("Item/flavour not found")
        curr_stock = res[0]
        if qty > curr_stock: raise ValueError("Not enough stock")
        
        new_stock = curr_stock - qty
        self.cursor.execute("UPDATE inventory12 SET stock=%s WHERE item=%s AND flavour=%s", (new_stock, item, flavour))
        
        total = qty * price
        self.cursor.execute("INSERT INTO td_sale1 (item, flavour, price, stock, date_) VALUES (%s,%s,%s,%s,%s)",
                            (item, flavour, qty, total, date.today()))
        self.mydb.commit()
        return total

    def create_bill_table_if_not_exists(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS bill (sr INT AUTO_INCREMENT PRIMARY KEY, item CHAR(100), flavour CHAR(100), quantity INT, total DOUBLE)")
        self.mydb.commit()

    def aggregate_sales_by_date(self):
        self.cursor.execute("SELECT date_, SUM(stock) FROM td_sale1 GROUP BY date_")
        data = self.cursor.fetchall()
        if not data: return pd.DataFrame(columns=["date", "quantity"]) 
        df = pd.DataFrame(data, columns=["date", "quantity"]).sort_values("date")
        df['date'] = pd.to_datetime(df['date'])
        return df

class MenuFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Bakery Menu & Inventory", style="Header.TLabel").pack(pady=10)

        cols = ("Item", "Flavour", "Price (₹)", "Stock")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor='center', width=150)
        self.tree.pack(fill='both', expand=True, padx=20)

        ttk.Button(self, text="🔄 Refresh Inventory", command=self.refresh).pack(pady=15)

    def refresh(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        try:
            self.controller.cursor.execute("SELECT item, flavour, price, stock FROM inventory12")
            for r in self.controller.cursor.fetchall():
                self.tree.insert('', 'end', values=r)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {e}")

class PurchaseFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="New Purchase", style="Header.TLabel").pack(pady=10)

        form = tk.Frame(self, bg=COLORS["secondary"])
        form.pack(pady=10, fill="x")

        # Layout using grid for better control
        tk.Label(form, text="Item:", bg=COLORS["secondary"]).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.item_cb = ttk.Combobox(form, values=self.controller.inventory_items, state='readonly', width=30)
        self.item_cb.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.item_cb.bind("<<ComboboxSelected>>", self.on_item_selected)

        tk.Label(form, text="Flavour:", bg=COLORS["secondary"]).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.flavour_cb = ttk.Combobox(form, values=[], state='readonly', width=30)
        self.flavour_cb.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form, text="Stock Available:", bg=COLORS["secondary"]).grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.stock_var = tk.StringVar(value='-')
        tk.Label(form, textvariable=self.stock_var, font=("Helvetica", 10, "bold"), bg=COLORS["secondary"], fg=COLORS["primary"]).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        tk.Label(form, text="Quantity:", bg=COLORS["secondary"]).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.qty_entry = ttk.Entry(form, width=10)
        self.qty_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        ttk.Button(form, text="➕ Add to Cart", command=self.add_to_cart).grid(row=2, column=1, columnspan=2, pady=15)

        # Cart Table
        cols = ("Item", "Flavour", "Qty", "Unit Price", "Total (₹)")
        self.cart_tree = ttk.Treeview(self, columns=cols, show='headings', height=10)
        for c in cols:
            self.cart_tree.heading(c, text=c)
            self.cart_tree.column(c, anchor='center')
        self.cart_tree.pack(fill='both', expand=True, padx=20, pady=10)

        bottom = tk.Frame(self, bg=COLORS["secondary"])
        bottom.pack(fill='x', padx=20, pady=10)
        
        self.total_var = tk.StringVar(value='0.00')
        tk.Label(bottom, text="Grand Total: ₹", font=FONTS["header"], bg=COLORS["secondary"]).pack(side='left')
        tk.Label(bottom, textvariable=self.total_var, font=FONTS["header"], bg=COLORS["secondary"], fg="#2E7D32").pack(side='left')
        
        ttk.Button(bottom, text="✅ Checkout", command=self.checkout).pack(side='right', padx=10)
        ttk.Button(bottom, text="🧹 Clear Cart", command=self.clear_cart).pack(side='right')

    def refresh(self):
        self.item_cb['values'] = self.controller.inventory_items
        self.clear_cart()

    def on_item_selected(self, event=None):
        item = self.item_cb.get()
        if not item: return
        flavours = self.controller.get_flavours_for_item(item)
        self.flavour_map = {f['flavour']: f for f in flavours}
        vals = list(self.flavour_map.keys())
        self.flavour_cb['values'] = vals
        if vals:
            self.flavour_cb.set(vals[0])
            self.stock_var.set(str(self.flavour_map[vals[0]]['stock']))
        self.flavour_cb.bind('<<ComboboxSelected>>', self.on_flavour_selected)

    def on_flavour_selected(self, event=None):
        flav = self.flavour_cb.get()
        if flav in getattr(self, 'flavour_map', {}):
            self.stock_var.set(str(self.flavour_map[flav]['stock']))

    def add_to_cart(self):
        item, flavour, qty_str = self.item_cb.get(), self.flavour_cb.get(), self.qty_entry.get()
        if not all([item, flavour, qty_str]):
            messagebox.showwarning("Incomplete", "Please select item/flavour and enter quantity")
            return
        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Quantity must be a positive integer")
            return

        stock = self.flavour_map[flavour]['stock']
        if qty > stock:
            messagebox.showerror("Stock Error", f"Only {stock} items available")
            return
        
        price = self.flavour_map[flavour]['price']
        total = qty * price
        new_row = pd.DataFrame([{"item": item, "flavour": flavour, "quantity": qty, "price": price, "total": total}])
        self.controller.cart = pd.concat([self.controller.cart, new_row], ignore_index=True)
        self.refresh_cart_view()
        self.qty_entry.delete(0, 'end')

    def refresh_cart_view(self):
        for r in self.cart_tree.get_children(): self.cart_tree.delete(r)
        total_sum = 0
        for _, row in self.controller.cart.iterrows():
            self.cart_tree.insert('', 'end', values=(row['item'], row['flavour'], int(row['quantity']), f"{row['price']:.2f}", f"{row['total']:.2f}"))
            total_sum += row['total']
        self.total_var.set(f"{total_sum:.2f}")

    def clear_cart(self):
        self.controller.cart = pd.DataFrame(columns=["item", "flavour", "quantity", "price", "total"])
        self.refresh_cart_view()

    def checkout(self):
        if self.controller.cart.empty:
            messagebox.showinfo("Empty", "Cart is empty")
            return
        if not messagebox.askyesno("Confirm", "Confirm payment and update stock?"): return
        
        try:
            self.controller.create_bill_table_if_not_exists()
            grand_total = 0
            for _, row in self.controller.cart.iterrows():
                grand_total += self.controller.update_stock_and_record_sale(row['item'], row['flavour'], int(row['quantity']), float(row['price']))
                self.controller.cursor.execute("INSERT INTO bill (item, flavour, quantity, total) VALUES (%s,%s,%s,%s)",
                                               (row['item'], row['flavour'], int(row['quantity']), float(row['total'])))
            self.controller.mydb.commit()
            messagebox.showinfo("Success", f"Payment successful! Total: ₹{grand_total:.2f}")
            self.clear_cart()
        except Exception as e:
            messagebox.showerror("Checkout Error", f"Failed to complete checkout: {e}")

class BillFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Recent Transactions", style="Header.TLabel").pack(pady=10)
        self.text = ScrolledText(self, font=("Courier New", 10), bg="#F5F5F5")
        self.text.pack(fill='both', expand=True, padx=20)
        ttk.Button(self, text="🔄 Refresh Bill", command=self.refresh).pack(pady=15)

    def refresh(self):
        try:
            self.controller.cursor.execute("SELECT sr, item, flavour, quantity, total FROM bill ORDER BY sr DESC LIMIT 15")
            rows = self.controller.cursor.fetchall()
            self.text.delete('1.0', tk.END)
            if not rows:
                self.text.insert(tk.END, "No recent transactions found.")
                return
            df = pd.DataFrame(rows, columns=["SR", "Item", "Flavour", "Qty", "Total"]).sort_values('SR')
            header = f"SWEETS 'N JOY BAKERY\nDate: {date.today()}\n" + "="*40 + "\n"
            content = df.to_string(index=False)
            footer = "\n" + "="*40 + f"\nGrand Total of displayed items: ₹{df['Total'].sum():.2f}"
            self.text.insert(tk.END, header + content + footer)
        except Exception as e:
            self.text.insert(tk.END, f"Error: {e}")

class FeedbackFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Customer Feedback", style="Header.TLabel").pack(pady=10)
        self.txt = ScrolledText(self, height=10, font=FONTS["normal"])
        self.txt.pack(fill='both', expand=False, padx=40, pady=10)
        ttk.Button(self, text="🚀 Submit Feedback", command=self.submit_feedback).pack(pady=15)

    def refresh(self): self.txt.delete('1.0', tk.END)

    def submit_feedback(self):
        fb = self.txt.get('1.0', tk.END).strip()
        if not fb:
            messagebox.showwarning("Empty", "Please write something before submitting")
            return
        try:
            self.controller.cursor.execute("CREATE TABLE IF NOT EXISTS feedback (id INT AUTO_INCREMENT PRIMARY KEY, text TEXT, date_ DATE)")
            self.controller.cursor.execute("INSERT INTO feedback (text, date_) VALUES (%s, %s)", (fb, date.today()))
            self.controller.mydb.commit()
            messagebox.showinfo("Thank You", "We appreciate your feedback!")
            self.txt.delete('1.0', tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save feedback: {e}")

class SalesLoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Center the login form
        container = tk.Frame(self, bg=COLORS["secondary"])
        container.place(relx=0.5, rely=0.4, anchor="center")
        
        ttk.Label(container, text="Employee Login", font=FONTS["header"]).pack(pady=20)
        
        form = tk.Frame(container, bg=COLORS["secondary"])
        form.pack()
        
        tk.Label(form, text="Employee ID:", bg=COLORS["secondary"]).grid(row=0, column=0, pady=10, sticky="e")
        self.id_entry = ttk.Entry(form)
        self.id_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(form, text="Password:", bg=COLORS["secondary"]).grid(row=1, column=0, pady=10, sticky="e")
        self.pw_entry = ttk.Entry(form, show='*')
        self.pw_entry.grid(row=1, column=1, pady=10)
        
        ttk.Button(container, text="🔓 Login", command=self.check_login).pack(pady=20)

    def reset(self):
        self.id_entry.delete(0, 'end')
        self.pw_entry.delete(0, 'end')

    def check_login(self):
        try:
            eid = int(self.id_entry.get())
        except:
            messagebox.showerror("Error", "Invalid Employee ID")
            return
        
        pw = self.pw_entry.get()
        try:
            self.controller.cursor.execute("SELECT pass FROM employee WHERE id=%s", (eid,))
            res = self.controller.cursor.fetchone()
            if res and pw == res[0]:
                self.controller.show_sales_report()
            else:
                messagebox.showerror("Denied", "Incorrect ID or Password")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

class SalesReportFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Sales Intelligence & Reports", style="Header.TLabel").pack(pady=10)

        # Button Grid
        btn_container = tk.Frame(self, bg=COLORS["secondary"])
        btn_container.pack(pady=10)

        btns = [
            ("💰 Total Sales", self.total_sales, 0, 0),
            ("🍰 Top Item", self.most_sold_item, 0, 1),
            ("🍓 Top Flavour", self.most_sold_flavour, 0, 2),
            ("📦 Stock Status", self.remaining_stock, 1, 0),
            ("🔮 7-Day Prediction", self.sales_prediction, 1, 1),
            ("⬅️ Logout", lambda: controller.show_frame('MenuFrame'), 1, 2)
        ]

        for text, cmd, r, c in btns:
            ttk.Button(btn_container, text=text, command=cmd).grid(row=r, column=c, padx=5, pady=5, sticky="ew")

        self.out_text = ScrolledText(self, height=12, font=("Courier New", 10))
        self.out_text.pack(fill='both', expand=True, padx=20, pady=10)
        self.plot_container = tk.Frame(self, bg=COLORS["secondary"])
        self.plot_container.pack(fill='both', expand=True)
        self.plot_canvas = None

    def reset(self):
        self.out_text.delete('1.0', tk.END)
        self.clear_plot()

    def clear_plot(self):
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None

    def total_sales(self):
        self.out_text.delete('1.0', tk.END)
        self.controller.cursor.execute("SELECT SUM(stock) FROM td_sale1")
        res = self.controller.cursor.fetchone()
        total = res[0] if res and res[0] is not None else 0
        self.out_text.insert(tk.END, f"TOTAL SALES REVENUE: ₹{total:,.2f}")

    def most_sold_item(self):
        self.out_text.delete('1.0', tk.END)
        try:
            self.controller.cursor.execute("CALL top_item1(@name, @qty)")
            self.controller.cursor.execute("SELECT @name, @qty")
            res = self.controller.cursor.fetchone()
            if res and res[0]:
                self.out_text.insert(tk.END, f"MOST POPULAR ITEM: {res[0]}\nTOTAL QUANTITY SOLD: {res[1]}")
            else:
                self.out_text.insert(tk.END, "No sales data available yet.")
        except Exception as e:
            self.out_text.insert(tk.END, f"Error calling procedure top_item1: {e}")

    def most_sold_flavour(self):
        self.out_text.delete('1.0', tk.END)
        try:
            self.controller.cursor.execute("CALL top_item4(@name, @qty)")
            self.controller.cursor.execute("SELECT @name, @qty")
            res = self.controller.cursor.fetchone()
            if res and res[0]:
                self.out_text.insert(tk.END, f"MOST POPULAR FLAVOUR: {res[0]}\nTOTAL QUANTITY SOLD: {res[1]}")
            else:
                self.out_text.insert(tk.END, "No sales data available yet.")
        except Exception as e:
            self.out_text.insert(tk.END, f"Error calling procedure top_item4: {e}")

    def remaining_stock(self):
        self.out_text.delete('1.0', tk.END)
        self.controller.cursor.execute("SELECT item, flavour, stock FROM inventory12")
        rows = self.controller.cursor.fetchall()
        if not rows:
            self.out_text.insert(tk.END, "No inventory data found.")
            return
        df = pd.DataFrame(rows, columns=['Item', 'Flavour', 'Stock Balance'])
        self.out_text.insert(tk.END, "CURRENT STOCK STATUS:\n" + "="*30 + "\n" + df.to_string(index=False))

    def sales_prediction(self):
        self.out_text.delete('1.0', tk.END)
        df = self.controller.aggregate_sales_by_date()
        if df.empty or len(df) < 2:
            self.out_text.insert(tk.END, "Not enough historical data for prediction (min 2 days required).")
            return
        
        try:
            full_dates = pd.date_range(start=df['date'].min(), end=df['date'].max())
            df_daily = df.set_index('date').reindex(full_dates, fill_value=0).rename_axis('date').reset_index()
            df_daily['day_of_week'] = df_daily['date'].dt.dayofweek
            
            X, y = df_daily[['day_of_week']], df_daily['quantity']
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            last_date = df_daily['date'].max()
            future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
            future_features = pd.DataFrame({'day_of_week': [d.dayofweek for d in future_dates]})
            future_preds = model.predict(future_features)

            out = "FORECASTED SALES (NEXT 7 DAYS):\n" + "="*30 + "\n"
            for d, p in zip(future_dates, future_preds):
                out += f"{d.date()} ({d.strftime('%a')}): {p:,.2f} units\n"
            self.out_text.insert(tk.END, out)

            # Visualizing the forecast
            self.clear_plot()
            fig = Figure(figsize=(6, 3), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(df_daily['date'], df_daily['quantity'], marker='o', color=COLORS["primary"], label='Historical')
            ax.plot(future_dates, future_preds, marker='x', linestyle='--', color=COLORS["accent"], label='Forecast')
            ax.set_title("Sales Forecast", fontsize=10)
            ax.legend(fontsize=8)
            fig.autofmt_xdate()
            
            self.plot_canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
            self.plot_canvas.draw()
            self.plot_canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            self.out_text.insert(tk.END, f"Prediction error: {e}")

if __name__ == '__main__':
    try:
        app = BakeryApp()
        app.mainloop()
    except Exception as e:
        print(f"Application failed to start: {e}")
