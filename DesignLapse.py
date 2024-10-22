import FreeCAD, math, shutil
from PIL import Image, ImageDraw
from PySide import QtGui, QtCore, QtWidgets



import FreeCADGui as Gui

class DesignLapseWindow(QtGui.QWidget):
    def __init__(self):
        super(DesignLapseWindow, self).__init__()
        #self.setWindowFlags(QtGui.WindowStaysOnTopHint)
        self.setWindowTitle("DesignLapse")

        # slider to adjust how much rotation per frame
        self.rotationLabel = QtGui.QLabel("Rotation per frame: " + str(150))

        self.rotationSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.rotationSlider.setMinimum(-1000)
        self.rotationSlider.setMaximum(1000)
        self.rotationSlider.setValue(150)
        self.rotationSlider.valueChanged.connect(self.updateRotationLabel)
		
        # slider to adjust ms per frame
        self.timeLabel = QtGui.QLabel("Milliseconds per frame: " + str(50))

        self.timeSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.timeSlider.setMinimum(1)
        self.timeSlider.setMaximum(1000)
        self.timeSlider.setValue(50)
        self.timeSlider.valueChanged.connect(self.updateTimeLabel)

        self.renderButton = QtGui.QPushButton("Render")
        self.renderButton.pressed.connect(self.render)
        
        # overall layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.rotationLabel)
        layout.addWidget(self.rotationSlider)
        layout.addWidget(self.timeLabel)
        layout.addWidget(self.timeSlider)
        layout.addWidget(self.renderButton)
        self.setLayout(layout)
        self.show()

    def updateRotationLabel(self, value):
        self.rotationLabel.setText("Rotation per frame: " + str(value))

    def updateTimeLabel(self, value):
        self.timeLabel.setText("Milliseconds per frame: " + str(value))

    def get_body_features(self, body):
        """Gets all features of a given body."""
        features = []

        # Check if the object is a PartDesign Body
        if body.TypeId == "PartDesign::Body":
            for obj in body.Group:
                # Check if the object is a feature
                if hasattr(obj, "TypeId") and obj.TypeId.startswith("PartDesign::") and not obj.TypeId.endswith("Plane"):
                    features.append(obj)

        return features

    def render(self):
        self.renderButton.setText("Rendering...")
        self.renderButton.repaint()  
        
        rotation = self.rotationSlider.value()
        frameTime = self.timeSlider.value()


        FreeCAD.Console.PrintMessage("Starting DesignLapse")

        # make tmp directory

        doc = FreeCAD.ActiveDocument 

        filePath = os.path.dirname(doc.FileName) + "/"

        tmpPath = filePath + "tmp/"

        if os.path.exists(tmpPath):
            shutil.rmtree(tmpPath)

        os.mkdir(tmpPath)

        if doc:
            body = doc.getObject("Body")  # Replace "Body" with the actual name of your body object
            features = self.get_body_features(body)

            index = 0
            images = []
            rotationMatrix = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), math.radians(rotation))

            for feature in features:
	
                FreeCAD.Console.PrintMessage("Processing the image for " + feature.Name + "\n")
	
        	    # this only toggles the body
                #Gui.Selection.addSelection(body, feature.Name)

                feature.ViewObject.Visibility = True

                body.Placement.Rotation = rotationMatrix * body.Placement.Rotation

                FreeCAD.ActiveDocument.recompute()
	
                path = doc.FileName

                #FreeCAD.Console.PrintMessage(path)

                imgPath = tmpPath + str(index) + "-" + feature.Name + '.png'

                Gui.activeDocument().activeView().saveImage(imgPath,1920,1080,'Current')

                images.append(Image.open(imgPath))

                index = index + 1

            images[0].save(filePath + os.path.splitext(os.path.basename(doc.FileName))[0] + ".gif", save_all=True, append_images=images[1:], optimize=False, duration=frameTime, loop=0)

            if os.path.exists(tmpPath):
                shutil.rmtree(tmpPath)

	

        FreeCAD.Console.PrintMessage("Done!\n")
        self.close()

DesignLapse = DesignLapseWindow()