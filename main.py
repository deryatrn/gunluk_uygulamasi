import tkinter as tk
from tkinter import messagebox, Toplevel, simpledialog, scrolledtext
import mysql.connector
from tkinter import *
from mysql.connector import Error
import datetime

def pencereyi_ortala(pen):
    pen.update_idletasks()
    genislik = pen.winfo_width()
    yukseklik = pen.winfo_height()
    ekran_genislik = pen.winfo_screenwidth()
    ekran_yukseklik = pen.winfo_screenheight()
    x = (ekran_genislik - genislik) // 2
    y = (ekran_yukseklik - yukseklik) // 2
    pen.geometry('{}x{}+{}+{}'.format(genislik, yukseklik, x, y))
db_connection = None
current_user_id = None
def create_connection():
    global db_connection
    try:
        db_connection = mysql.connector.connect(
            host="localhost",
            port=8889,
            user="root",
            password="root",
            database="Gunluk"
        )
        print("Veritabanı bağlantısı başarılı")
    except Error as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")
def register_user():
    global db_connection
    username = entry_new_username.get()
    password = entry_new_password.get()
    if not username or not password:
        messagebox.showerror("Hata", "Kullanıcı adı ve şifre boş bırakılamaz")
        return
    if db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db_connection.commit()
            messagebox.showinfo("Başarılı", "Kullanıcı kaydedildi: " + username)
        except Error as e:
            messagebox.showerror("Hata", f"Kullanıcı kaydedilemedi: {e}")
        finally:
            cursor.close()
    else:
        messagebox.showerror("Hata", "Veritabanı bağlantısı yok")
def login_user():
    global db_connection, current_user_id
    username = entry_username.get()
    password = entry_password.get()
    if not username or not password:
        messagebox.showerror("Hata", "Kullanıcı adı ve şifre boş bırakılamaz")
        return
    if db_connection:
        cursor = db_connection.cursor()
        try:
            query = "SELECT id FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                current_user_id = result[0]
                messagebox.showinfo("Başarılı", "Giriş yapıldı: " + username)
                open_main_window()
            else:
                messagebox.showerror("Hata", "Yanlış kullanıcı adı veya şifre")
        except Error as e:
            messagebox.showerror("Hata", f"Giriş yapılırken hata oluştu: {e}")
        finally:
            cursor.close()
create_connection()
pen = Tk()
pen.title("Günlük Uygulaması")
pen.configure(bg="pink")
pen.geometry("600x300")
pencereyi_ortala(pen)
label_description =Label(pen, text="Günlüklerinizi kilitleyebildiğiniz,kayıt olup giriş yapabildiğiniz bir arayüz uygulaması", fg="black",bg="pink")
label_description.pack(pady=10)
label_username = Label(pen, text="Kullanıcı Adı:", bg="pink")
label_username.pack()

entry_username = Entry(pen,bg="lightpink",fg="black")
entry_username.pack(pady=5)

label_password = Label(pen, text="Şifre:",bg="pink")
label_password.pack()

entry_password = Entry(pen, show="*",bg="lightpink",fg="black")
entry_password.pack(pady=5)

button_login = Button(pen, text="Giriş Yap", command=login_user, bg="blue", fg="black", highlightbackground="pink")
button_login.pack(pady=10)
def open_edit_window(entry_id, entry_text):
    global edit_window
    edit_window = Toplevel(pen)
    edit_window.title("Notu Düzenle")
    edit_window.geometry("400x300")
    pencereyi_ortala(edit_window)
    edit_window.configure(bg="pink")
    text_edit_entry = scrolledtext.ScrolledText(edit_window, height=10)
    text_edit_entry.pack()
    text_edit_entry.insert(END, entry_text)
    button_update = Button(edit_window, text="Güncelle", command=lambda: update_entry(entry_id, text_edit_entry.get('1.0', END)),highlightbackground="pink")
    button_update.pack()
    button_delete = Button(edit_window, text="Sil", command=lambda: delete_entry(entry_id),fg="black",highlightbackground="pink")
    button_delete.pack()
