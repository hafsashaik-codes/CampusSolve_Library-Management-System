import json
import csv
import os
from datetime import date, timedelta
from collections import Counter

DATA_FILE = "library_records.json"
REPORT_DIR = "library_reports"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                return (data["books"], data["members"],
                        data["transactions"])
            except (ValueError, KeyError):
                pass
    return [], [], []


def save_data(books, members, transactions):
    data = {
        "books": books,
        "members": members,
        "transactions": transactions
    }

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

    print("Records saved successfully!")


def add_book(books):
    book_id = input("Enter Book ID: ")

    if any(b["id"] == book_id for b in books):
        print("Book ID already exists!")
        return

    title = input("Enter Book Title: ")
    author = input("Enter Author: ")
    category = input("Enter Category: ")

    try:
        copies = int(input("Enter Number of Copies: "))
        if copies <= 0:
            raise ValueError
    except ValueError:
        print("Enter a valid positive number!")
        return

    books.append({
        "id": book_id,
        "title": title,
        "author": author,
        "category": category,
        "total": copies,
        "available": copies
    })

    print("Book added successfully!")


def view_books(books):
    if not books:
        print("No books available!")
        return

    print("\n--- BOOK DETAILS ---")

    for book in books:
        print(
            book["id"], "|",
            book["title"], "|",
            book["author"], "|",
            book["category"], "|",
            "Available:", book["available"]
        )


def register_member(members):
    member_id = input("Enter Student ID: ")

    if any(m["id"] == member_id for m in members):
        print("Student already registered!")
        return

    name = input("Enter Student Name: ")
    department = input("Enter Department: ")
    phone = input("Enter Phone Number: ")

    members.append({
        "id": member_id,
        "name": name,
        "department": department,
        "phone": phone
    })

    print("Student registered successfully!")


def view_members(members):
    if not members:
        print("No registered students!")
        return

    print("\n--- STUDENT DETAILS ---")

    for member in members:
        print(
            member["id"], "|",
            member["name"], "|",
            member["department"], "|",
            member["phone"]
        )


def issue_book(books, members, transactions):
    book_id = input("Enter Book ID: ")
    member_id = input("Enter Student ID: ")

    book = next(
        (b for b in books if b["id"] == book_id), None
    )

    member = next(
        (m for m in members if m["id"] == member_id), None
    )

    if book is None:
        print("Book not found!")
    elif member is None:
        print("Student not found!")
    elif book["available"] == 0:
        print("Book is currently unavailable!")
    else:
        today = date.today()
        due_date = today + timedelta(days=14)

        book["available"] -= 1

        transactions.append({
            "book_id": book_id,
            "member_id": member_id,
            "title": book["title"],
            "member_name": member["name"],
            "issued": str(today),
            "due": str(due_date),
            "returned": ""
        })

        print("Book issued successfully!")
        print("Due Date:", due_date)


def return_book(books, transactions):
    book_id = input("Enter Book ID: ")
    member_id = input("Enter Student ID: ")

    for record in transactions:
        if (record["book_id"] == book_id
                and record["member_id"] == member_id
                and not record["returned"]):

            record["returned"] = str(date.today())

            for book in books:
                if book["id"] == book_id:
                    book["available"] += 1
                    break

            print("Book returned successfully!")
            return

    print("No active issue record found!")


def view_transactions(transactions):
    if not transactions:
        print("No transactions available!")
        return

    print("\n--- TRANSACTION HISTORY ---")

    for record in transactions:
        status = record["returned"] or "Not Returned"

        print(
            record["book_id"], "|",
            record["title"], "|",
            record["member_name"], "|",
            "Issued:", record["issued"], "|",
            "Due:", record["due"], "|",
            "Status:", status
        )


def search_records(books, members):
    keyword = input("Enter title, author or student name: ").lower()

    print("\n--- SEARCH RESULTS ---")

    for book in books:
        if (keyword in book["title"].lower()
                or keyword in book["author"].lower()):
            print("Book:", book["title"], "-", book["id"])

    for member in members:
        if keyword in member["name"].lower():
            print("Student:", member["name"], "-", member["id"])


