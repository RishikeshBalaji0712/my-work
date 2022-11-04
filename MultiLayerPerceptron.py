import pandas as pd
from PyQt5.QtCore import pyqtSlot
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.QtWidgets import QFileDialog


def UniqueElements(data, st):
    i = 0
    dev = []
    while (i < len(data[st])):
        if (data.loc[i][st] not in dev):
            dev.append(data.loc[i][st])
        i += 1
    return dev

def vector(data, st):
    le = LabelEncoder()
    le.fit(data[st].unique())
    le.classes_
    i = 0
    arr = []
    while i < len(le.classes_):
        arr.append(le.classes_[i])
        i += 1
    num = le.transform(data[st].unique())
    i = 0
    vec = []

    while i < len(data):
        vec.append(arr.index(data.loc[i][st]))
        i += 1
    return vec

def UniqueNumbers(data, st):
    le = LabelEncoder()
    num = le.transform(UniqueElements(data, st))
    return num

def RelevantData(st):
    data = pd.read_excel(st)
    df = pd.DataFrame()
    i = 0
    prepid = []
    glan = []
    source = []
    ac = []
    at = []
    while i < len(data):
        prepid.append(data.loc[i]['Preparer_ID'])
        glan.append(data.loc[i]['GL_Account_Number'])
        source.append(data.loc[i]['Source'])
        ac.append(data.loc[i]['Account_Class'])
        at.append(data.loc[i]['Account_Type'])
        i += 1

    df['Preparer_ID'] = prepid
    df['GL_Account_Number'] = glan
    df['Source'] = source
    df['Account_Class'] = ac
    df['Account_Type'] = at

    return df

def num(stri):
    data = RelevantData(stri)
    data['Account_Class_Num'] = vector(data, 'Account_Class')
    data['Preparer_ID_Num'] = vector(data, 'Preparer_ID')
    data['Source_Num'] = vector(data, 'Source')
    data['GL_Account_Number_Num'] = vector(data, 'GL_Account_Number')

    assets = []
    liabilities = []
    expenses = []
    revenue = []
    i = 0

    while i < len(data):
        if (data.loc[i]['Account_Type'] == 'Assets'):
            assets.append(1)
            liabilities.append(0)
            expenses.append(0)
            revenue.append(0)
        elif (data.loc[i]['Account_Type'] == 'Liabilities'):
            assets.append(0)
            liabilities.append(1)
            expenses.append(0)
            revenue.append(0)
        elif (data.loc[i]['Account_Type'] == 'Expenses'):
            assets.append(0)
            liabilities.append(0)
            expenses.append(1)
            revenue.append(0)
        elif (data.loc[i]['Account_Type'] == 'Revenue'):
            assets.append(0)
            liabilities.append(0)
            expenses.append(0)
            revenue.append(1)
        i += 1

    data['Account_Type_Assets'] = assets
    data['Account_Type_Expenses'] = expenses
    data['Account_Type_Liabilities'] = liabilities
    data['Account_Type_Revenue'] = revenue
    return data

def NumToStr(predval):
    predtype = []
    i = 0
    while i < len(predval):
        if (predval[i][0] == 1):
            predtype.append('Assets')
        elif (predval[i][1] == 1):
            predtype.append('Expenses')
        elif (predval[i][2] == 1):
            predtype.append('Liabilities')
        elif (predval[i][3] == 1):
            predtype.append('Revenue')
        else:
            predtype.append('NA')
        i += 1
    return predtype

def MLP(st):
    df1 = num('/Users/Rishikesh/Documents/Internship/Robotech Solutions/Data1.xlsx')
    df2 = num(st)
    x = df1.values[:, 5 : 9].tolist()
    y = df1.values[:, 9 : 13].tolist()
    clf = MLPClassifier(solver = 'lbfgs', alpha = 1e-5, hidden_layer_sizes = (5, 4), random_state = 1)
    clf.fit(x, y)
    pred = clf.predict(df2.values[:, 5 : 9])
    act = df2.values[:, 9 : 13]
    predtype = NumToStr(pred)
    df2['Predicted Types'] = predtype
    return df2

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Predictions'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.initUI()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py)", options=options)
        return (fileName)


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createTable()
        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def createTable(self):
        method = input("Enter the model to be used: MLP, KNN, DT: ")
        if (method == 'MLP'):
            arr = MLP(self.openFileNameDialog())
        elif (method == 'KNN'):
            arr = KNN(self.openFileNameDialog())
        elif (method == 'DT'):
            arr = DecisionTree((self.openFileNameDialog()))
        else:
            print ('The default model MLP will be used as the method entered is invalid.')
            arr = MLP(self.openFileNameDialog())
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(arr))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Preparer ID"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("GL Account Number"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("Source"))
        self.tableWidget.setItem(0, 3, QTableWidgetItem("Account Class"))
        self.tableWidget.setItem(0, 4, QTableWidgetItem("Actual Account Type"))
        self.tableWidget.setItem(0, 5, QTableWidgetItem("Predicted Account Type"))

        i = 0
        while i < len(arr):
            j = 0
            while j < 5:
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(arr.loc[i][j])))
                j += 1
                self.tableWidget.setItem(i + 1, j + 1, QTableWidgetItem(str(arr.loc[i]['Predicted Types'])))
            i += 1

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = App()
    mainWin.show()
    sys.exit( app.exec_() )
