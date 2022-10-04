import os
from geographiclib.geodesic import Geodesic

from qgis.core import (
    QgsField, QgsPointXY, QgsGeometry, QgsPropertyDefinition,
    QgsProject, QgsWkbTypes, QgsCoordinateTransform)

from qgis.core import (
    QgsProcessing,
    QgsProcessingFeatureBasedAlgorithm,
    QgsProcessingParameters,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum)

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant, QUrl
from .ImportCSV_dialog import ImportCSVDialog
from .settings import settings, epsg4326, geod
from .utils import tr, conversionToMeters, makeIdlCrossingsPositive, DISTANCE_LABELS

SHAPE_TYPE = [tr("Polygon"), tr("Line")]


class ImportCSVAlgorithm(QgsProcessingFeatureBasedAlgorithm):
    """
    Algorithm to create a donut shape.
    """



    def createInstance(self):
        return ImportCSVAlgorithm()

    def name(self):
        return 'importCSV'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'images/pie.png'))

    def displayName(self):
        return tr('Create pie wedge')
        self.dlg = ImportCSVDialog()
        # 点击按钮，确定路径
        self.dlg.pushButtonTxt.clicked.connect(self.select_input_csvfile)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # self.iface.messageBar().pushMessage("成功", "打印对话框结果ImportCSV：" + result, level=Qgis.Success, duration=3)
        # print("打印对话框结果ImportCSV：", result)
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
             # substitute with your code.
            # 获取txt文件路径，shp文件路径，腾讯key
            txtname = self.dlg.lineEditTxt.text()
            layerName = txtname.split("/")[len(txtname.split("/")) - 1].replace(".csv", "")

            # print(txtname)
            self.iface.messageBar().pushMessage("成功", "打印路径：" + txtname, level=Qgis.Success, duration=3)
            # 注意坑，和官网不一样，file后边必须是3个///
            uri = "file:///{}?delimiter={}&crs=epsg:4326&xField={}&yField={}".format(txtname, ",", "celllongitude",
                                                                                 "celllatitude")
            self.iface.messageBar().pushMessage("成功", "打印CSV路径：" + uri, level=Qgis.Success, duration=3)
            vlayer = QgsVectorLayer(uri, layerName, "delimitedtext")
            # 将结果加载QGIS界面

            if vlayer.isValid():
                QgsProject.instance().addMapLayer(vlayer)
            else:
                print("图层加载失败！")

            pass
            # 在QGIS界面上打印结果
            self.iface.messageBar().pushMessage("成功", "加载图层：", level=Qgis.Success, duration=3)
