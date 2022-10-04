import qgis  # NOQA switch sip api
import os
from qgis.core import (
                       QgsVectorLayer,
                       QgsActionManager,
                       QgsAction,
                       QgsProcessingFeatureBasedAlgorithm)

from qgis.PyQt.QtGui import QIcon
from .AddActions_dialog import AddActionsDialog
from .utils import tr

SHAPE_TYPE = [tr("Polygon"), tr("Line")]


class AddActionsAlgorithm(QgsProcessingFeatureBasedAlgorithm):
    """
    Algorithm to create a donut shape.
    """

    def createInstance(self):
        return AddActionsAlgorithm()

    def name(self):
        return 'addActions'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'images/pie.png'))

    def displayName(self):
        return tr('addActions')
        self.dlg = AddActionsDialog()
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
            #uri = "file:///{}?delimiter={}&crs=epsg:4326&xField={}&yField={}".format(txtname, ",", "celllongitude","celllatitude")
            self.iface.messageBar().pushMessage("成功", "打印CSV路径：" + uri, level=Qgis.Success, duration=3)

            #vlayer = QgsVectorLayer(uri, layerName, "delimitedtext")

            layer = QgsVectorLayer("polygon?crs=epsg:4326&field=cellname:string(0,0)&field=pci:string(0,0)",
                                   "Output layer", "memory")
            self.manager = QgsActionManager(layer)
            print(layer)
            # should be empty to start with
            #self.assertEqual(self.manager.actions(), [])

            # add an action
            action1 = QgsAction(QgsAction.GenericPython, 'Test Action', 'i=1')
            self.manager.addAction(action1)
            self.assertEqual(len(self.manager.actions()), 1)
            self.assertEqual(self.manager.actions()[0].type(), QgsAction.GenericPython)
            self.assertEqual(self.manager.actions()[0].name(), 'Test Action')
            self.assertEqual(self.manager.actions()[0].command(), 'i=1')

            print("添加结束")
            # 将结果加载QGIS界面

            #if vlayer.isValid():
            #    QgsProject.instance().addMapLayer(vlayer)
            #else:
            #    print("图层加载失败！")

            pass
            # 在QGIS界面上打印结果
            self.iface.messageBar().pushMessage("成功", "加载图层：", level=Qgis.Success, duration=3)
