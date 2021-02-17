from tkinter import *
from tkinter import filedialog as fd
import tkinter.messagebox as messagebox
import tkinter as tk
from bookManager import *
from tkinter import ttk


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.master.geometry('400x650')
        self.createWidgets()
        self.schoolFile = ''
        self.dataSource = ''
        self.vendorFiles = []
        self.schoolTypes = []
        self.copyCountEntry

    def openDataSourceFile(self):
        self.dataSource = fd.askopenfilename()
        print(self.dataSource)

    def openSchoolOrderFile(self):
        self.schoolFile = fd.askopenfilename()
        print(self.schoolFile)

    def openVendorFile(self):
        self.vendorFiles = fd.askopenfilenames()
        print(self.vendorFiles)

    def updateDataSource(self):
        if self.dataSource == '':
            messagebox.showwarning('警告', '请选择数据源')
            return
        if not self.vendorFiles:
            messagebox.showwarning('警告', '请选供应商书单')
            return
        result = mergeMultiVendorsData(self.vendorFiles, self.dataSource)
        if result:
            messagebox.showinfo('成功', '更新供应商数据成功')
        else:
            messagebox.showinfo('成功', '更新供应商数据失败')

    def getSchoolBookList(self):
        if self.dataSource == '':
            messagebox.showwarning('警告', '请选择数据源')
            return

        copyCount = self.copyCountEntry.get()
        if not copyCount.isalnum():
            messagebox.showwarning('警告', '请输入正确的副本数量')
            return

        schoolName = self.schoolName.get()
        if not schoolName:
            messagebox.showwarning('警告', '请输入正确的学校名称')
            return

        if not self.schoolTypes:
            messagebox.showwarning('警告', '请选择学校类型')
            return

        result = generateSchoolSupplyList(
            schoolName, self.schoolTypes, int(copyCount), self.dataSource)
        if result:
            messagebox.showinfo('成功', '生成学校书单成功')
        else:
            messagebox.showinfo('成功', '生成学校书单失败')

    def generateVendorOrders(self):
        schoolName = self.schoolName2.get()
        if not schoolName:
            messagebox.showwarning('警告', '请输入正确的学校名称')
            return
        if self.schoolFile == '':
            messagebox.showwarning('警告', '请选学校订单')
            return
        result = splitSchoolOrder(schoolName, self.schoolFile,
                                  dataSourcePath=self.dataSource)
        if result:
            messagebox.showinfo('成功', '生成供应商订单成功')
        else:
            messagebox.showinfo('成功', '生成供应商订单失败')

    def selectSchoolType(self):
        self.schoolTypes = []
        for i in range(len(schoolType)):
            if self.schoolTypeCheckbuttons[i].get() == '1':
                self.schoolTypes.append(schoolType[i])
        print(self.schoolTypes)

    def createWidgets(self):
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=tk.X, pady=10)
        Button(self, text='选择数据源', pady=10, padx=10, relief='raised',
               command=self.openDataSourceFile).pack(pady=5)
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=tk.X, pady=5)

        Button(self, text='选择供应商书单', pady=10, padx=10, relief='raised',
               command=self.openVendorFile).pack(pady=5)
        Button(self, text='更新数据源', pady=10, padx=10, relief='raised',
               command=self.updateDataSource).pack(pady=5)
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=tk.X, pady=5)

        Label(self, text='学校类型:').pack()
        schoolTypes = [StringVar(), StringVar(), StringVar()]
        self.schoolTypeCheckbuttons = schoolTypes
        for i in range(len(schoolType)):
            Checkbutton(self, text=schoolType[i],
                        variable=schoolTypes[i], command=self.selectSchoolType).pack()

        Label(self, text='学校名称:').pack()
        self.schoolName = Entry(self)
        self.schoolName.pack()
        Label(self, text='副本量:').pack()
        self.copyCountEntry = Entry(self)
        self.copyCountEntry.pack()
        Button(self, text='生成学校供书单', pady=10, padx=10, relief='raised',
               command=self.getSchoolBookList).pack(pady=5)

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=tk.X, pady=5)

        Label(self, text='学校名称:').pack()
        self.schoolName2 = Entry(self)
        self.schoolName2.pack()
        Button(self, text='选择学校返单', pady=10, padx=10, relief='raised',
               command=self.openSchoolOrderFile).pack(pady=5)
        Button(self, text='生成供应商订单', pady=10, padx=10, relief='raised',
               command=self.generateVendorOrders).pack(pady=5)


# root = Tk()
app = Application()
# 设置窗口标题:
app.master.title('图书数据管理')
# 主消息循环:
app.mainloop()
