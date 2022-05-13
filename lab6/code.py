from tkinter import *
from tkinter import ttk
from typing import List
import mysql.connector
from datetime import datetime

class MainWindow:
    def __init__(self, root, cnx) -> None:
        self.cnx = cnx
        self.root = root
        self.user = None
        
        root.title("Main window")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.minsize(720, 600)

        mainframe = ttk.Frame(root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)

        datalist = []
        strlist = []
        datavar = StringVar(value=datalist)        
        data = Listbox(mainframe, listvariable=datavar, height=10, activestyle="none")
        data.grid(column=0, row=0, sticky=(N, W, E, S))


        toolframe = ttk.Frame(root)
        toolframe.grid(column=1, row=0, sticky=(N, W, E, S))
        toolframe.columnconfigure(0, weight=1)
        toolframe.columnconfigure(1, weight=1)

        self.status = ttk.Label(toolframe, text="Status: guest", anchor=E)
        self.status.grid(column=0, row=0, columnspan=2, sticky=(N, W, E, S))

        tablebox = ttk.Combobox(toolframe, state="readonly")
        tablebox.grid(column=0, columnspan=2, row=1, sticky=(N, W, E, S))
        tablebox["values"] = ("book", "author", "series") 
        
        ttk.Button(toolframe, command=self.login_window, text="Sign in").grid(row=2, column=0, sticky=(N, W, E, S))
        ttk.Button(toolframe, command=self.register_window, text="Register").grid(row=2, column=1, sticky=(N, W, E, S))

        self.admin_button = ttk.Button(toolframe, command=self.admin, text="Admin", state="disabled")
        self.admin_button.grid(column=0, columnspan=2, row=3, sticky=(N, W, E, S))

        def on_review_button(*_):
            if self.user is None:
                return
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            id = datalist[index][0]
            if tablebox.get() != "book":
                return
            self.review_window(id)
        self.review_button = ttk.Button(toolframe, command=on_review_button, text="Add review", state="disabled")
        self.review_button.grid(column=0, columnspan=2, row=4, sticky=(N, W, E, S))

        def on_rating_button(*_):
            if self.user is None:
                return
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            id = datalist[index][0]
            if tablebox.get() != "book":
                return
            self.rating_window(id)
        self.rating_button = ttk.Button(toolframe, command=on_rating_button, text="Add rating", state="disabled")
        self.rating_button.grid(column=0, columnspan=2, row=5, sticky=(N, W, E, S))

        info = Text(toolframe, width=50, height=15, state="disabled")
        info.grid(column=0, columnspan=2, row=6, sticky=(W, E))

        def on_combobox_selectdsfsa():
            table_name = tablebox.get()
            try:
                cur = self.cnx.cursor()
                datalist.clear()
                strlist.clear()
                cur.callproc(f"get_{table_name}")                
                for elem in cur.stored_results():
                    res = elem.fetchall()
                    [datalist.append(item) for item in res]
                    for elem in datalist:
                        strlist.append(self.data_to_str(elem, table_name))
                datavar.set(strlist)
            except Exception as e:
                print(e)
            finally:
                cur.close()
            data.focus()


        def on_list_select(*_):
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            table_name = tablebox.get()
            info.configure(state="normal")
            info.delete("1.0", END)
            try:
                cur = self.cnx.cursor()
                id = datalist[index][0]
                if table_name == "book":
                    cur.callproc("getauthors_bookid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Authors:\n")
                            for author in res:
                                info.insert(END, f"  {author[1]} {author[2]}\n")
                    cur.callproc("getseries_bookid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Series:\n")
                            for series in res:
                                info.insert(END, f"  {series[1]}\n")

                elif table_name == "author":
                    cur.callproc("getbooks_authorid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Books:\n")
                            for book in res:
                                info.insert(END, f"  name={book[1]}; genre_id={book[2]}\n")
                elif table_name == "series":
                    cur.callproc("getbooks_seriesid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Books:\n")
                            for book in res:
                                info.insert(END, f"  name={book[1]}; genre_id={book[2]}\n")
            except Exception as e:
                print(e)
            finally:
                cur.close() 
                info.configure(state="disabled")

        data.bind("<<ListboxSelect>>", on_list_select)
        tablebox.bind("<<ComboboxSelected>>", lambda _: on_combobox_select())
        tablebox.current(0)
        on_combobox_select()

    def on_status_change(self):
        if self.user == None:
            self.status["text"] = "Status: guest"
            self.review_button.state(["disabled"])
            self.rating_button.state(["disabled"])
        else:
            self.status["text"] = f"Status: {self.user.name} ({self.user.role})"
            self.review_button.state(["!disabled"])
            self.rating_button.state(["!disabled"])
            if self.user.role == "admin":
                self.admin_button.state(["!disabled"])
                return
        self.admin_button.state(["disabled"])


    def review_window(self, book_id):
        top = Toplevel()
        top.title("Add review")
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))        
        
        review_text = Text(mainframe, width=40, height=10)
        review_text.grid(column=0, row=0)

        info = ttk.Label(mainframe)
        info.grid(column=0, row=1)

        def on_button(*_):
            if self.user is None:
                info["text"] = "guest cant add review"
            try:
                cur = self.cnx.cursor()
                content = review_text.get("1.0", END)
                args = [content[:1024], book_id] # isob
                cur.callproc("add_review", args)
                cur.execute("select last_insert_id()")
                review_id = cur.fetchall()[0][0]
                self.cnx.commit()                
                cur.callproc("add_review_user", [review_id, self.user.id])
                cur.callproc("add_log", [datetime.today(), f"review id{review_id} on book id:{book_id} from user id:{self.user.id}"])
                self.cnx.commit()
                info["text"] = f"review {review_id} added"
            except Exception as e:
                print(e)
            finally:
                cur.close()
        btn = ttk.Button(mainframe, text="Add review", command=on_button)
        btn.grid(column=0, row=2, sticky=(W, E))

        top.mainloop()

    def rating_window(self, book_id):
        top = Toplevel()
        top.title("Add rating")
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))        
        
        spinval = StringVar(value=10)
        review_text = ttk.Spinbox(mainframe, from_=1.0, to=10.0, state="readonly", textvariable=spinval)
        review_text.grid(column=0, row=0)

        info = ttk.Label(mainframe)
        info.grid(column=0, row=1)

        def on_button(*_):
            if self.user is None:
                info["text"] = "guest cant add rating"
            try:
                cur = self.cnx.cursor()
                rating = spinval.get()
                args = [rating, book_id]
                cur.callproc("add_rating", args)
                cur.execute("select last_insert_id()")
                rating_id = cur.fetchall()[0][0]
                self.cnx.commit()                
                cur.callproc("add_rating_user", [rating_id, self.user.id])
                cur.callproc("add_log", [datetime.today(), f"rating id:{rating_id} on book id:{book_id} from user id:{self.user.id}"])
                self.cnx.commit()
                info["text"] = f"rating {rating} added"
            except Exception as e:
                print(e)
            finally:
                cur.close()
        btn = ttk.Button(mainframe, text="Add rating", command=on_button)
        btn.grid(column=0, row=2, sticky=(W, E))

        top.mainloop()

    def login_window(self):
        top = Toplevel()
        top.title("Sign in")
        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        ttk.Label(mainframe, text="username").grid(column=0, row=0)
        namevar = StringVar()
        name_entry = ttk.Entry(mainframe, textvariable=namevar)
        name_entry.grid(column=1, row=0)   
        ttk.Label(mainframe, text="password").grid(column=0, row=1)
        passwordvar = StringVar()
        password_entry = ttk.Entry(mainframe, textvariable=passwordvar, show="*")
        password_entry.grid(column=1, row=1)
        info = ttk.Label(mainframe)
        info.grid(column=0, columnspan=2, row=3, sticky=(N, W, E, S))

        def foo(*args):
            if len(namevar.get()) == 0:
                info["text"] = "Enter username"
                return
            if len(passwordvar.get()) < 4:
                info["text"] = "Wrong password"
                return

            # isob
            if len(namevar.get()) > 32:
                info["text"] = "Too long name"
                return
            if len(passwordvar.get()) > 32:
                info["text"] = "Too long password"
                return
            
            try:
                cur = self.cnx.cursor()
                cur.callproc("get_user_name", [namevar.get()]) # isob
                user = None
                for elem in cur.stored_results():
                    res = elem.fetchall()
                    if len(res) == 0:
                        info["text"] = "User not found"
                        raise ValueError("User not found")
                    user = res[0]
                if user[2] != passwordvar.get():
                    info["text"] = "Wrong password"
                    raise ValueError("Wrong password")                    
                self.user = User(user[0], user[1], user[3])
                cur.callproc("add_log", [datetime.today(), f"user id:{self.user.id} login"])
                self.cnx.commit()
            except Exception as e:
                print(e)
            finally:
                cur.close()
            self.on_status_change()
            top.destroy()
            
            
        ttk.Button(mainframe, command=foo, text="Sign in").grid(column=0, columnspan=2, row=2, sticky=(W, E, N, S))
        
        mainframe.rowconfigure(2, weight=1)
        mainframe.columnconfigure(1, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=2)

        top.bind("<Return>", foo)
        
        def name_bind(*args):
            info["text"] = "Enter name"
        name_entry.bind("<FocusIn>", name_bind)
        def password_bind(*args):
            info["text"] = "Enter password"
        password_entry.bind("<FocusIn>", password_bind)
        name_entry.focus()

        top.mainloop()

    def register_window(self):
        top = Toplevel()
        top.title("Register")
        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        ttk.Label(mainframe, text="username").grid(column=0, row=0)
        namevar = StringVar()
        name_entry = ttk.Entry(mainframe, textvariable=namevar)
        name_entry.grid(column=1, row=0)   
        ttk.Label(mainframe, text="password").grid(column=0, row=1)
        passwordvar = StringVar()
        password_entry = ttk.Entry(mainframe, textvariable=passwordvar)
        password_entry.grid(column=1, row=1)
        info = ttk.Label(mainframe)
        info.grid(column=0, columnspan=2, row=3, sticky=(N, W, E, S))

        def foo(*args):
            if len(namevar.get()) == 0:
                info["text"] = "Enter username"
                return
            if len(passwordvar.get()) < 4:
                info["text"] = "Password too short"
                return

            # isob
            if len(namevar.get()) > 32:
                info["text"] = "Too long name"
                return
            if len(passwordvar.get()) > 32:
                info["text"] = "Too long password"
                return

            try:
                cur = self.cnx.cursor()
                cur.callproc("get_user_name", [namevar.get()])
                res = None
                for elem in cur.stored_results():
                    res = elem.fetchall()
                    if len(res) > 0:
                        info["text"] = "Username already taken. Choose another"
                        raise ValueError("Username taken")
                args = [namevar.get(), passwordvar.get(), "user"]
                cur.callproc("add_user", args)                
                self.cnx.commit()
                cur.execute("select last_insert_id()")
                user_id = cur.fetchall()[0][0]
                self.user = User(user_id, args[0], args[2])
                cur.callproc("add_log", 
                    [datetime.today(), f"registrate user id='{self.user.id}' name='{self.user.name}'"])
                self.cnx.commit()                
            except Exception as e:
                print(e)
            finally:                
                cur.close()            
            self.on_status_change()
            top.destroy()
            
            
        ttk.Button(mainframe, command=foo, text="Register").grid(column=0, columnspan=2, row=2, sticky=(W, E, N, S))
        
        mainframe.rowconfigure(2, weight=1)
        mainframe.columnconfigure(1, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=2)

        top.bind("<Return>", foo)
        
        def name_bind(*args):
            info["text"] = "Enter name"
        name_entry.bind("<FocusIn>", name_bind)
        def password_bind(*args):
            info["text"] = "Enter password"
        password_entry.bind("<FocusIn>", password_bind)
        name_entry.focus()


    def get_params(self, table_name: str):
        if table_name == "book_author":
            return ["book_id", "author_id"]
        if table_name == "book_series":
            return ["book_id", "series_id"]
        if table_name == "rating_user":
            return ["rating_id", "user_id"]
        if table_name == "review_user":
            return ["review_id", "user_id"]
        if table_name == "logs":
            return ["date", "log"]
        if table_name == "rating":
            return ["rating", "book_id"]
        if table_name == "review":
            return ["content", "book_id"]
        params = ["name"]
        if table_name == "author":
            params.append("surname")
        elif table_name == "book":
            params.append("genre_id")
        elif table_name == "user":
            params.append("password")
            params.append("role")
        return params

    def admin_insert(self, table_name, params: List[str]):
        top = Toplevel()
        top.title(f"Insert {table_name}")

        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        entry_var = []
        entry = []
        index = 0
        for param in params:
            ttk.Label(mainframe, text=param).grid(column=0, row=index)
            _entry_var = StringVar()
            entry_var.append(_entry_var)
            entry.append(ttk.Entry(mainframe, textvariable=entry_var[index]))
            entry[index].grid(column=1, row=index)
            index += 1        
        info = ttk.Label(mainframe)
        info.grid(column=0, columnspan=2, row=index, sticky=(N, W, E, S))
        index += 1

        def foo(*_):
            for i, elem in enumerate(entry_var):
                if len(elem.get()) == 0:
                    info["text"] = f"Enter {params[i]}"
                    return
                if params[i] == "password" and len(elem.get()) < 4:
                    info["text"] = f"Password too short"
                    return
            try:
                args = [elem.get() for elem in entry_var]
                cur = self.cnx.cursor()
                cur.callproc(f"add_{table_name}", args)
                log = f"admin id:{self.user.id} insert: "
                for i, val in enumerate(entry_var):
                    log = f"{log}{params[i]}='{val.get()}'; "
                cur.callproc("add_log", [datetime.today(), log])
                self.cnx.commit()
                info["text"] = "Insert successful"
            except Exception as e:
                info["text"] = f"Err: {e}"
            finally:
                cur.close()
            
            
        ttk.Button(mainframe, command=foo, text="Insert").grid(column=0, columnspan=2, row=index, sticky=(W, E, N, S))
        
        mainframe.rowconfigure(index, weight=1)
        mainframe.columnconfigure(1, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=2)

        top.bind("<Return>", foo)
        entry[0].focus()

        top.mainloop()

    def admin_update(self, table_name, params: List, data: List):
        top = Toplevel()
        top.title(f"Update {table_name}")

        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        entry_var = []
        entry = []
        index = 0
        params.insert(0, "id")
        for param in params:
            ttk.Label(mainframe, text=param).grid(column=0, row=index)
            _entry_var = StringVar(value=data[index])
            entry_var.append(_entry_var)
            entry.append(ttk.Entry(mainframe, textvariable=entry_var[index]))
            entry[index].grid(column=1, row=index)
            index += 1
        entry[0].state(["readonly"])    
        info = ttk.Label(mainframe)
        info.grid(column=0, columnspan=2, row=index, sticky=(N, W, E, S))
        index += 1

        def foo(*_):
            for i, elem in enumerate(entry_var):
                if len(elem.get()) == 0:
                    info["text"] = f"Enter {params[i]}"
                    return
                if params[i] == "password" and len(elem.get()) < 4:
                    info["text"] = f"Password too short"
                    return
            try:
                args = [elem.get() for elem in entry_var]
                cur = self.cnx.cursor()
                cur.callproc(f"update_{table_name}", args)
                log = f"admin id:{self.user.id} update: "
                for i, val in enumerate(entry_var):
                    log = f"{log}{params[i]}='{val.get()}'; "
                cur.callproc("add_log", [datetime.today(), log])
                self.cnx.commit()
            except Exception as e:
                info["text"] = f"Err: {e}"
            finally:
                cur.close()

            info["text"] = "update successful"
            
            
        ttk.Button(mainframe, command=foo, text="Update").grid(column=0, columnspan=2, row=index, sticky=(W, E, N, S))
        
        mainframe.rowconfigure(index, weight=1)
        mainframe.columnconfigure(1, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=2)

        top.bind("<Return>", foo)
        entry[0].focus()

        top.mainloop()

    def data_to_str(self, data, table_name):
        params = self.get_params(table_name)
        params.insert(0, "id")

        if len(data) != len(params):
            return "error"

        res = ""
        for i, param in enumerate(params):
            res = f"{res}{param}:'{data[i]}' "
        return res


    def admin(self):
        top = Toplevel()
        top.title(f"Admin")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        top.minsize(600, 360)

        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        datalist = []
        strlist = []
        datavar = StringVar()
        data = Listbox(mainframe, listvariable=datavar, height=10, activestyle="none")
        data.grid(column=0, row=0, sticky=(N, W, E, S))

        toolframe = ttk.Frame(mainframe)
        toolframe.grid(column=1, row=0, sticky=(N, W, E, S))

        tablebox = ttk.Combobox(toolframe, state="readonly")
        tablebox.grid(column=0, columnspan=2, row=0, sticky=(N, W, E, S))
        tablebox["values"] = ("book", "author", "genre", "rating", "review", "series", "user", "logs")
        def on_combobox_select():  
            table_name = tablebox.get()
            try:
                cur = self.cnx.cursor()
                cur.callproc(f"get_{table_name}", [])
                datalist.clear()
                strlist.clear()
                for elem in cur.stored_results():
                    res = elem.fetchall()
                    [datalist.append(elem) for elem in res]       
                    for elem in datalist:
                        strlist.append(self.data_to_str(elem, table_name))       
                datavar.set(strlist)       
            except Exception as e:
                print(e)
            finally:
                cur.close()
            data.focus() 

        debug = ttk.Label(toolframe)
        debug.grid(column=0, columnspan=2, row=3)     

        def on_insert_button(*args):
            table_name = tablebox.get()
            self.admin_insert(table_name, self.get_params(tablebox.get()))
        insert = ttk.Button(toolframe, text="Insert", command=on_insert_button)
        insert.grid(column=0, row=1, sticky=(W, E))

        def on_update_button(*args):
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            table_name = tablebox.get()            
            self.admin_update(table_name, self.get_params(tablebox.get()), datalist[index])
        update = ttk.Button(toolframe, text="Update", command=on_update_button)
        update.grid(column=1, row=1, sticky=(W, E))

        def on_delete_button(*_):
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            table_name = tablebox.get()
            try:                
                cur = self.cnx.cursor()
                id = datalist[index][0]
                # if id == self.user.id:
                #     return
                cur.callproc(f"delete_{table_name}", [id]) 
                self.cnx.commit()
                log = f"admin id:{self.user.id} delete: {table_name} id: {id}"
                cur.callproc("add_log", [datetime.today(), log])
                self.cnx.commit()
                datalist.pop(index)
                strlist.pop(index)
                datavar.set(strlist)       
            except Exception as e:
                print(e)
            finally:
                cur.close()
            data.focus() 
        delete = ttk.Button(toolframe, text="Delete", command=on_delete_button)
        delete.grid(column=0, row=2, sticky=(W, E))
        
        refresh = ttk.Button(toolframe, text="Refresh", command=lambda *_: on_combobox_select())
        refresh.grid(column=1, row=2, sticky=(W, E))  

        def on_add_author(*_):
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            id = datalist[index][0]
            table_name = tablebox.get()
            if table_name != "book":
                return
            self.bind_rel_tables(table_name, id, "author")
        add_author = ttk.Button(toolframe, text="Add book to author", command=on_add_author)  
        add_author.grid(column=0, columnspan=2, row=3, sticky=(W, E))   

        def on_add_series(*_):
            selection = data.curselection()
            if len(selection) == 0:
                return
            index = selection[0]
            id = datalist[index][0]
            table_name = tablebox.get()
            if table_name != "book":
                return
            self.bind_rel_tables(table_name, id, "series")
        add_series = ttk.Button(toolframe, text="Add book to series", command=on_add_series)  
        add_series.grid(column=0, columnspan=2, row=4, sticky=(W, E))

        info = Text(toolframe, width=50, height=15, state="disabled")
        info.grid(column=0, columnspan=2, row=5, sticky=(W, E))

        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=2)

        def on_list_select(*_):
            selection = data.curselection()
            if len(selection) == 0:
                info.delete("1.0", END)
                return
            index = selection[0]
            table_name = tablebox.get()
            info.configure(state="normal")
            info.delete("1.0", END)
            try:
                cur = self.cnx.cursor()
                id = datalist[index][0]
                if table_name == "book":
                    cur.callproc("getauthors_bookid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Authors:\n")
                            for author in res:
                                info.insert(END, f"  {author[1]} {author[2]}\n")
                    cur.callproc("getseries_bookid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Series:\n")
                            for series in res:
                                info.insert(END, f"  {series[1]}\n")

                elif table_name == "author":
                    cur.callproc("getbooks_authorid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Books:\n")
                            for book in res:
                                info.insert(END, f"  name={book[1]}; genre_id={book[2]}\n")
                elif table_name == "series":
                    cur.callproc("getbooks_seriesid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Books:\n")
                            for book in res:
                                info.insert(END, f"  name={book[1]}; genre_id={book[2]}\n")
                elif table_name == "user":
                    cur.callproc("getrating_userid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Ratings:\n")
                            for rating in res:
                                info.insert(END, f"  rating={rating[1]}; book_id={rating[2]}\n")
                    cur.callproc("getreview_userid", [id])
                    for elem in cur.stored_results():
                        res = elem.fetchall()
                        if len(res) > 0:
                            info.insert(END, "Reviews:\n")
                            for review in res:
                                info.insert(END, f"  review_id={review[0]}; book_id={review[2]}\n")
            except Exception as e:
                print(e)
            finally:
                cur.close() 
                info.configure(state="disabled")
        data.bind("<<ListboxSelect>>", on_list_select)
        tablebox.bind("<<ComboboxSelected>>", lambda _: on_combobox_select())
        tablebox.current(0)
        on_combobox_select()
        top.mainloop()

    def bind_rel_tables(self, table_name1: str, id1, table_name2: str):
        top = Toplevel()
        top.title(f"Bind {table_name1}:{table_name2}")

        mainframe = ttk.Frame(top)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        datalist = []
        try:
            cur = self.cnx.cursor()
            cur.callproc(f"get_{table_name2}")            
            for elem in cur.stored_results():
                res = elem.fetchall()
                [datalist.append(item) for item in res]
        except Exception as e:
            print(e)
        finally:
            cur.close()
        if len(datalist) == 0:
            return

        tablebox = ttk.Combobox(mainframe, state="readonly")
        tablebox.grid(column=0, row=0, sticky=(N, W, E, S))
        values = []
        for elem in datalist:
            res = ""
            for i, val in enumerate(elem):
                if i == 0:
                    continue
                res = f"{res}{val} "
            values.append(res)
        tablebox["values"] = values
        tablebox.current(0)

        def on_confirm(*_):
            index = tablebox.current()
            try:
                cur = self.cnx.cursor()
                args = [id1, datalist[index][0]]
                cur.callproc(f"add_{table_name1}_{table_name2}", args)
                self.cnx.commit()
            except Exception as e:
                print(e)
            finally:
                cur.close()
            info["text"] = "Bind successful"
        btn = ttk.Button(mainframe, text="Add", command=on_confirm)
        btn.grid(column=0, row=1)

        info = ttk.Label(mainframe)
        info.grid(column=0, row=2)


        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=2)
        top.bind("<Return>", on_confirm)
        tablebox.bind("<<ComboboxSelected>>", lambda *_: btn.focus())

        top.mainloop()

class User:
    def __init__(self, id, name, role) -> None:
        self.id = id
        self.name = name
        self.role = role


def main():
    cnx = mysql.connector.connect(user="omwi", password="573458", database="library")
    root = Tk()
    MainWindow(root, cnx)
    root.mainloop()

if __name__ == "__main__":
    main()