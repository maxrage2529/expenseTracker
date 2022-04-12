from PyQt5 import QtWidgets, QtGui,QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog ,QFileDialog,QDesktopWidget,QMessageBox
from PyQt5.uic import loadUi
import pandas as pd
import numpy as np
import sys,os,shutil
import pathlib
import sqlite3
import pyautogui
from matplotlib import pyplot as p
from datetime import date
import time
from PyQt5.QtCore import QTimer, QDateTime
dirname = os.path.dirname(__file__)
today = date.today()
d1 = today.strftime("%d/%m/%Y")
year=int(today.year)-1
month=11
day=int(today.day)

counter=0
filename_ = os.path.join(dirname, 'db/tabledb.db')
conn = sqlite3.connect(filename_)
c = conn.cursor()
c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='temp' ''')
if c.fetchone()[0]==1 : 
	print('Table exists.')

else :
    conn.execute('''CREATE TABLE temp
         (id INT PRIMARY KEY     NOT NULL,
         date           date    NOT NULL,
         activity           char(100)     NOT NULL,
         source        CHAR(500),
         comment     char(100),
         debit    int,
         credit    int)''')
        
#commit the changes to db			
conn.commit()
c.close()
#close the connection
conn.close()

class win1(QMainWindow):
    def __init__(self): 
        super(win1, self).__init__()
        filename = os.path.join(dirname, 'ui/splashScreen.ui')
        loadUi(filename, self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)
        
        # self.progressBar.setValue(20)
        self.center()
        
    def increaseTimeF(self):
        global counter
        self.progressBar.setValue(counter)
        if counter>100:
            self.timer.stop()
            self.main=win2()
            self.main.show()
            self.close()
        counter+=1
     
    def center(self):
        width, height= pyautogui.size()
        print(width,height)
        if width<1250 or height<800:
            msg=QMessageBox(QMessageBox.Critical,"Warning", "Your screen resolution is below 1250x800")
            x=msg.exec_()
            sys.exit()
        else:
            qr=self.frameGeometry()
            cp=QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
            self.timer=QTimer(self)
            self.timer.timeout.connect(self.increaseTimeF)
            self.timer.start(20)
            
            self.show()
class win2(QMainWindow):
    def __init__(self):
        super(win2, self).__init__()
        filename = os.path.join(dirname, 'ui/main.ui')
        loadUi(filename, self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)

        self.graphBt.setToolTip("It will be available in version 2.0")
        self.graphBt.setEnabled(False)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.deleteMenuF)
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.graphMenuF)

        self.exitBt.clicked.connect(self.exitF)
        self.expenseTrackerBt.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.expenseTrackerP))
        self.manageFilesBt.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.manageFilesP))
        self.graphBt.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.graphP))
        self.backBt.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.expenseTrackerP))
        
        self.populate()
        self.center()
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 320)
        self.tableWidget.setColumnWidth(3, 200)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.setColumnWidth(5, 100)
        self.treeView.setColumnWidth(0, 400)
        self.refreshBt1.clicked.connect(self.loadDataF)
        self.refreshBt2.clicked.connect(self.totalF)
        self.refreshBt3.clicked.connect(lambda : self.dataForParticularGraph(self.tempNeed, self.tempS))
        self.addFileBt.clicked.connect(self.addFileF)
    
    def center(self):
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def totalF(self):
        
        filename = os.path.join(dirname, 'db/tabledb.db')
        conn = sqlite3.connect(filename)
        cur=conn.cursor()
        f3=self.filter3.currentText()
        if f3=="All Time":
            sqlQuery_debit=f"select sum(debit) from temp"
            sqlQuery_credit=f"select sum(credit) from temp"
        if f3=="This Year":
            sqlQuery_debit=f"select sum(debit) from temp where strftime('%Y',temp.DATE) = '{year}'"
            sqlQuery_credit=f"select sum(credit) from temp where strftime('%Y',temp.DATE) = '{year}'"
        if f3=="This Month":
            sqlQuery_debit=f"select sum(debit) from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}'"
            sqlQuery_credit=f"select sum(credit) from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}'"
        if f3=="Last Month":
            sqlQuery_debit=f"select sum(debit) from temp where strftime('%m',temp.DATE) = '{month-1}' and strftime('%Y',temp.DATE) = '{year}'"
            sqlQuery_credit=f"select sum(credit) from temp where strftime('%m',temp.DATE) = '{month-1}' and strftime('%Y',temp.DATE) = '{year}'"
        for i in cur.execute(sqlQuery_debit):
            self.debitL.setText(str(i[0]))
        for i in cur.execute(sqlQuery_credit):
            self.creditL.setText(str(i[0]))

    def clearTableF(self):
        filename = os.path.join(dirname, 'db/tabledb.db')
        conn = sqlite3.connect(filename)
        conn.execute('delete from temp')
        conn.commit()
        conn.close()

    def initialF(self):
        filename = os.path.join(dirname, 'db/tabledb.db')
        filename2 = os.path.join(dirname, 'data/cleanedMain.csv')
        conn = sqlite3.connect(filename)
        f=open(filename2,'r')
        f.readline()
        l=[]
        for i in f.readlines():
            l.append(list(i.split(",")))
        for i in l:
            conn.execute("INSERT INTO temp VALUES (?, ?, ?, ?, ?, ?,?)",
                            (int(i[0]),i[1].split()[0],i[2],i[3].split('#')[0],i[4],float(i[5]),float(i[6])))
        conn.commit()
        conn.close()

    def loadDataF(self):
        filename = os.path.join(dirname, 'db/tabledb.db')
        f1=self.filter1.currentText()
        f2=self.filter2.currentText()
        conn = sqlite3.connect(filename)
        cur = conn.cursor()

        
        if f1=="All Transactions":
            if f2=="All Time":
                sqlQuery = "SELECT * FROM temp"
            if f2=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}'"
            if f2=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}'"
            if f2=="Last Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month-1}' and strftime('%Y',temp.DATE) = '{year}'"
        if f1=="Debits":
            if f2=="All Time":
                sqlQuery = f"select * from temp where  Debit>0"
            elif f2=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}' and Debit>0"
            elif f2=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}' and Debit>0"
            elif f2=="Last Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month-1}' and strftime('%Y',temp.DATE) = '{year}' and Debit>0"
        if f1=="Credits":
            if f2=="All Time":
                sqlQuery = f"select * from temp where  Credit>0"
            elif f2=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}' and Credit>0"
            elif f2=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}' and Credit>0"
            elif f2=="Last Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month-1}' and strftime('%Y',temp.DATE) = '{year}' and Credit>0"
        if f1=="Cashbacks":
            if f2=="All Time":
                sqlQuery = f"select * from temp where  activity='Cashback received'"
            elif f2=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}' and activity='Cashback received'"
            elif f2=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}' and activity='Cashback received'"
            elif f2=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month-1}' and strftime('%Y',temp.DATE) = '{year}' and activity='Cashback received'"
        
        
        rowCount = len(cur.execute(sqlQuery).fetchall())
        self.tableWidget.setRowCount(rowCount)
        tableRow = 0
        for rows in cur.execute(sqlQuery):
            self.tableWidget.setItem(
                tableRow, 0, QtWidgets.QTableWidgetItem(str(rows[1])))
            self.tableWidget.setItem(
                tableRow, 1, QtWidgets.QTableWidgetItem(str(rows[2])))
            self.tableWidget.setItem(
                tableRow, 2, QtWidgets.QTableWidgetItem(str(rows[3])))
            self.tableWidget.setItem(
                tableRow, 3, QtWidgets.QTableWidgetItem(str(rows[4])))
            self.tableWidget.setItem(
                tableRow, 4, QtWidgets.QTableWidgetItem(str(rows[5])))
            self.tableWidget.setItem(
                tableRow, 5, QtWidgets.QTableWidgetItem(str(rows[6])))
            
                
            tableRow += 1
        cur.close()
        conn.close()


    def exitF(self):
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(r"D:\Projects\Python_Projects\modernUI\resources\images\redCross1.png"))
        # self.exitBt.setIcon(icon)
        self.close()

    def addFileF(self):
        filename = os.path.join(dirname, 'data/rawData')
        try:
            fname=QFileDialog.getOpenFileName(self,'Open file','C:\Windows','CSV (*.csv, *)')
            shutil.copy(fname[0],filename)
            self.populate()
        except:
            pass
    def populate(self):
        filename = os.path.join(dirname, 'data/rawData')
        path=filename
        self.model=QtWidgets.QFileSystemModel()
        self.model.setRootPath((QtCore.QDir.rootPath()))
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(path))
        self.treeView.setSortingEnabled(True)
        
        
        self.createOrgMainF()
        self.createCleanedMainF()
        self.clearTableF()
        self.initialF()
        self.loadDataF()
        self.totalF()

    def deleteMenuF(self):
        menu=QtWidgets.QMenu()
        delete=menu.addAction("Delete")
        delete.triggered.connect(self.deleteFileF)
        cursor=QtGui.QCursor()
        menu.exec_(cursor.pos())

    def graphMenuF(self):
        menu=QtWidgets.QMenu()
        delete=menu.addAction("Show Graph")
        delete.triggered.connect(self.showGraphF)
        cursor=QtGui.QCursor()
        menu.exec_(cursor.pos())

    def deleteFileF(self):
        index=self.treeView.currentIndex()
        path=self.model.filePath(index)
        try:
            os.remove(path)
            self.populate()
        except:
            pass

    def showGraphF(self):
        try:
            row = self.tableWidget.currentRow()
            source = self.tableWidget.item(row,2).text()
            activity = self.tableWidget.item(row,1).text()
            comment = self.tableWidget.item(row,3).text()
            self.stackedWidget.setCurrentWidget(self.showGraphP)
            # print(source,type(source),source=="Paytm Order ")
            if str(source)=="Order ":
                need=activity+" "+comment
                self.graphNameL.setText(need)
                self.dataForParticularGraph(comment,"comment")
            elif source=="Paytm Order ":
                need=activity
                self.graphNameL.setText(need)
                self.dataForParticularGraph(activity,"activity")
            else:
                need=source
                self.graphNameL.setText(need)
                self.dataForParticularGraph(source,"source")
        except:
            pass

    def dataForParticularGraph(self,need,s):
        filename = os.path.join(dirname, 'db/tabledb.db')
        self.tempNeed=need
        self.tempS=s
        f4=self.filter4.currentText()
        conn = sqlite3.connect(filename)
        cur = conn.cursor()
        if s=="source":
            if f4=="All Time":
                sqlQuery = f"select * from temp where source='{need}' "
            elif f4=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}' and source='{need}'"
            elif f4=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}' and source='{need}'"
        elif s=="activity":
            if f4=="All Time":
                sqlQuery = f"select * from temp where activity='{need}'"
            elif f4=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}' and activity='{need}'"
            elif f4=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}' and activity='{need}'"
        elif s=="comment":
            if f4=="All Time":
                sqlQuery = f"select * from temp where comment='{need}'"
            elif f4=="This Year":
                sqlQuery = f"select * from temp where strftime('%Y',temp.DATE) = '{year}' and source='{need}'"
            elif f4=="This Month":
                sqlQuery = f"select * from temp where strftime('%m',temp.DATE) = '{month}' and strftime('%Y',temp.DATE) = '{year}' and source='{need}'"
        l=[]
        # rowCount = len(cur.execute(sqlQuery).fetchall())
        # print(rowCount)
        for rows in cur.execute(sqlQuery):
           
            l.append(list(rows))
        cur.close()
        conn.close() 
        l=l[::-1]
        self.creditList=[]
        self.debitList=[]
        self.dateList=[]
        for i in l:
            self.creditList.append(i[-1])
            self.debitList.append(i[-2])
            self.dateList.append(i[1])
        if f4=="All Time":
            self.generateGraph(0)
        elif f4=="This Year":
            self.generateGraph(1)
        elif f4=="This Month":
            self.generateGraph(2)

    
    def generateGraph(self,a):
        filename = os.path.join(dirname, 'temp/particularGraph.png')
        filename2 = os.path.join(dirname, 'temp/no.png')
        try:
            os.remove(filename)
        except:
            pass
        if a==0:
            #for all time
            tempDateList=self.dateList.copy()
            for i in range(len(tempDateList)):
                tempDateList[i]=tempDateList[i][:4]
            self.debitL2.setText(str(sum(self.debitList)))
            self.creditL2.setText(str(sum(self.creditList)))
            tempDateList,tempDebitList,tempCreditList=self.prakashF(tempDateList,self.debitList,self.creditList)
            self.prakashGraph(tempDateList, tempDebitList, tempCreditList)
            self.graphImgL.setPixmap(QtGui.QPixmap(filename))
        elif a==1:
            #for this year
            tempDateList=self.dateList.copy()
            for i in range(len(tempDateList)):
                tempDateList[i]=int(tempDateList[i][5:7])-1
            creditList2=[0,0,0,0,0,0,0,0,0,0,0,0]
            debitList2=[0,0,0,0,0,0,0,0,0,0,0,0]
            months=["Jan","Feb","Mar","May","Apr","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            for i in range(len(self.debitList)):
                creditList2[tempDateList[i]]+=self.creditList[i]
                debitList2[tempDateList[i]]+=self.debitList[i]
            self.debitL2.setText(str(sum(debitList2)))
            self.creditL2.setText(str(sum(creditList2)))
            if len(self.dateList)==0:
                self.graphImgL.setPixmap(QtGui.QPixmap(filename2))
            else:
                
                self.prakashGraph(months, debitList2, creditList2)
                self.graphImgL.setPixmap(QtGui.QPixmap(filename))
    
        else:
            #for this month
            tempDateList=self.dateList.copy()
            self.debitL2.setText(str(sum(self.debitList)))
            self.creditL2.setText(str(sum(self.creditList)))
            if len(self.dateList)==0:
                self.graphImgL.setPixmap(QtGui.QPixmap(filename2))
            else:
                tempDateList,tempDebitList,tempCreditList=self.prakashF(tempDateList,self.debitList,self.creditList)
                self.prakashGraph(tempDateList, tempDebitList, tempCreditList)
                self.graphImgL.setPixmap(QtGui.QPixmap(filename))
                

    def createOrgMainF(self):
        filename = os.path.join(dirname, 'data/orgMain.csv')
        filename2 = os.path.join(dirname, 'data/rawData')
        orgMain=open(filename,'w')
        orgMain.write('"Date","Activity","Source/Destination","Wallet Txn ID","Comment","Debit","Credit","Transaction Breakup","Status"')
        orgMain.write("\n")
        for path in pathlib.Path(filename2).iterdir():
            if path.is_file():
                f = open(path, "r")
                f.readline()
                for i in f.readlines():
                    orgMain.write(i)
                f.close()
        orgMain.close()
    def createCleanedMainF(self):
        filename = os.path.join(dirname, 'data/orgMain.csv')
        filename2 = os.path.join(dirname, 'data/cleanedMain.csv')
        df=pd.read_csv(filename)
        df=df.drop_duplicates()
        df=df.iloc[:,[0,1,2,4,5,6,8]]
        df=df.loc[df.Status=="SUCCESS"]
        df=df.loc[df.Activity!="Added to Loyalty Wallet"]
        df=df.drop('Status',axis=1)
        df=df.fillna(0)
        df['Date']= pd.to_datetime(df['Date'])
        df=df.sort_values(by='Date',ascending=False)
        df.to_csv(filename2)

    def prakashF(self,l1,l2,l3) :
        
        d = dict()
        for i in range(len(l1)) :
            if l1[i] in d :
                d[l1[i]].append(i)
            else :
                d[l1[i]] = [i]
        # print(d)
        temp1 = {i:0 for i in list(d.keys())}
        temp2 = {i:0 for i in list(d.keys())}
        for i in d :
            for j in d[i] :
                temp1[i]+=l2[j]
        for i in d :
            for j in d[i] :
                temp2[i]+=l3[j]
        # print(temp1)
        l1 = list(temp1.keys())
        l2 = list(temp1.values())
        l3 = list(temp2.values())
        return l1,l2,l3
    def prakashGraph(self,x,y,z):
        filename = os.path.join(dirname, 'temp/particularGraph.png')
        if len(x)==1:
            p.xlim(-1,1)
        bw1 = .09
        bw2 = .039
        x_range = np.arange(len(y) / 8, step=0.125)
        p.bar(x_range, y, color='#8edea3', width=bw1/2, edgecolor='#c3d5e8', label='Debit')
        p.bar(x_range, z, color='#ffc001', width=bw2/2, edgecolor='#c3d5e8', label='Credit')

        for i, bar in enumerate(y):
            p.text(i / 8 - 0.010, bar + 1, bar, fontsize=10)
        p.xticks(x_range, x)
        p.tick_params(
            axis='y',          
            which='both',      
            bottom=False,      
            top=False,        
            labelbottom=False,labelsize=10)
        p.yticks([])

        p.axhline(y=0, color='gray')
        # p.legend(frameon=False, loc='upper right')
        p.box(False)
        figure = p.gcf()

        figure.set_size_inches(9, 5)
        p.savefig(filename, dpi=100)
        p.clf()
def main():
    app = QApplication(sys.argv)
    win = win1()
    sys.exit(app.exec_())
main()