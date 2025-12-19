import psycopg2
from psycopg2 import sql
def get_connection():
    return psycopg2.connect(
        dbname="restaurant_db",
        user="postgres",
        password="08121378",
        host="localhost",
        port="5432"
    )

def add_menu_item(name, price):
    """Add a new item to the menu"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu_items (name, price) VALUES (%s, %s)",
            (name, price)
        )
        conn.commit()
        print(f"{name} added successfully!")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

def edit_menu_item_price(item_id, new_price):
    """Edit the price of a menu item"""
    if new_price < 0:
        print("Invalid price!")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
# Check if item exists
        cursor.execute("SELECT name FROM menu_items WHERE id=%s", (item_id,))
        item = cursor.fetchone()
        if not item:
            print("Menu item not found!")
            return

# Update price
        cursor.execute("UPDATE menu_items SET price=%s WHERE id=%s", (new_price, item_id))
        conn.commit()
        print(f"Price of {item[0]} updated to {new_price}!")

    except Exception as e:
        print("Error updating price:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def show_menu():
    """Show the list of menu items"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, price FROM menu_items ORDER BY id")
        items = cursor.fetchall()
        
        print("---- Menu ----")
        for item in items:
            print(f"{item[0]}. {item[1]} - {item[2]}")
            
    except Exception as e:
        print("Error fetching menu:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def show_tables_status():
    """Show status of all tables"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT table_number, status FROM restaurant_tables ORDER BY table_number"
        )
        tables = cursor.fetchall()

        print("---- Tables Status ----")
        for table in tables:
            print(f"Table {table[0]} : {table[1]}")

    except Exception as e:
        print("Error fetching tables:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_table_status(table_number, new_status):
    """Update table status (available / occupied)"""
    if new_status not in ("available", "occupied"):
        print("Invalid status!")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT status FROM restaurant_tables WHERE table_number=%s",
            (table_number,)
        )
        result = cursor.fetchone()

        if not result:
            print("Table not found!")
            return

        # Update status
        cursor.execute(
            "UPDATE restaurant_tables SET status=%s WHERE table_number=%s",
            (new_status, table_number)
        )
        conn.commit()
        print(f"Table {table_number} status updated to {new_status}")

    except Exception as e:
        print("Error updating table status:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def add_table(table_number):
    """Add a new table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if table number already exists
        cursor.execute(
            "SELECT id FROM restaurant_tables WHERE table_number=%s",
            (table_number,)
        )
        if cursor.fetchone():
            print("Table number already exists!")
            return

        cursor.execute(
            "INSERT INTO restaurant_tables (table_number) VALUES (%s)",
            (table_number,)
        )
        conn.commit()
        print(f"Table {table_number} added successfully")

    except Exception as e:
        print("Error adding table:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def remove_table(table_number):
    """Remove a table (only if available)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

# Check if table exists and get its status
        cursor.execute(
            "SELECT status FROM restaurant_tables WHERE table_number=%s",
            (table_number,)
        )
        result = cursor.fetchone()

        if not result:
            print("Table not found!")
            return

        if result[0] != "available":
            print("Table is occupied and cannot be removed!")
            return

# Remove table
        cursor.execute(
            "DELETE FROM restaurant_tables WHERE table_number=%s",
            (table_number,)
        )
        conn.commit()
        print(f"Table {table_number} removed successfully")

    except Exception as e:
        print("Error removing table:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_order(table_number):
    """Create a new order"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

# Check table and its status
        cursor.execute(
            "SELECT id, status FROM restaurant_tables WHERE table_number=%s",
            (table_number,)
        )
        table = cursor.fetchone()

        if not table:
            print("Table not found!")
            return

        if table[1] != "available":
            print("Table is occupied, cannot create order!")
            return

        table_id = table[0]

# Create order
        cursor.execute(
            "INSERT INTO orders (table_id, status) VALUES (%s, 'received')",
            (table_id,)
        )

# Update table status
        cursor.execute(
            "UPDATE restaurant_tables SET status='occupied' WHERE id=%s",
            (table_id,)
        )

        conn.commit()
        print("Order created successfully")

    except Exception as e:
        print("Error creating order:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_order_status(order_id, new_status):
    """Update order status"""
    if new_status not in ("received", "preparing", "ready", "paid"):
        print("Invalid order status!")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

# Check if order exists
        cursor.execute(
            "SELECT status FROM orders WHERE id=%s",
            (order_id,)
        )
        order = cursor.fetchone()

        if not order:
            print("Order not found!")
            return

# Update order status
        cursor.execute(
            "UPDATE orders SET status=%s WHERE id=%s",
            (new_status, order_id)
        )

# If order is paid, free the table
        if new_status == "paid":
            cursor.execute(
                """
                UPDATE restaurant_tables
                SET status='available'
                WHERE id = (
                    SELECT table_id FROM orders WHERE id=%s
                )
                """,
                (order_id,)
            )

        conn.commit()
        print(f"Order {order_id} status updated to {new_status}")

    except Exception as e:
        print("Error updating order status:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def show_active_orders():
    """Show active orders"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT o.id, t.table_number, o.status, o.order_time
            FROM orders o
            JOIN restaurant_tables t ON o.table_id = t.id
            WHERE o.status != 'paid'
            ORDER BY o.order_time
            """
        )
        orders = cursor.fetchall()

        print("---- Active Orders ----")
        for order in orders:
            print(
                f"Order {order[0]} | Table {order[1]} | Status {order[2]} | Time {order[3]}"
            )

    except Exception as e:
        print("Error fetching active orders:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def show_order_details(order_id):
    """Show order details using JOIN"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT m.name, d.quantity, m.price
            FROM order_details d
            JOIN menu_items m ON d.item_id = m.id
            WHERE d.order_id = %s
            """,
            (order_id,)
        )
        details = cursor.fetchall()

        if not details:
            print("No items found for this order")
            return

        print(f"---- Order {order_id} Details ----")
        total = 0
        for item in details:
            item_total = item[1] * item[2]
            total += item_total
            print(f"{item[0]} | Qty: {item[1]} | Price: {item[2]}")

        print(f"Total: {total}")

    except Exception as e:
        print("Error fetching order details:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_daily_sales_report():
    """Calculate total sales for today"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT SUM(m.price * d.quantity)
            FROM orders o
            JOIN order_details d ON o.id = d.order_id
            JOIN menu_items m ON d.item_id = m.id
            WHERE o.status = 'paid'
              AND DATE(o.order_time) = CURRENT_DATE
            """
        )
        total = cursor.fetchone()[0]

        if total is None:
            total = 0

        print(f"Total sales today: {total}")

    except Exception as e:
        print("Error calculating daily sales:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def manage_tables_menu():
    while True:
        print("\n--- Table Management ---")
        print("1. Add a new table")
        print("2. Remove a table")
        print("3. Back to main menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            table_number = input("Enter new table number: ")
            if table_number.isdigit():
                add_table(int(table_number))
            else:
                print("Invalid table number!")

        elif choice == "2":
            table_number = input("Enter table number to remove: ")
            if table_number.isdigit():
                remove_table(int(table_number))
            else:
                print("Invalid table number!")

        elif choice == "3":
            break

        else:
            print("Invalid choice!")

def main_menu():
    while True:
        print("\nRestaurant Management System")
        print("1. Show Menu")
        print("2. Show Table Status")
        print("3. Add New Order")
        print("4. Update Order Status")
        print("5. View Order Details & Total Price")
        print("6. Show Daily Sales Report")
        print("7. Manage Tables") 
        print("8. Add New Menu Item")
        print("9. Edit Menu Item Price")
        print("10. Exit") 
        choice = input("Enter your choice: ")

        if choice == "1":
            show_menu()

        elif choice == "2":
            show_tables_status()

        elif choice == "3":
            table_number = input("Enter table number for the order: ")
            if table_number.isdigit():
                add_order(int(table_number))
            else:
                print("Invalid table number!")

        elif choice == "4":
            order_id = input("Enter order ID to update: ")
            new_status = input("Enter new status (received/preparing/ready/paid): ")
            if order_id.isdigit():
                update_order_status(int(order_id), new_status)
            else:
                print("Invalid order ID!")

        elif choice == "5":
            order_id = input("Enter order ID to view details: ")
            if order_id.isdigit():
                show_order_details(int(order_id))
            else:
                print("Invalid order ID!")

        elif choice == "6":
            get_daily_sales_report()

        elif choice == "7":
            manage_tables_menu()

        elif choice == "8":
            name = input("Enter food name: ")
            price = input("Enter food price: ")
            if price.replace('.', '', 1).isdigit():
                add_menu_item(name, float(price))
            else:
                print("Invalid price!")

        elif choice == "9":
            item_id = input("Enter menu item ID to edit: ")
            new_price = input("Enter new price: ")
            if item_id.isdigit() and new_price.replace('.', '', 1).isdigit():
                edit_menu_item_price(int(item_id), float(new_price))
            else:
                print("Invalid input!")


        elif choice == "10":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main_menu()




