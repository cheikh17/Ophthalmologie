from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QSlider, QHBoxLayout, QLabel, QSpinBox
from PyQt5.QtCore import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from core.imageloader import ImageLoader

class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualiseur d'Images Médicales")
        self.setGeometry(100, 100, 800, 600)

        self.widgetCentral = QWidget(self)
        self.setCentralWidget(self.widgetCentral)

        self.layout = QVBoxLayout()
        self.widgetCentral.setLayout(self.layout)

        self.boutonChargerDICOM = QPushButton("Charger Série DICOM", self)
        self.boutonChargerDICOM.clicked.connect(self.charger_serie_dicom)
        self.layout.addWidget(self.boutonChargerDICOM)

        self.curseurCoupe = QSlider(self)
        self.curseurCoupe.setOrientation(Qt.Horizontal)
        self.curseurCoupe.valueChanged.connect(self.mettre_a_jour_coupe)
        self.layout.addWidget(self.curseurCoupe)

        self.layoutControles = QHBoxLayout()
        self.boutonZoomAvant = QPushButton("Zoom Avant", self)
        self.boutonZoomAvant.clicked.connect(self.zoom_avant)
        self.layoutControles.addWidget(self.boutonZoomAvant)

        self.boutonZoomArriere = QPushButton("Zoom Arrière", self)
        self.boutonZoomArriere.clicked.connect(self.zoom_arriere)
        self.layoutControles.addWidget(self.boutonZoomArriere)

        self.boutonRotationGauche = QPushButton("Rotation Gauche", self)
        self.boutonRotationGauche.clicked.connect(self.rotation_gauche)
        self.layoutControles.addWidget(self.boutonRotationGauche)

        self.boutonRotationDroite = QPushButton("Rotation Droite", self)
        self.boutonRotationDroite.clicked.connect(self.rotation_droite)
        self.layoutControles.addWidget(self.boutonRotationDroite)

        self.layout.addLayout(self.layoutControles)

        self.layoutSegmentation = QHBoxLayout()
        self.labelMin = QLabel("Seuil Min:", self)
        self.layoutSegmentation.addWidget(self.labelMin)

        self.seuilMin = QSpinBox(self)
        self.seuilMin.setRange(0, 4096)
        self.layoutSegmentation.addWidget(self.seuilMin)

        self.labelMax = QLabel("Seuil Max:", self)
        self.layoutSegmentation.addWidget(self.labelMax)

        self.seuilMax = QSpinBox(self)
        self.seuilMax.setRange(0, 4096)
        self.layoutSegmentation.addWidget(self.seuilMax)

        self.boutonSegmenter = QPushButton("Appliquer la Segmentation", self)
        self.boutonSegmenter.clicked.connect(self.appliquer_segmentation)
        self.layoutSegmentation.addWidget(self.boutonSegmenter)

        self.layout.addLayout(self.layoutSegmentation)

        self.boutonExporter = QPushButton("Exporter l'Image", self)
        self.boutonExporter.clicked.connect(self.exporter_image)
        self.layout.addWidget(self.boutonExporter)

        self.vtkWidget = QVTKRenderWindowInteractor(self.widgetCentral)
        self.layout.addWidget(self.vtkWidget)

        self.rendu = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.rendu)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.reslice = None
        self.reader = None
        self.acteur_image = None

    def charger_serie_dicom(self):
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le Répertoire de la Série DICOM")
        if directory:
            self.reslice, self.reader, extent = self.afficher_serie_images(directory)
            self.curseurCoupe.setMinimum(extent[4])
            self.curseurCoupe.setMaximum(extent[5])
            self.curseurCoupe.setValue(extent[4])

    def afficher_serie_images(self, directory):
        chargeur_image = ImageLoader()
        reslice, reader, extent = chargeur_image.load_image_series(directory)
        
        if self.acteur_image:
            self.rendu.RemoveActor(self.acteur_image)

        self.acteur_image = vtk.vtkImageActor()
        self.acteur_image.GetMapper().SetInputConnection(reslice.GetOutputPort())
        
        self.rendu.AddActor(self.acteur_image)
        self.rendu.SetBackground(0.1, 0.1, 0.1)
        self.rendu.ResetCamera()
        self.iren.Initialize()
        
        return reslice, reader, extent

    def mettre_a_jour_coupe(self, value):
        if self.reslice:
            chargeur_image = ImageLoader()
            slice_output = chargeur_image.get_slice(self.reslice, value)
            self.vtkWidget.GetRenderWindow().Render()

    def zoom_avant(self):
        camera = self.rendu.GetActiveCamera()
        camera.Zoom(1.2)
        self.vtkWidget.GetRenderWindow().Render()

    def zoom_arriere(self):
        camera = self.rendu.GetActiveCamera()
        camera.Zoom(0.8)
        self.vtkWidget.GetRenderWindow().Render()

    def rotation_gauche(self):
        self.acteur_image.RotateZ(-10)
        self.vtkWidget.GetRenderWindow().Render()

    def rotation_droite(self):
        self.acteur_image.RotateZ(10)
        self.vtkWidget.GetRenderWindow().Render()

    def appliquer_segmentation(self):
        seuil_min = self.seuilMin.value()
        seuil_max = self.seuilMax.value()

        if self.reslice:
            threshold = vtk.vtkImageThreshold()
            threshold.SetInputConnection(self.reslice.GetOutputPort())
            threshold.ThresholdBetween(seuil_min, seuil_max)
            threshold.SetInValue(255) 
            threshold.SetOutValue(0)   
            threshold.Update()

            self.acteur_image.GetMapper().SetInputConnection(threshold.GetOutputPort())
            self.vtkWidget.GetRenderWindow().Render()

    def exporter_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter l'Image", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            window_to_image_filter = vtk.vtkWindowToImageFilter()
            window_to_image_filter.SetInput(self.vtkWidget.GetRenderWindow())
            window_to_image_filter.Update()

            writer = vtk.vtkPNGWriter()
            writer.SetFileName(file_path)
            writer.SetInputConnection(window_to_image_filter.GetOutputPort())
            writer.Write()