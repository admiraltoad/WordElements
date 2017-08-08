import json
import random
import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TermsManager():
    def __init__(self):
        self.filePath = os.path.join(os.path.dirname(QApplication.arguments()[0]), "data.json")
        self.data = {}
        self.cache = []
        self.load()

    def load(self):
        with open(self.filePath, 'r') as file:
            self.data = json.load(file)

    def save(self):
        with open(self.filePath, 'w') as file:
            json.dump(self.data, file)

    def terms(self):
        return list(self.data.keys())

    def links(self, term):
        try:
            return self.data[term]
        except:
            return []

    def add(self, term, link):
        if term not in self.terms():
            self.data[term] = [link]
        else:
            if link not in self.data[term]:
                self.data[term].append(link)

    def sequences(self, count=1, length=4, cached=False):
        # count determines how many to generate
        # length determines how long each one must be
        # cached determines if we can return sequences that have been returned in previous calls
        pass

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
    def __init__(self):
        super().__init__()  
        self.termsManager = TermsManager()
        self.initLayout()        
        self.setWindowTitle('Word Elements')
        self.resize(800, 624)
        self.center()
        self.show()
        self.updateTermsModel()

        # related to generating random sequences. will be removed once I make a 
        self.counter = 1
        self.cached = []        

    def createFileInputLayout(self):
        label = QLabel('Word Database:')
        filePath = QLineEdit(self.termsManager.filePath)
        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(filePath)
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
            self.updateLinksModel(terms[0], None)
        else:
            self.updateTermsModel(None)
            self.updateLinksModel(None, None)

    def termInputReturnPressed(self):     
        terms = [term for term in self.termInput.text().split(' ') if term]
        if len(terms) < 2:
            return
        for i in range(len(terms) - 1):
            self.termsManager.add(terms[i].lower(), terms[i + 1].lower())
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
        terms = self.termsManager.terms()
        try:
            i = random.randint(0, len(terms))
            first = terms[i]
            links = self.termsManager.links(first)
            useful = []
            for link in links:
                if link in terms:
                    useful.append(link)
            i = random.randint(0, len(useful))
            second = useful[i]
            links = self.termsManager.links(second)
            useful = []
            for link in links:
                if link in terms:
                    useful.append(link)
            i = random.randint(0, len(useful))
            third = useful[i]
            links = self.termsManager.links(third)
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

    def closeEvent(self, event):
        self.termsManager.save()
        super().closeEvent(event)
       
if __name__ == '__main__':   
    QCoreApplication.setOrganizationName("Word Elements")
    QCoreApplication.setApplicationName("Word Elements")
    app = QApplication(sys.argv)
    frame = Mainframe()
    sys.exit(app.exec_())