def library_summary(books, members, transactions):
    issued = sum(
        1 for t in transactions if not t["returned"]
    )

    overdue = [
        t for t in transactions
        if not t["returned"]
        and date.fromisoformat(t["due"]) < date.today()
    ]

    categories = Counter(
        book["category"] for book in books
    )

    print("\n--- LIBRARY SUMMARY ---")
    print("Total Book Titles:", len(books))
    print("Total Copies:", sum(b["total"] for b in books))
    print("Available Copies:", sum(b["available"] for b in books))
    print("Registered Students:", len(members))
    print("Books Currently Issued:", issued)
    print("Overdue Books:", len(overdue))
    print("Book Categories:", dict(categories))


def export_reports(books, members, transactions):
    os.makedirs(REPORT_DIR, exist_ok=True)

    datasets = [
        ("books.csv", books),
        ("members.csv", members),
        ("transactions.csv", transactions)
    ]

    for filename, records in datasets:
        if not records:
            continue

        with open(
            os.path.join(REPORT_DIR, filename),
            "w",
            newline=""
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=records[0].keys()
            )
            writer.writeheader()
            writer.writerows(records)

    print("Reports exported successfully!")


def import_books(books):
    filename = input("Enter CSV file path: ")

    if not os.path.exists(filename):
        print("File not found!")
        return

    count = 0

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if any(b["id"] == row["id"] for b in books):
                continue

            try:
                copies = int(row["copies"])
                if copies <= 0:
                    continue
            except (ValueError, KeyError):
                continue

            books.append({
                "id": row["id"],
                "title": row["title"],
                "author": row["author"],
                "category": row["category"],
                "total": copies,
                "available": copies
            })

            count += 1

    print(count, "books imported successfully!")


def load_demo_data(books, members):
    if books or members:
        print("Demo data is already present!")
        return

    books.extend([
        {
            "id": "BK201",
            "title": "Python Made Simple",
            "author": "A. Kumar",
            "category": "Programming",
            "total": 4,
            "available": 4
        },
        {
            "id": "BK202",
            "title": "The Hidden Library",
            "author": "M. Rao",
            "category": "Fiction",
            "total": 3,
            "available": 3
        },
        {
            "id": "BK203",
            "title": "Basics of Networks",
            "author": "S. Iyer",
            "category": "Technology",
            "total": 2,
            "available": 2
        },
        {
            "id": "BK204",
            "title": "Design Thinking Guide",
            "author": "R. Das",
            "category": "Education",
            "total": 5,
            "available": 5
        }
    ])

    members.extend([
        {
            "id": "ST201",
            "name": "Ananya Sharma",
            "department": "CSE",
            "phone": "9000011122"
        },
        {
            "id": "ST202",
            "name": "Rahul Verma",
            "department": "IT",
            "phone": "9000033344"
        },
        {
            "id": "ST203",
            "name": "Meera Nair",
            "department": "ECE",
            "phone": "9000055566"
        }
    ])

    print("Second attempt demo data loaded!")


def display_menu():
    print("\n========== CAMPUSSOLVE LIBRARY DESK ==========")
    print("1. Add Book")
    print("2. View Books")
    print("3. Register Student")
    print("4. View Students")
    print("5. Issue Book")
    print("6. Return Book")
    print("7. View Transactions")
    print("8. Search Records")
    print("9. Library Summary")
    print("10. Export Reports")
    print("11. Import Books")
    print("12. Load Demo Data")
    print("0. Save and Exit")
    print("==============================================")


def main():
    books, members, transactions = load_data()

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            add_book(books)

        elif choice == "2":
            view_books(books)

        elif choice == "3":
            register_member(members)

        elif choice == "4":
            view_members(members)

        elif choice == "5":
            issue_book(books, members, transactions)

        elif choice == "6":
            return_book(books, transactions)

        elif choice == "7":
            view_transactions(transactions)

        elif choice == "8":
            search_records(books, members)

        elif choice == "9":
            library_summary(books, members, transactions)

        elif choice == "10":
            export_reports(books, members, transactions)

        elif choice == "11":
            import_books(books)

        elif choice == "12":
            load_demo_data(books, members)

        elif choice == "0":
            save_data(books, members, transactions)
            print("Thank you for using CampusSolve!")
            break

        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
    
        