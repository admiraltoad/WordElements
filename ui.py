import sys
from terms import TermsManager, AttemptsExpired
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class FilterModel(QSortFilterProxyModel):
    def __init__(self, filterText):
        super().__init__()
        self.filterText = filterText.lower()

    def filterAcceptsRow(self, row, parent):
        return self.sourceModel().createIndex(row, 0, parent).data(Qt.EditRole).startswith(self.filterText)

class ListModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self.data[index.row()]).title()
        elif role == Qt.EditRole:
            return str(self.data[index.row()]).lower()
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

class TableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setStyleSheet('QTableView { font-weight: bold; font-size: 18pt; }')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customContext)

    def customContext(self, point):
        menu = QMenu()
        menu.addAction('Delete').triggered.connect(self.deleteItem)
        menu.exec_(self.mapToGlobal(point))

    def deleteItem(self):
        selection = self.selectionModel().selectedIndexes()
        if selection:
            self.parent().deleteItem(self, selection[0])

class Mainframe(QWidget):
    def __init__(self):
        super().__init__()  
        self.termsManager = TermsManager()
        self.initLayout()        
        self.setWindowTitle('Word Elements')
        self.resize(800, 624)
        self.center()
        self.show()
        self.updateTermsModel()       

    def createFileInputLayout(self):
        label = QLabel('Word Database:')
        filePath = QLineEdit(self.termsManager.filePath)
        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(filePath)
        return hbox

    def createTermLayout(self):       
        self.terms = TableView(self)
        self.links = TableView(self)
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

    def termSelectionChanged(self, selected, deselected):
        indexes = selected.indexes()
        if len(indexes) <= 0:
            self.updateLinksModel(None)
        else:
            self.updateLinksModel(indexes[0].data(Qt.EditRole))

    def termInputTextChanged(self, text):
        terms = text.split(' ')
        if len(terms) >=2 and not terms[-1]:
            self.updateTermsModel(terms[-2])
            self.updateLinksModel(terms[-2], None)
        elif len(terms) >= 2:
            self.updateTermsModel(terms[-2])
            self.updateLinksModel(terms[-2], terms[-1])
        elif len(terms) == 1:
            self.updateTermsModel(terms[0])
            if self.terms.model().rowCount() == 1:
                self.updateLinksModel(self.terms.model().index(0, 0).data(Qt.EditRole), None)
            else:
                self.updateLinksModel(None)
        else:
            self.updateTermsModel(None)
            self.updateLinksModel(None, None)

    def termInputReturnPressed(self):     
        terms = [term for term in self.termInput.text().split(' ') if term]
        if len(terms) < 2:
            return
        for i in range(len(terms) - 1):
            self.termsManager.add(terms[i].lower(), terms[i + 1].lower())
        self.updateTermsModel(None)
        self.updateLinksModel(None, None)
        self.termInput.setText('')

    def updateTermsModel(self, filterText=None):
        terms = self.termsManager.terms()
        terms.sort()
        model = ListModel(terms)
        if filterText:
            filter = FilterModel(filterText)
            filter.setSourceModel(model)
            model = filter
        self.terms.setModel(model)
        self.terms.selectionModel().selectionChanged.connect(self.termSelectionChanged)
        if self.terms.model().rowCount() == 1:
            self.terms.selectionModel().select(self.terms.model().index(0, 0), QItemSelectionModel.Select)

    def updateLinksModel(self, term=None, filterText=None):
        if not term:
            self.links.setModel(None)
        else:
            links = self.termsManager.links(term)
            links.sort()
            model = ListModel(links)
            if filterText:
                filter = FilterModel(filterText)
                filter.setSourceModel(model)
                model = filter
            self.links.setModel(model)
        
    def generateTestClicked(self):
        try:
            sequence = self.termsManager.sequence(length=4)            
            self.testOutput.setText(' > '.join(sequence))
        except AttemptsExpired:
            self.testOutput.setText('Attempts to generate sequence expired')

    def closeEvent(self, event):
        self.termsManager.save()
        super().closeEvent(event)

    def deleteItem(self, sender, index):
        if sender == self.terms:
            self.termsManager.delete(index.data(Qt.EditRole))
            self.updateTermsModel(None)
            self.updateLinksModel(None, None)
        elif sender == self.links:
            termSelection = self.terms.selectionModel().selectedIndexes()
            if termSelection:
                term = termSelection[0].data(Qt.EditRole)
                self.termsManager.delete(term, index.data(Qt.EditRole))
                if term in self.termsManager.terms():
                    self.updateLinksModel(term, None)
                else:
                    self.updateTermsModel(None)
                    self.updateLinksModel(None, None)
        self.termInput.setText('')
       
if __name__ == '__main__':   
    QCoreApplication.setOrganizationName("Word Elements")
    QCoreApplication.setApplicationName("Word Elements")
    app = QApplication(sys.argv)
    frame = Mainframe()
    sys.exit(app.exec_())