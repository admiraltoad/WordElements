import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

CompoundNounData = {
    'fire': ['truck', 'ball', 'work'],
    'work': ['station', 'desk']
}

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

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.name

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self.data[index.row()]).title()
        elif role == Qt.EditRole:
            return str(self.data[index.row()])

class ListView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        vh = self.verticalHeader()
        vh.setSectionResizeMode(QHeaderView.Fixed)
        vh.hide()
        hh = self.horizontalHeader()
        hh.setHighlightSections(False)
        hh.setSectionsMovable(True)
        hh.setSectionResizeMode(QHeaderView.Stretch)

class Mainframe(QWidget):   
    def __init__(self):
        super().__init__()  
        self.dataFilePath = ''
        self.initLayout()
        self.center()
        self.setWindowTitle('Expenses')
        self.resize(800, 200)
        self.show()

    def createFileInputLayout(self):
        label = QLabel('Word Database:')
        self.fileInput = QLineEdit(self.dataFilePath)
        select = QPushButton('Select')
        select.clicked.connect(self.selectDataFile)
        save = QPushButton('Save')
        save.clicked.connect(self.saveDataFile)
        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.fileInput)
        hbox.addWidget(select)
        hbox.addWidget(save)
        return hbox

    def createTermLayout(self):       
        self.terms = ListView()
        self.links = ListView()
        self.termInput = QLineEdit()
        self.termInput.textChanged.connect(self.termInputTextChanged)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.terms)
        hbox.addWidget(self.links)
        vbox.addLayout(hbox)
        vbox.addWidget(self.termInput)
        return vbox

    def initLayout(self):
        vbox = QVBoxLayout()       
        vbox.addLayout(self.createFileInputLayout())
        vbox.addLayout(self.createTermLayout())
        self.setLayout(vbox) 
       
    def center(self):
        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())

    def selectDataFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select a WordElement data file', '', 'JSON Files (*.json);;All Files (*)')
        if filePath:
            try:
                with open(filePath, 'r') as file:
                    CompoundNounData = json.load(file)
                    self.dataFilePath = filePath
                    self.fileInput.setText(self.dataFilePath)
                    self.updateTermsModel()
            except:
                pass           

    def saveDataFile(self):
        with open(self.dataFilePath, 'w') as file:
            json.dump(CompoundNounData, file)

    def termSelectionChanged(self, selected, deselected):
        indexes = selected.indexes()
        if len(indexes) <= 0:
            self.updateLinksModel(None)
        else:
            self.updateLinksModel(indexes[0].data(Qt.EditRole))

    def termInputTextChanged(self, text):
        firstTerm = text.split(' ')[0]
        self.updateTermsModel(firstTerm)

    def updateTermsModel(self, filterText=None):
        keys = list(CompoundNounData.keys())
        keys.sort()
        model = ListModel(keys, 'Terms')
        if filterText:
            filter = FilterModel(filterText)
            filter.setSourceModel(model)
            model = filter
        self.terms.setModel(model)
        self.terms.selectionModel().selectionChanged.connect(self.termSelectionChanged)

    def updateLinksModel(self, term=None):
        model = None
        if term in CompoundNounData:
            links = CompoundNounData[term]
            links.sort()
            model = ListModel(links, 'Links')
        self.links.setModel(model)       
       
if __name__ == '__main__':   
    QCoreApplication.setOrganizationName("Expenses")
    QCoreApplication.setApplicationName("Expenses")
    app = QApplication(sys.argv)
    frame = Mainframe()
    sys.exit(app.exec_())