def update_entry(entry_id, new_text):
    cursor = None
    try:
        cursor = db_connection.cursor()
        query = "UPDATE diary_entries SET entry_text = %s WHERE id = %s"
        cursor.execute(query, (new_text, entry_id))
        db_connection.commit()
        messagebox.showinfo("Başarılı", "Not güncellendi")
        refresh_entries(listbox_entries)
    except Error as e:
        messagebox.showerror("Hata", f"Not güncellenirken hata oluştu: {e}")
    finally:
        if cursor is not None:
            cursor.close()
def on_entry_double_click(event):
    try:
        index = listbox_entries.curselection()[0]
        entry = listbox_entries.get(index)
        entry_id = entry.split("[NotID: ")[1].split("]")[0]
        entry_details = get_entry_details(current_user_id, entry_id)

        if entry_details[2]:
            password = simpledialog.askstring("Şifre", "Notun şifresini girin:", show='*')
            if password != entry_details[3]:
                messagebox.showerror("Hata", "Yanlış şifre.")
                return
            open_edit_window(entry_id, entry_details[1])
        else:
            open_edit_window(entry_id, entry_details[1])

    except IndexError:
        pass
def get_entry_details(user_id, entry_id):
    try:
        cursor = db_connection.cursor(buffered=True)
        query = "SELECT id, entry_text, is_locked, lock_password FROM diary_entries WHERE user_id = %s AND id = %s"
        cursor.execute(query, (user_id, entry_id))
        return cursor.fetchone()
    except Error as e:
        messagebox.showerror("Hata", f"Not detayları getirilirken hata oluştu: {e}")
        return None, None, None, None
    finally:
        cursor.close()
def lock_note():
    selected_index = listbox_entries.curselection()
    if not selected_index:
        messagebox.showinfo("Bilgi", "Lütfen kilitlemek istediğiniz notu seçin.")
        return
    entry_id = listbox_entries.get(selected_index[0]).split("[NotID: ")[1].split("]")[0]
    new_password = simpledialog.askstring("Şifre", "Not için bir şifre girin:", show='*')
    if new_password:
        try:
            cursor = db_connection.cursor()
            query = "UPDATE diary_entries SET is_locked = %s, lock_password = %s WHERE id = %s"
            cursor.execute(query, (True, new_password, entry_id))
            db_connection.commit()
            messagebox.showinfo("Başarılı", "Not kilitlendi.")
        except Error as e:
            messagebox.showerror("Hata", f"Not kilitleme sırasında hata oluştu: {e}")
        finally:
            cursor.close()
    refresh_entries(listbox_entries)
def unlock_note():
    selected_index = listbox_entries.curselection()
    if not selected_index:
        messagebox.showinfo("Bilgi", "Lütfen kilidini açmak istediğiniz notu seçin.")
        return
    entry_id = listbox_entries.get(selected_index[0]).split("[NotID: ")[1].split("]")[0]
    password = simpledialog.askstring("Şifre", "Notun şifresini girin:", show='*')
    if password:
        try:
            cursor = db_connection.cursor()
            query = "SELECT lock_password FROM diary_entries WHERE id = %s"
            cursor.execute(query, (entry_id,))
            result = cursor.fetchone()
            if result and result[0] == password:
                query = "UPDATE diary_entries SET is_locked = %s WHERE id = %s"
                cursor.execute(query, (False, entry_id))
                db_connection.commit()
                messagebox.showinfo("Başarılı", "Notun kilidi açıldı.")
            else:
                messagebox.showerror("Hata", "Yanlış şifre.")
        except Error as e:
            messagebox.showerror("Hata", f"Not kilidini açma sırasında hata oluştu: {e}")
        finally:
            cursor.close()
    refresh_entries(listbox_entries)
