from tkinter import *
from tkinter import ttk
from csvreader import CSV_worker
import os

# 随手写的幽默app 推荐不要数据量超过1000条，否则可能会爆慢

root = Tk()
root.title("CSV内容显示")
root.geometry("800x600")

# 初始化CSV读取器
csv_path = ".\\data\\data.csv"
if not os.path.exists(csv_path):
    os.mkdir('data')
    with open(csv_path, "w",encoding='UTF-8') as f:
        f.write('标题,路径,主标签')
reader = CSV_worker(csv_path)
columns = reader.fieldnames_
reader.read()

def flush_windows(data):
    # 清空旧内容
    for i in tree.get_children():
        tree.delete(i)

    # 设置表头
    tree["columns"] = columns
    tree["show"] = "headings"
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # 插入数据
    for row in data:
        values = [row[col] for col in columns]
        tree.insert("", END, values=values)

def csv_write():
    # 从Entry获取输入
    new_row = {}
    for col, entry in zip(columns, entries):
        new_row[col] = entry.get()
    # 写入buffer
    reader.write(new_row)
    flush_windows(reader.data_)  # 刷新显示

# 创建Treeview控件
tree = ttk.Treeview(root)
tree.pack(fill=BOTH, expand=True)

# 添加输入框和标签
entry_frame = Frame(root)
entry_frame.pack(pady=5)
entries = []
for col in columns:
    lbl = Label(entry_frame, text=col)
    lbl.pack(side=LEFT, padx=2)
    ent = Entry(entry_frame, width=10)
    ent.pack(side=LEFT, padx=2)
    entries.append(ent)

# 双击事件
def on_double_click(event):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if not item or not column:
        return
    col_index = int(column.replace('#', '')) - 1
    x, y, width, height = tree.bbox(item, column)
    value = tree.item(item, 'values')[col_index]

    edit_box = Entry(tree)
    edit_box.place(x=x, y=y, width=width, height=height)
    edit_box.insert(0, value)
    edit_box.focus()

    def save_edit(event=None):
        new_value = edit_box.get()
        values = list(tree.item(item, 'values'))
        values[col_index] = new_value
        tree.item(item, values=values)
        # 同步到reader.data_
        idx = tree.index(item)
        reader.data_[idx][columns[col_index]] = new_value
        edit_box.destroy()

    edit_box.bind('<Return>', save_edit)
    edit_box.bind('<FocusOut>', lambda e: edit_box.destroy())

tree.bind('<Double-1>', on_double_click)

hyperlink_col = '路径'  # 可以根据实际列名修改

def on_click(event,tree):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if not item or not column:
        return
    col_index = int(column.replace('#', '')) - 1
    if columns[col_index] == hyperlink_col:
        file_path = tree.item(item, 'values')[col_index]
        if os.path.exists(file_path):
            os.startfile(file_path)  # Windows下打开文件
        else:
            from tkinter import messagebox
            messagebox.showerror("错误", f"文件不存在：{file_path}")

# ctrl + 鼠标双击 自动跳转到路径
tree.bind('<Control-Double-1>', lambda e : on_click(e,tree))

def delete_selected():
    selected = tree.selection()
    if not selected:
        return
    for item in selected:
        idx = tree.index(item)
        tree.delete(item)
        reader.delete(idx)
    reader.save()

def flush_default():
    flush_windows(reader.data_)

def find():
    win = Toplevel(root)
    win.title("查找")
    win.geometry("800x600")

    # 选择列
    lbl_col = Label(win, text="选择列：")
    lbl_col.pack(pady=5)
    col_var = StringVar()
    col_var.set(columns[0])
    col_menu = ttk.Combobox(win, textvariable=col_var, values=columns, state="readonly")
    col_menu.pack(pady=5)

    # 输入字符串
    lbl_str = Label(win, text="输入内容：")
    lbl_str.pack(pady=5)
    entry_str = Entry(win)
    entry_str.pack(pady=5)

    # 结果Treeview
    result_tree = ttk.Treeview(win)
    result_tree.pack(fill=BOTH, expand=True, pady=10)
    result_tree["columns"] = columns
    result_tree["show"] = "headings"
    for col in columns:
        result_tree.heading(col, text=col)
        result_tree.column(col, width=80)

    def do_find():
        col = col_var.get()
        s = entry_str.get()
        result = reader.select(col, s)
        # 清空旧内容
        for i in result_tree.get_children():
            result_tree.delete(i)
        # 插入新内容
        for row in result:
            values = [row[c] for c in columns]
            result_tree.insert("", END, values=values)
    
    def on_double_click_readonly(event):
        item = result_tree.identify_row(event.y)
        column = result_tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace('#', '')) - 1
        x, y, width, height = result_tree.bbox(item, column)
        value = result_tree.item(item, 'values')[col_index]

        edit_box = Entry(result_tree)
        edit_box.place(x=x, y=y, width=width, height=height)
        edit_box.insert(0, value)
        edit_box.focus()
        
        edit_box.bind('<Return>', lambda e: edit_box.destroy())
        edit_box.bind('<FocusOut>', lambda e: edit_box.destroy())


    result_tree.bind('<Double-1>', on_double_click_readonly)
    result_tree.bind('<Control-Double-1>',lambda e : on_click(e,tree=result_tree))
    btn_do_find = Button(win, text="查找", command=do_find)
    btn_do_find.pack(pady=5)

btn_write = Button(root, text="读取文件", command=flush_default)
btn_write.pack(pady=5)

btn_write = Button(root, text="加入条目", command=csv_write)
btn_write.pack(pady=5)

btn_delete = Button(root, text="删除选中", command=delete_selected)
btn_delete.pack(pady=5)

btn_find = Button(root, text="查找", command=find)
btn_find.pack(pady=5)

flush_windows(reader.data_)  # 启动时先读取一次

root.mainloop()

reader.save()