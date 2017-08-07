import json
import random
import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class FilterModel(QSortFilterProxyModel):
    def __init__(self, term):
        super().__init__()
        self.term = term.lower()

    def filterAcceptsRow(self, row, parent):
        text = self.sourceModel().createIndex(row, 0, parent).data(Qt.EditRole)
        return text.startswith(self.term)

class ListModel(QAbstractTableModel):
    def __init__(self, data, name):
        super().__init__()
        self.data = data
        self.name = name

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self.data[index.row()]).title()
        elif role == Qt.EditRole:
            return str(self.data[index.row()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

class ListView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setStyleSheet('QTableView { font-weight: bold; font-size: 18pt; }')

class Mainframe(QWidget):  
    
    compoundNounFilePath = None
    compoundNounData = {}

    def __init__(self):
        super().__init__()  
        self.dataFilePath = ''
        self.initLayout()        
        self.setWindowTitle('Word Elements')
        self.resize(800, 624)
        self.center()
        self.show()
        self.counter = 1
        self.cached = []        

        args = QApplication.arguments()
        self.compoundNounFilePath = os.path.join(os.path.dirname(args[0]), "data.json") 
        self.loadJSONFile(self.compoundNounFilePath)
        self.updateTermsModel()

    def createFileInputLayout(self):
        label = QLabel('Word Database:')
        self.fileInput = QLineEdit(self.dataFilePath)
        select = QPushButton('Select')
        select.clicked.connect(self.selectDataFile)
        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.fileInput)
        hbox.addWidget(select)
        return hbox

    def createTermLayout(self):       
        self.terms = ListView()
        self.links = ListView()
        self.termInput = QLineEdit()
        self.termInput.textChanged.connect(self.termInputTextChanged)
        self.termInput.returnPressed.connect(self.termInputReturnPressed)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.terms)
        hbox.addWidget(self.links)
        vbox.addLayout(hbox)
        vbox.addWidget(self.termInput)
        return vbox

    def createTestLayout(self):
        generate = QPushButton('Generate')
        generate.clicked.connect(self.generateTestClicked)
        self.testOutput = QLineEdit()
        hbox = QHBoxLayout()
        hbox.addWidget(generate)
        hbox.addWidget(self.testOutput)
        return hbox

    def initLayout(self):
        vbox = QVBoxLayout()       
        vbox.addLayout(self.createFileInputLayout())
        vbox.addLayout(self.createTermLayout())
        vbox.addLayout(self.createTestLayout())
        self.setLayout(vbox) 
       
    def center(self):
        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())

    def selectDataFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select a WordElements data file', '', 'JSON Files (*.json);;All Files (*)')
        if filePath:
            self.loadJSONFile(filePath)

    def loadJSONFile(self, filepath): 
        with open(filepath, 'r') as file:
            self.compoundNounData = json.load(file)
            self.dataFilePath = filepath
            self.fileInput.setText(self.dataFilePath)
            self.updateTermsModel()


    def termSelectionChanged(self, selected, deselected):
        indexes = selected.indexes()
        if len(indexes) <= 0:
            self.updateLinksModel(None)
        else:
            self.updateLinksModel(indexes[0].data(Qt.EditRole))

    def termInputTextChanged(self, text):        
        try:
            terms = text.split(' ')
            self.updateTermsModel(terms[0])
            self.updateLinksModel(terms[0], terms[1])
        except:
            pass

    def termInputReturnPressed(self):        
        try:
            terms = self.termInput.text().split(' ')
            if terms[1] not in self.compoundNounData[terms[0]]:
                self.compoundNounData[terms[0]].append(terms[1])
            self.termInput.setText('')
        except:
            pass

    def updateTermsModel(self, filterText=None):
        keys = list(self.compoundNounData.keys())
        keys.sort()
        model = ListModel(keys, 'Terms')
        if filterText:
            filter = FilterModel(filterText)
            filter.setSourceModel(model)
            model = filter
        self.terms.setModel(model)
        self.terms.selectionModel().selectionChanged.connect(self.termSelectionChanged)

    def updateLinksModel(self, term=None, filterText=None):
        model = None
        if term in self.compoundNounData:
            links = self.compoundNounData[term]
            links.sort()
            model = ListModel(links, 'Links')
            if filterText:
                filter = FilterModel(filterText)
                filter.setSourceModel(model)
                model = filter
        self.links.setModel(model)  
        
    def generateTestClicked(self):
        terms = list(self.compoundNounData.keys())
        try:
            i = random.randint(0, len(terms))
            first = terms[i]
            links = self.compoundNounData[first]
            useful = []
            for link in links:
                if link in terms:
                    useful.append(link)
            i = random.randint(0, len(useful))
            second = useful[i]
            links = self.compoundNounData[second]
            useful = []
            for link in links:
                if link in terms:
                    useful.append(link)
            i = random.randint(0, len(useful))
            third = useful[i]
            links = self.compoundNounData[third]
            i = random.randint(0, len(links))
            fourth = links[i]
            sequence = '{} > {} > {} > {}'.format(first, second, third, fourth)
            if sequence in self.cached:
                raise Exception
            self.cached.append(sequence)
            self.testOutput.setText('{}: {}'.format(self.counter, sequence))
            self.counter = 1
        except:
            self.testOutput.setText('{}'.format(self.counter))
            self.counter += 1
            QTimer.singleShot(1, self.generateTestClicked)
       
if __name__ == '__main__':   
    QCoreApplication.setOrganizationName("Word Elements")
    QCoreApplication.setApplicationName("Word Elements")
    app = QApplication(sys.argv)
    frame = Mainframe()
    sys.exit(app.exec_())