def open_main_window():
    global current_user_id, listbox_entries, text_entry
    pen.withdraw()
    main_window = Toplevel()
    main_window.title("Günlüğüm")
    main_window.configure(bg="pink")
    main_window.geometry("800x400")
    pencereyi_ortala(main_window)
    menubar = Menu(main_window,bg="white", fg="black")
    main_window.config(menu=menubar)
    settings_menu = Menu(menubar, tearoff=0,bg="white", fg="black")
    menubar.add_cascade(label="Ayarlar", menu=settings_menu)
    settings_menu.add_command(label="Notu Kilitle", command=lock_note)
    settings_menu.add_command(label="Notu Aç", command=unlock_note)
    settings_menu.add_separator()
    settings_menu.add_command(label="Çıkış", command=main_window.destroy)
    text_entry = scrolledtext.ScrolledText(main_window, height=12)
    text_entry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    button_submit = Button(main_window, text="Notu Kaydet", command=lambda: submit_entry(text_entry), bg="pink",highlightbackground="pink")
    button_submit.grid(row=1, column=0, pady=10)
    listbox_entries = Listbox(main_window, font="white", bg="white", fg="black")
    listbox_entries.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    listbox_entries.bind("<Double-1>", on_entry_double_click)
    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_columnconfigure(1, weight=1)
    main_window.grid_rowconfigure(0, weight=1)
    refresh_entries(listbox_entries)
    def filter_entries_by_date():
        date_str = simpledialog.askstring("Tarih Filtresi", "Notları filtrelemek için bir tarih girin (YYYY-MM-DD):", parent=main_window)
        if not date_str:
            return
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz tarih formatı. Lütfen YYYY-MM-DD formatında girin.", parent=main_window)
            return
        filtered_entries = get_entries_by_date(current_user_id, date_str)
        listbox_entries.delete(0, END)
        for entry in filtered_entries:
            entry_date, entry_text, entry_id, is_locked = entry
            display_text = f"{entry_date}: {'[Kilitli Not]' if is_locked else entry_text[:50]}... [NotID: {entry_id}]"
            listbox_entries.insert(END, display_text)
    def get_entries_by_date(user_id, date_str):
        try:
            cursor = db_connection.cursor()
            query = "SELECT entry_date, entry_text, id, is_locked FROM diary_entries WHERE user_id = %s AND DATE(entry_date) = %s ORDER BY entry_date DESC"
            cursor.execute(query, (user_id, date_str))
            return cursor.fetchall()
        except Error as e:
            messagebox.showerror("Hata", f"Veritabanı sorgusu sırasında hata oluştu: {e}", parent=main_window)
            return []
        finally:
            if cursor is not None:
                cursor.close()
    button_filter_by_date = Button(main_window, text="Tarihe Göre Filtrele", command=get_entries_by_date, highlightbackground="pink", bg="#bf91b7", fg="black")
    button_filter_by_date.grid(row=1, column=1, pady=10)
    def on_closing():
        pen.destroy()
    main_window.protocol("WM_DELETE_WINDOW", on_closing)
    refresh_entries(listbox_entries)
def submit_entry(text_widget):
    entry_text = text_widget.get('1.0', END)
    add_entry(current_user_id, entry_text)
    text_widget.delete('1.0', END)
    refresh_entries(listbox_entries)
def refresh_entries(listbox_widget):
    entries = get_entries(current_user_id)
    listbox_widget.delete(0, END)
    for entry in entries:
        entry_date, entry_text, entry_id, is_locked = entry
        display_text = f"{entry_date}: {'[Kilitli Not]' if is_locked else entry_text[:50]}... [NotID: {entry_id}]"
        listbox_widget.insert(END, display_text)
def add_entry(user_id, entry_text):
    cursor = None
    try:
        cursor = db_connection.cursor()
        query = "INSERT INTO diary_entries (user_id, entry_date, entry_text, is_locked) VALUES (%s, NOW(), %s, False)"
        cursor.execute(query, (user_id, entry_text))
        db_connection.commit()
    except Error as e:
        messagebox.showerror("Hata", f"Girdi eklenirken hata oluştu: {e}")
    finally:
        if cursor is not None:
            cursor.close()
def get_entries(user_id):
    try:
        cursor = db_connection.cursor()
        query = "SELECT entry_date, entry_text, id, is_locked FROM diary_entries WHERE user_id = %s ORDER BY entry_date DESC"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Error as e:
        messagebox.showerror("Hata", f"Girdiler getirilirken hata oluştu: {e}")
        return []
    finally:
        cursor.close()
