import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class AccChartView(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Account Chart Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Create a QSqlDatabase
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('projects.db')

        if not self.db.open():
            print("Error: Connection to the database failed")
            sys.exit(1)

        # Set up the tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(
            ['ID', 'ParentID', 'Code', 'Name', 'LatinName'])
        self.tree_widget.setColumnWidth(0, 150)  # Set width for ID column

        # Populate the tree widget with data from the database
        self.populate_tree()

        self.layout.addWidget(self.tree_widget)

    def populate_tree(self):
        query = QSqlQuery(
            "SELECT ID, ParentID, Code, Name, LatinName FROM mnrAcc")
        items = {}

        while query.next():
            item = QTreeWidgetItem()
            for column in range(query.record().count()):
                # Convert to str
                item.setText(column, str(query.value(column)))
                item.setFlags(item.flags() | Qt.ItemIsEditable)

            account_id = query.value('ID')
            parent_id = query.value('ParentID')
            items[account_id] = item

            if parent_id in items:
                parent_item = items[parent_id]
                parent_item.addChild(item)
            else:
                self.tree_widget.addTopLevelItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccChartView()
    window.show()
    sys.exit(app.exec_())
