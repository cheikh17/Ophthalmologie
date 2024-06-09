import sys
from PyQt5.QtWidgets import QApplication
from ui.mainwindow import FenetrePrincipale  # Mettez à jour l'importation

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()  # Utilisez le nouveau nom de la classe
    fenetre.show()
    sys.exit(app.exec_())