def lock_note():
    selected_index = listbox_entries.curselection()
    if not selected_index:
        messagebox.showinfo("Bilgi", "Lütfen kilitlemek istediğiniz notu seçin.")
        return
    entry = listbox_entries.get(selected_index[0])
    entry_id = entry.split("[NotID: ")[1].split("]")[0]
    new_password = simpledialog.askstring("Şifre", "Not için bir şifre girin:", show='*')
    if new_password is not None:
        try:
            cursor = db_connection.cursor()
            query = "UPDATE diary_entries SET is_locked = True, lock_password = %s WHERE id = %s"
            cursor.execute(query, (new_password, entry_id))
            db_connection.commit()
            messagebox.showinfo("Başarılı", "Not kilitlendi.")
        except Error as e:
            messagebox.showerror("Hata", f"Not kilitleme sırasında hata oluştu: {e}")
        finally:
            cursor.close()
    refresh_entries(listbox_entries)
def unlock_note():
    selected_index = listbox_entries.curselection()
    if not selected_index:
        messagebox.showinfo("Bilgi", "Lütfen kilidini açmak istediğiniz notu seçin.")
        return
    entry = listbox_entries.get(selected_index[0])
    entry_id = entry.split("[NotID: ")[1].split("]")[0]
    password = simpledialog.askstring("Şifre", "Notun şifresini girin:", show='*')
    if password is not None:
        try:
            cursor = db_connection.cursor()
            query = "SELECT lock_password FROM diary_entries WHERE id = %s"
            cursor.execute(query, (entry_id,))
            result = cursor.fetchone()
            if result and result[0] == password:
                query = "UPDATE diary_entries SET is_locked = False, lock_password = NULL WHERE id = %s"
                cursor.execute(query, (entry_id,))
                db_connection.commit()
                messagebox.showinfo("Başarılı", "Notun kilidi açıldı.")
            else:
                messagebox.showerror("Hata", "Yanlış şifre.")
        except Error as e:
            messagebox.showerror("Hata", f"Not kilidini açma sırasında hata oluştu: {e}")
        finally:
            cursor.close()
    refresh_entries(listbox_entries)
def delete_entry(entry_id):
    global edit_window
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT is_locked, lock_password FROM diary_entries WHERE id = %s", (entry_id,))
        is_locked, lock_password = cursor.fetchone()
        if is_locked:
            password = simpledialog.askstring("Şifre", "Notun şifresini girin:", show='*')
            if password != lock_password:
                messagebox.showerror("Hata", "Yanlış şifre. Not silinemedi.")
                return
        query = "DELETE FROM diary_entries WHERE id = %s"
        cursor.execute(query, (entry_id,))
        db_connection.commit()
        messagebox.showinfo("Başarılı", "Not silindi")
        refresh_entries(listbox_entries)
        if edit_window:
            edit_window.destroy()
            edit_window = None
    except Error as e:
        messagebox.showerror("Hata", f"Not silinirken hata oluştu: {e}")
    finally:
        if cursor is not None:
            cursor.close()
def open_register_window():
    register_window = Toplevel(pen)
    register_window.title("Kayıt Ol")
    register_window.geometry("400x300")
    pencereyi_ortala(register_window)
    register_window.configure(bg="pink")
    global entry_new_username, entry_new_password
    label_new_username = Label(register_window, text="Yeni Kullanıcı Adı:",bg="pink",fg="black")
    label_new_username.pack()
    entry_new_username = Entry(register_window,bg="lightgray",fg="black")
    entry_new_username.pack()
    label_new_password = Label(register_window, text="Yeni Şifre:",bg="pink",fg="black")
    label_new_password.pack()
    entry_new_password = Entry(register_window, show="*",fg="black",bg="lightgray")
    entry_new_password.pack()
    button_register = Button(register_window, text="Kayıt Ol", command=register_user,bg="pink",highlightbackground="pink", fg="black")
    button_register.pack()
button_open_register = Button(pen, text="Kayıt Ekranını Aç", command=open_register_window,fg="black",highlightbackground="pink")
button_open_register.pack()

pen.mainloop()
def close_connection():
    global db_connection
    if db_connection:
        db_connection.close()
        print("Veritabanı bağlantısı kapatıldı")
close_connection()
