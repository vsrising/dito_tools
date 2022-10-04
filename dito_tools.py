# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DitoTools
                                 A QGIS plugin
 This plugin is developed for DITO O&M Optimization team
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-06-22
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Asun Feng
        email                : feng.zeng@ptr.dito.ph
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QFileDialog, QMenu,QToolButton
from qgis.core import Qgis,QgsProject,QgsVectorLayer, QgsApplication,QgsActionManager,QgsAction


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .dito_tools_dialog import DitoToolsDialog
from .ImportCSV_dialog import ImportCSVDialog
from .provider import ShapeToolsProvider
from .stFunctions import InitShapeToolsFunctions, UnloadShapeToolsFunctions
import os.path
import processing
import os
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr
import requests
def tr(string):
    return QCoreApplication.translate('@default', string)



class DitoTools:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.provider = ShapeToolsProvider()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DitoTools_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Dito Tools')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DitoTools', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Initialie the Shape Tools toolbar
        self.toolbar = self.iface.addToolBar('Dito Tools Toolbar')
        self.toolbar.setObjectName('DitoToolsToolbar')
        self.toolbar.setToolTip('Dito Tools Toolbar')

        # Initialize the create shape menu items
        menu = QMenu()
        menu.setObjectName('stCreateShapes')

        #导入CSV工单
        icon=QIcon(self.plugin_dir+'/images/dito.png')
        self.createPieAction = menu.addAction(icon, tr('Step1:Import Engineering parameter'), self.importCSVLocal)
        self.createPieAction.setObjectName('ImportCSV')
        # 增加的绘制扇区
        icon = QIcon(self.plugin_dir + '/images/dito.png')
        self.createPieAction = menu.addAction(icon, tr('Step2:Create pie wedge'), self.createPie)
        self.createPieAction.setObjectName('stCreatePie')
        # 增加actons测试
        icon = QIcon(self.plugin_dir + '/images/dito.png')
        self.createPieAction = menu.addAction(icon, tr('Step3:Add new actions'), self.addActionsLocal)
        self.createPieAction.setObjectName('addActions')



        # Add the shape creation tools to the menu
        icon = QIcon(self.plugin_dir + '/images/shapes.png')
        self.createShapesAction = QAction(icon, tr('Engineering parameter map'), self.iface.mainWindow())
        self.createShapesAction.setMenu(menu)
        self.iface.addPluginToVectorMenu('DitoTools', self.createShapesAction)






        # Add the shape creation tools to the toolbar
        self.createShapeButton = QToolButton()
        self.createShapeButton.setMenu(menu)

        self.createShapeButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.createShapeButton.triggered.connect(self.createShapeTriggered)
        self.createShapeToolbar = self.toolbar.addWidget(self.createShapeButton)
        self.createShapeToolbar.setObjectName('stCreateShape')

        # Add the processing provider
        QgsApplication.processingRegistry().addProvider(self.provider)
        InitShapeToolsFunctions()




        # will be set False in run()
        self.first_start = True
    def createShapeTriggered(self, action):
        self.createShapeButton.setDefaultAction(action)

    def unload(self):

        # remove from menu
        self.iface.removePluginVectorMenu('Shape Tools', self.createShapesAction)
        # Remove from toolbar
        self.iface.removeToolBarIcon(self.createShapeToolbar)
        # remove the toolbar
        del self.toolbar

        QgsApplication.processingRegistry().removeProvider(self.provider)
        UnloadShapeToolsFunctions()

        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Dito Tools'),
                action)
            self.iface.removeToolBarIcon(action)

    def importCSV(self):
        processing.execAlgorithmDialog('DitoTools:importCSV', {})

    def createPie(self):
        processing.execAlgorithmDialog('DitoTools:createpie', {})

    def addActions(self):
        processing.execAlgorithmDialog('DitoTools:addActions',{})

    def select_input_csvfile(self):
        filename, _filter = QFileDialog.getOpenFileName(
            self.dlg, "Select input file", "", "*.csv"
        )
        self.dlg.lineEditTxt.setText(filename)

    def select_input_file(self):
        filename, _filter = QFileDialog.getOpenFileName(
            self.dlg, "Select input file", "", "*.txt"
        )
        self.dlg.lineEditTxt.setText(filename)

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFilename(
            self.dlg, "Select output file", "", "*.txt"
        )
        self.dlg.lineEditShp.setText(filename)

        # 调用腾讯geocode服务

    def geoCode(self, address, key):
        url = 'https://apis.map.qq.com/ws/geocoder/v1/?address=' + address + '&key=' + key
        reponse = requests.get(url=url)
        reponse.encoding = 'utf-8'
        data = reponse.json()
        try:
            if data['status'] == 0:
                return {'address': address, 'title': data['result']['title'],
                        'point': 'POINT(' + str(data['result']['location']['lng']) + ' ' + str(
                            data['result']['location']['lat']) + ')',
                        'level': data['result']['level']}
        except BaseException as e:
            print(e)

        # 读txt文件

    def readTxt(self, path_str):
        f = open(path_str, 'r', encoding='utf-8')
        flines = f.readlines()
        address_list = []
        for l in flines:
            address_list.append(l.strip('\n'))
            print(l.strip('\n'))
        f.close()
        return address_list

        # 写shp文件

    def writeShp(self, path_str, geocode_list):
        # 支持中文路径
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # 属性表字段支持中文
        gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
        # 注册驱动
        ogr.RegisterAll()
        # 创建shp数据
        strDriverName = "ESRI Shapefile"
        oDriver = ogr.GetDriverByName(strDriverName)
        if oDriver == None:
            return "驱动不可用：" + strDriverName
        # 创建数据源
        oDS = oDriver.CreateDataSource(path_str)
        if oDS == None:
            return "创建文件失败：" + path_str
        # 创建一个多边形图层，指定坐标系为WGS84
        papszLCO = []
        geosrs = osr.SpatialReference()
        geosrs.SetWellKnownGeogCS("WGS84")
        # 线：ogr_type = ogr.wkbLineString
        # 点：ogr_type = ogr.wkbPoint
        ogr_type = ogr.wkbPoint
        # 面的类型为Polygon，线的类型为Polyline，点的类型为Point
        oLayer = oDS.CreateLayer("Point", geosrs, ogr_type, papszLCO)
        if oLayer == None:
            return "图层创建失败！"
        # 创建属性表
        # 创建id字段
        oId = ogr.FieldDefn("id", ogr.OFTInteger)
        oLayer.CreateField(oId, 1)
        # 创建address、title、level字段
        oAddress = ogr.FieldDefn("address", ogr.OFTString)
        oLayer.CreateField(oAddress, 1)
        oTitle = ogr.FieldDefn("title", ogr.OFTString)
        oLayer.CreateField(oTitle, 1)
        oLevel = ogr.FieldDefn("level", ogr.OFTInteger)
        oLayer.CreateField(oLevel, 1)
        oDefn = oLayer.GetLayerDefn()
        # 创建要素
        # 数据集
        for index, f in enumerate(geocode_list):
            oFeaturePolygon = ogr.Feature(oDefn)
            oFeaturePolygon.SetField("id", index)
            oFeaturePolygon.SetField("address", f['address'])
            oFeaturePolygon.SetField("title", f['title'])
            oFeaturePolygon.SetField("level", f['level'])
            geomPolygon = ogr.CreateGeometryFromWkt(f['point'])
            oFeaturePolygon.SetGeometry(geomPolygon)
            oLayer.CreateFeature(oFeaturePolygon)
        # 创建完成后，关闭进程
        oDS.Destroy()
        return "数据集创建完成！"

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DitoToolsDialog()
            # 点击按钮，确定路径
            self.dlg.pushButtonTxt.clicked.connect(self.select_input_file)
            # self.dlg.pushButtonShp.clicked.connect(self.select_output_file)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        print("打印对话框结果：", result)
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # 获取txt文件路径，shp文件路径，腾讯key
            txtname = self.dlg.lineEditTxt.text()
            shpname = self.dlg.lineEditShp.text()
            tencentkey = self.dlg.lineEditKey.text()
            address_list = self.readTxt(txtname)
            # 读txt文件中的内容，并将geocode结果写入shp
            geocode_list = []
            for address in address_list:
                print("打印读取的txt文本:", address)
                result = self.geoCode(address, tencentkey)
                if result != None:
                    geocode_list.append(result)
                    print("获取的地址：", result)
            self.writeShp(shpname, geocode_list)
            # 将结果加载QGIS界面
            layerName = shpname.split("/")[len(shpname.split("/")) - 1].replace(".shp", "")
            vlayer = QgsVectorLayer(shpname, layerName, "ogr")
            if vlayer.isValid():
                QgsProject.instance().addMapLayer(vlayer)
            else:
                print("图层加载失败！")

            pass
            # 在QGIS界面上打印结果
            self.iface.messageBar().pushMessage("成功", "加载图层：" + layerName, level=Qgis.Success, duration=3)

    def importCSVLocal(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
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


    def addActionsLocal(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
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
            # uri = "file:///{}?delimiter={}&crs=epsg:4326&xField={}&yField={}".format(txtname, ",", "celllongitude","celllatitude")


            # vlayer = QgsVectorLayer(uri, layerName, "delimitedtext")

            layer = QgsVectorLayer("polygon?crs=epsg:4326&field=cellname:string(0,0)&field=pci:string(0,0)",
                                   "Output layer", "memory")
            self.manager = QgsActionManager(layer)
            print("打印图层:",layer.type())
            # should be empty to start with

            self.iface.messageBar().pushMessage("开始addactions", "开始addactions：", level=Qgis.Success, duration=3)
            # add an action
            action1 = QgsAction(QgsAction.GenericPython, 'Test Action', 'i=1')
            self.manager.addAction(action1)
            print("打印action1的长度:",len(self.manager.actions()))
            self.iface.messageBar().pushMessage("成功", "addactions：", level=Qgis.Success, duration=3)
            print("添加结束")
            # 将结果加载QGIS界面


            #if vlayer.isValid():
            #    QgsProject.instance().addMapLayer(vlayer)
            #else:
            #    print("图层加载失败！")

            pass
            # 在QGIS界面上打印结果
            self.iface.messageBar().pushMessage("成功", "加载图层：", level=Qgis.Success, duration=3)