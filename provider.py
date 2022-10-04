import os
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .createPie import CreatePieAlgorithm


class ShapeToolsProvider(QgsProcessingProvider):

    def unload(self):
        QgsProcessingProvider.unload(self)

    def loadAlgorithms(self):
        
        self.addAlgorithm(CreatePieAlgorithm())
       

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/images/shapes.png')

    def id(self):
        return 'DitoTools'

    def name(self):
        return 'Dito tools'

    def longName(self):
        return self.name()
