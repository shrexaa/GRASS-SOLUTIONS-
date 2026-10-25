from datetime import date, timedelta
from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

DB = Path(__file__).resolve().parent / "library.db"
st.set_page_config(page_title="Libra | Library Analytics", page_icon="📚", layout="wide")

def connect():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS books(
          book_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
          author TEXT NOT NULL, isbn TEXT UNIQUE, category TEXT NOT NULL,
          total_copies INTEGER NOT NULL CHECK(total_copies>=1),
          available_copies INTEGER NOT NULL CHECK(available_copies>=0 AND available_copies<=total_copies));
        CREATE TABLE IF NOT EXISTS members(
          member_id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE, joined_on TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS transactions(
          transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
          book_id INTEGER NOT NULL REFERENCES books(book_id),
          member_id INTEGER NOT NULL REFERENCES members(member_id),
          issue_date TEXT NOT NULL, due_date TEXT NOT NULL, return_date TEXT,
          status TEXT NOT NULL CHECK(status IN ('Issued','Returned')));
        """)
        if c.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            books = [
              ("Atomic Habits","James Clear","9780735211292","Self-help",5,3),
              ("The Alchemist","Paulo Coelho","9780062315007","Fiction",7,4),
              ("Clean Code","Robert C. Martin","9780132350884","Technology",4,2),
              ("Deep Work","Cal Newport","9781455586691","Productivity",3,1),
              ("Sapiens","Yuval Noah Harari","9780062316097","History",4,4),
              ("Ikigai","Héctor García","9780143130727","Self-help",5,3),
              ("The Pragmatic Programmer","Andrew Hunt","9780135957059","Technology",3,2),
              ("Pride and Prejudice","Jane Austen","9780141439518","Fiction",6,5),
              ("A Brief History of Time","Stephen Hawking","9780553380163","Science",3,3)]
            c.executemany("INSERT INTO books(title,author,isbn,category,total_copies,available_copies) VALUES(?,?,?,?,?,?)", books)
            today = date.today()
            members = [
              ("Aarav Sharma","aarav.sharma@example.com",(today-timedelta(days=180)).isoformat()),
              ("Ananya Gupta","ananya.gupta@example.com",(today-timedelta(days=150)).isoformat()),
              ("Rohan Mehta","rohan.mehta@example.com",(today-timedelta(days=120)).isoformat()),
              ("Priya Verma","priya.verma@example.com",(today-timedelta(days=90)).isoformat()),
              ("Kabir Singh","kabir.singh@example.com",(today-timedelta(days=60)).isoformat())]
            c.executemany("INSERT INTO members(full_name,email,joined_on) VALUES(?,?,?)", members)
            tx = [
              (1,1,-4,10,None,"Issued"),(3,2,-18,-4,None,"Issued"),
              (4,3,-3,11,None,"Issued"),(2,4,-24,-10,-9,"Returned"),
              (6,5,-2,12,None,"Issued"),(7,1,-32,-18,-20,"Returned")]
            c.executemany("""INSERT INTO transactions(book_id,member_id,issue_date,due_date,return_date,status)
              VALUES(?,?,?,?,?,?)""", [(b,m,(today+timedelta(days=i)).isoformat(),
              (today+timedelta(days=d)).isoformat(),
              (today+timedelta(days=r)).isoformat() if r is not None else None,s)
              for b,m,i,d,r,s in tx])

def df(sql, params=()):
    with connect() as c:
        return pd.read_sql_query(sql, c, params=params)

def run(sql, params=()):
    with connect() as c:
        c.execute(sql, params)
        c.commit()

def books_data():
    return df("SELECT * FROM books ORDER BY title")

def members_data():
    return df("SELECT * FROM members ORDER BY full_name")

def tx_data():
    t = df("""SELECT t.transaction_id,b.book_id,b.title,b.author,b.category,
      m.member_id,m.full_name,m.email,t.issue_date,t.due_date,t.return_date,t.status
      FROM transactions t JOIN books b ON b.book_id=t.book_id
      JOIN members m ON m.member_id=t.member_id ORDER BY t.transaction_id DESC""")
    if not t.empty:
        t["issue_date"] = pd.to_datetime(t["issue_date"])
        t["due_date"] = pd.to_datetime(t["due_date"])
        t["return_date"] = pd.to_datetime(t["return_date"])
        t["overdue"] = (t.status == "Issued") & (t.due_date < pd.Timestamp(date.today()))
    else:
        t["overdue"] = pd.Series(dtype=bool)
    return t

init_db()
st.markdown("""<style>
.block-container{padding-top:1.6rem;max-width:1450px}
.hero{padding:1.35rem 1.5rem;border-radius:18px;background:linear-gradient(115deg,#263f9e,#5275e8);color:white;margin-bottom:1rem}
.hero h1{color:white;margin:0}.hero p{color:#e4eaff;margin:.4rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #e7ebf4;padding:14px 16px;border-radius:14px}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 📚 Libra")
    st.caption("LIBRARY MANAGEMENT & ANALYTICS")
    page = st.radio("NAVIGATION", ["Overview","Book collection","Members","Issue & return","Data insights"])
    st.divider()
    st.caption("Python · SQLite · Pandas · Plotly")

st.markdown('<div class="hero"><h1>Libra Library Management</h1><p>Manage your collection, track circulation, and turn library records into useful insights.</p></div>', unsafe_allow_html=True)
books = books_data()
members = members_data()
tx = tx_data()
total = int(books.total_copies.sum()) if not books.empty else 0
available = int(books.available_copies.sum()) if not books.empty else 0
out = total - available
overdue = tx[tx.overdue] if not tx.empty else tx
active = tx[tx.status == "Issued"] if not tx.empty else tx

def book_table(frame):
    cols = ["book_id","title","author","isbn","category","total_copies","available_copies"]
    st.dataframe(frame[cols].rename(columns={"book_id":"ID","title":"Title","author":"Author","isbn":"ISBN","category":"Category","total_copies":"Total copies","available_copies":"Available"}), use_container_width=True, hide_index=True)

if page == "Overview":
    st.subheader("Library at a glance")
    a,b,c,d = st.columns(4)
    a.metric("Total book copies", total)
    b.metric("Unique titles", len(books))
    c.metric("Copies currently out", out)
    d.metric("Overdue loans", len(overdue))
    left,right = st.columns(2)
    with left:
        st.markdown("### Collection by category")
        if not books.empty:
            cat = books.groupby("category",as_index=False).total_copies.sum().sort_values("total_copies",ascending=False)
            fig = px.bar(cat,x="category",y="total_copies",color="category",labels={"category":"Category","total_copies":"Copies"})
            fig.update_layout(showlegend=False,margin=dict(t=15,b=10))
            st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("### Copy availability")
        fig = px.pie(names=["Available","On loan"],values=[available,out],hole=.58,color_discrete_sequence=["#5275e8","#f0ad4e"])
        fig.update_layout(margin=dict(t=15,b=10))
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Collection")
    book_table(books.tail(6))
    st.markdown("### Recent transactions")
    if not tx.empty:
        recent = tx[["transaction_id","title","full_name","issue_date","due_date","status","overdue"]].copy()
        recent["status"] = recent.apply(lambda r:"Overdue" if r.overdue else r.status,axis=1)
        recent["issue_date"] = recent.issue_date.dt.strftime("%d %b %Y")
        recent["due_date"] = recent.due_date.dt.strftime("%d %b %Y")
        st.dataframe(recent.drop(columns="overdue").rename(columns={"transaction_id":"Txn ID","title":"Book","full_name":"Member","issue_date":"Issue date","due_date":"Due date","status":"Status"}).head(8),use_container_width=True,hide_index=True)

elif page == "Book collection":
    st.subheader("Book collection")
    with st.expander("➕ Add a book"):
        with st.form("add_book",clear_on_submit=True):
            x,y = st.columns(2)
            title=x.text_input("Book title *")
            author=y.text_input("Author *")
            isbn=x.text_input("ISBN (optional)")
            category=y.selectbox("Category",["Fiction","Technology","Self-help","Productivity","History","Science","Biography","Business","Other"])
            copies=st.number_input("Total copies",min_value=1,max_value=10000,value=1)
            ok=st.form_submit_button("Add book",type="primary")
            if ok:
                if not title.strip() or not author.strip(): st.error("Title and author are required.")
                else:
                    try:
                        run("INSERT INTO books(title,author,isbn,category,total_copies,available_copies) VALUES(?,?,?,?,?,?)",(title.strip(),author.strip(),isbn.strip() or None,category,int(copies),int(copies)))
                        st.success("Book added."); st.rerun()
                    except sqlite3.IntegrityError: st.error("That ISBN already exists. Leave ISBN blank if unavailable.")
    books=books_data()
    q=st.text_input("🔎 Search title, author, ISBN or category")
    filtered=books[books.apply(lambda r:q.lower() in " ".join(map(str,r.values)).lower(),axis=1)] if q else books
    book_table(filtered)
    if not books.empty:
        st.markdown("### Edit a book")
        options={f"{r.title} — {r.author} (ID {r.book_id})":r for r in books.itertuples()}
        label=st.selectbox("Choose title",list(options))
        chosen=options[label]
        with st.form("edit_book"):
            x,y=st.columns(2)
            nt=x.text_input("Title",chosen.title); na=y.text_input("Author",chosen.author)
            ni=x.text_input("ISBN",chosen.isbn or "")
            cats=["Fiction","Technology","Self-help","Productivity","History","Science","Biography","Business","Other"]
            if chosen.category not in cats: cats.append(chosen.category)
            nc=y.selectbox("Category",cats,index=cats.index(chosen.category))
            out_copies=int(chosen.total_copies-chosen.available_copies)
            ncopy=st.number_input("Total copies",min_value=max(1,out_copies),max_value=10000,value=int(chosen.total_copies))
            save=st.form_submit_button("Save changes")
            if save:
                try:
                    run("UPDATE books SET title=?,author=?,isbn=?,category=?,total_copies=?,available_copies=? WHERE book_id=?",(nt.strip(),na.strip(),ni.strip() or None,nc,int(ncopy),int(ncopy)-out_copies,chosen.book_id))
                    st.success("Book updated.");st.rerun()
                except sqlite3.IntegrityError: st.error("That ISBN is already assigned.")
        st.markdown("### Delete a book")
        st.caption("Titles with transaction history cannot be deleted, preserving the audit trail.")
        delete_label=st.selectbox("Select book to delete",list(options),key="delete_book")
        if st.button("Delete selected book"):
            bid=options[delete_label].book_id
            if df("SELECT COUNT(*) AS n FROM transactions WHERE book_id=?",(bid,)).iloc[0]["n"]:
                st.error("This book has transaction history and cannot be deleted.")
            else:
                run("DELETE FROM books WHERE book_id=?",(bid,));st.success("Deleted.");st.rerun()

elif page == "Members":
    st.subheader("Library members")
    with st.expander("➕ Register a member"):
        with st.form("add_member",clear_on_submit=True):
            name=st.text_input("Full name *");email=st.text_input("Email address *")
            ok=st.form_submit_button("Register member",type="primary")
            if ok:
                if not name.strip() or "@" not in email or "." not in email.split("@")[-1]:
                    st.error("Enter a name and valid email.")
                else:
                    try:
                        run("INSERT INTO members(full_name,email,joined_on) VALUES(?,?,?)",(name.strip(),email.strip().lower(),date.today().isoformat()))
                        st.success("Member registered.");st.rerun()
                    except sqlite3.IntegrityError: st.error("That email is already registered.")
    members=members_data();tx=tx_data()
    if not members.empty:
        counts=tx[tx.status=="Issued"].groupby("member_id").size().to_dict() if not tx.empty else {}
        members["Books currently out"]=members.member_id.map(counts).fillna(0).astype(int)
        st.dataframe(members.rename(columns={"member_id":"Member ID","full_name":"Name","email":"Email","joined_on":"Joined on"}),use_container_width=True,hide_index=True)
        st.download_button("Download members CSV",members.to_csv(index=False).encode("utf-8"),"library_members.csv","text/csv")

elif page == "Issue & return":
    st.subheader("Issue & return desk")
    a,b,c=st.columns(3);a.metric("Currently issued",len(active));b.metric("Overdue",len(overdue));c.metric("Returned",int((tx.status=="Returned").sum()) if not tx.empty else 0)
    with st.expander("📤 Issue a book",expanded=True):
        available_books=books[books.available_copies>0]
        if available_books.empty or members.empty:
            st.warning("Add a member and ensure at least one book copy is available.")
        else:
            book_map={f"{r.title} — {r.author} ({r.available_copies} available)":int(r.book_id) for r in available_books.itertuples()}
            member_map={f"{r.full_name} ({r.email})":int(r.member_id) for r in members.itertuples()}
            with st.form("issue_form"):
                selected_book=st.selectbox("Book",list(book_map));selected_member=st.selectbox("Member",list(member_map))
                issue_day=st.date_input("Issue date",date.today())
                due_day=st.date_input("Due date",date.today()+timedelta(days=14),min_value=date.today())
                ok=st.form_submit_button("Confirm issue",type="primary")
                if ok:
                    if due_day<issue_day: st.error("Due date must not be before issue date.")
                    else:
                        bid=book_map[selected_book]
                        with connect() as con:
                            row=con.execute("SELECT available_copies FROM books WHERE book_id=?",(bid,)).fetchone()
                            if not row or row[0]<1: st.error("No copies available.")
                            else:
                                con.execute("UPDATE books SET available_copies=available_copies-1 WHERE book_id=?",(bid,))
                                con.execute("INSERT INTO transactions(book_id,member_id,issue_date,due_date,status) VALUES(?,?,?,?, 'Issued')",(bid,member_map[selected_member],issue_day.isoformat(),due_day.isoformat()))
                                con.commit();st.success("Book issued.");st.rerun()
    st.markdown("### Transaction history")
    tx=tx_data()
    if not tx.empty:
        disp=tx[["transaction_id","title","full_name","issue_date","due_date","return_date","status","overdue"]].copy()
        disp["Status"]=disp.apply(lambda r:"Overdue" if r.overdue else r.status,axis=1)
        for col in ["issue_date","due_date","return_date"]: disp[col]=disp[col].dt.strftime("%d %b %Y")
        st.dataframe(disp.drop(columns="overdue").rename(columns={"transaction_id":"Txn ID","title":"Book","full_name":"Member","issue_date":"Issue date","due_date":"Due date","return_date":"Return date"}),use_container_width=True,hide_index=True)
        outstanding=tx[tx.status=="Issued"]
        if not outstanding.empty:
            tx_map={f"#{r.transaction_id} · {r.title} — {r.full_name} (due {r.due_date.date()})":int(r.transaction_id) for r in outstanding.itertuples()}
            with st.form("return_form"):
                chosen=st.selectbox("Choose loan to return",list(tx_map));return_day=st.date_input("Return date",date.today())
                ok=st.form_submit_button("Record return")
                if ok:
                    tid=tx_map[chosen]
                    with connect() as con:
                        row=con.execute("SELECT book_id,status FROM transactions WHERE transaction_id=?",(tid,)).fetchone()
                        if row and row[1]=="Issued":
                            con.execute("UPDATE transactions SET status='Returned',return_date=? WHERE transaction_id=?",(return_day.isoformat(),tid))
                            con.execute("UPDATE books SET available_copies=MIN(total_copies,available_copies+1) WHERE book_id=?",(row[0],))
                            con.commit()
                    st.success("Return recorded.");st.rerun()
        st.download_button("Download transactions CSV",tx.drop(columns="overdue").to_csv(index=False).encode("utf-8"),"library_transactions.csv","text/csv")
    else: st.info("No transactions yet.")

elif page == "Data insights":
    st.subheader("Data Science insights")
    st.caption("Exploratory data analysis based on the current database records.")
    a,b,c=st.columns(3)
    a.metric("Availability rate",f"{(available/total*100):.1f}%" if total else "0%")
    b.metric("Titles in collection",len(books))
    c.metric("Overdue loans",len(overdue))
    left,right=st.columns(2)
    with left:
        st.markdown("### Category distribution")
        if not books.empty:
            cat=books.groupby("category",as_index=False).total_copies.sum().sort_values("total_copies",ascending=False)
            fig=px.bar(cat,x="category",y="total_copies",color="category",labels={"category":"Category","total_copies":"Copies"})
            fig.update_layout(showlegend=False);st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("### Most borrowed titles")
        if not tx.empty:
            popular=tx.groupby("title",as_index=False).size().rename(columns={"size":"Transactions"}).sort_values("Transactions",ascending=True).tail(10)
            fig=px.bar(popular,x="Transactions",y="title",orientation="h",labels={"title":"Book"})
            st.plotly_chart(fig,use_container_width=True)
        else: st.info("Add transactions to see popular titles.")
    st.markdown("### Findings from current data")
    cats=books.groupby("category").total_copies.sum().sort_values(ascending=False) if not books.empty else pd.Series(dtype=int)
    if len(cats): st.markdown(f"- **Largest category:** {cats.index[0]} has {int(cats.iloc[0])} copies.")
    if not tx.empty:
        popular=tx.title.value_counts()
        st.markdown(f"- **Most frequently recorded title:** {popular.index[0]} ({int(popular.iloc[0])} transactions in the current dataset).")
    st.markdown(f"- **Availability:** {available} of {total} copies are available ({(available/total*100):.1f}% if total else 0%).")
    st.markdown(f"- **Overdue follow-up:** {len(overdue)} active loan(s) are past their due date.")
    st.info("The included data is synthetic demonstration data. Use real, authorized data only if you have permission.")
    st.download_button("Download book analysis CSV",books.to_csv(index=False).encode("utf-8"),"library_books_analysis.csv","text/csv")
    if not tx.empty: st.download_button("Download transaction analysis CSV",tx.drop(columns="overdue").to_csv(index=False).encode("utf-8"),"library_transactions_analysis.csv","text/csv")
