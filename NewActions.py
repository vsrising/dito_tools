# -*- coding: utf-8 -*-
"""QGIS Unit tests for QgsActionManager.
From build dir, run: ctest -R PyQgsActionManager -V
.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
__author__ = 'Nyall Dawson'
__date__ = '28/05/2016'
__copyright__ = 'Copyright 2016, The QGIS Project'

import qgis  # NOQA switch sip api

from qgis.core import (QgsVectorLayer,
                       QgsFeature,
                       QgsActionManager,
                       QgsAction,
                       QgsExpressionContext,
                       QgsField,
                       QgsFields
                       )
                       
                       
                       
                       
                       
                       
from qgis.PyQt.QtCore import QDir, QTemporaryFile, QUuid

from qgis.testing import start_app, unittest

import os
import time
import platform

#start_app()


class TestQgsActionManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #cls.layer = QgsVectorLayer("Point?field=fldtxt:string&field=fldint:integer&field=flddate:datetime","test_layer", "memory")
                                   
        cls.layer = QgsVectorLayer("polygon?crs=epsg:4326&field=cellname:string(0,0)&field=pci:string(0,0)",
                                   "Output layer", "memory")                           
        cls.manager = QgsActionManager(cls.layer)
        print(cls.layer)

        # make a little script to aid in recording action outputs
        # this is just a little python file which writes out its arguments to a text file
        cls.run_script_file = os.path.join(QDir.tempPath(), 'run_action.py')
        with open(cls.run_script_file, 'w') as s:
            s.write('import sys\n')
            s.write('open(sys.argv[1], "w").write(" ".join(sys.argv[2:]))\n')

    @classmethod
    def tearDownClass(cls):
        cls.layer = None
        cls.manager = None

    def get_temp_filename(self):
        tmpFile = QTemporaryFile()
        tmpFile.open()  # fileName is no available until open
        tmpName = tmpFile.fileName()
        tmpFile.close()
        tmpFile.setAutoRemove(False)
        return tmpName

    def create_action(self, dest_file, text_to_write):
        """ returns an action which writes some output to a file """
        return 'python {} {} {}'.format(self.run_script_file, dest_file, text_to_write)

    def testLayer(self):
        self.assertEqual(self.manager.layer(), self.layer)

    def testAddAction(self):
        """ Test adding actions """

        # should be empty to start with
        self.assertEqual(self.manager.actions(), [])

        # add an action
        action1 = QgsAction(QgsAction.GenericPython, 'Test Action', 'i=1')
        self.manager.addAction(action1)
        self.assertEqual(len(self.manager.actions()), 1)
        self.assertEqual(self.manager.actions()[0].type(), QgsAction.GenericPython)
        self.assertEqual(self.manager.actions()[0].name(), 'Test Action')
        self.assertEqual(self.manager.actions()[0].command(), 'i=1')


        print("添加结束")


    def testRemoveActions(self):
        """ test removing actions """

        # add an action
        self.manager.addAction(QgsAction.GenericPython, 'test_action', 'i=1')

        # clear the manager and check that it's empty
        self.manager.clearActions()
        self.assertEqual(self.manager.actions(), [])

        # add some actions
        id1 = self.manager.addAction(QgsAction.GenericPython, 'test_action', 'i=1')


        # remove non-existent action
        self.manager.removeAction(QUuid.createUuid())

        # remove them one by one

        self.assertEqual(self.manager.action(id1).name(), 'test_action')

        self.manager.removeAction(id1)
        self.assertEqual(len(self.manager.actions()), 1)

        self.assertEqual(len(self.manager.actions()), 0)

    def testDefaultAction(self):
        """ test default action for layer"""

        self.manager.clearActions()
        action1 = QgsAction(QgsAction.GenericPython, 'test_action', '', 'i=1', False, actionScopes={'Feature'})
        self.manager.addAction(action1)


        # initially should be not set
        self.assertFalse(self.manager.defaultAction('Feature').isValid())

        # set bad default action
        self.manager.setDefaultAction('Feature', QUuid.createUuid())
        self.assertFalse(self.manager.defaultAction('Feature').isValid())

        # set good default action
        self.manager.setDefaultAction('Feature', action1.id())
        self.assertTrue(self.manager.defaultAction('Feature').isValid())
        self.assertEqual(self.manager.defaultAction('Feature').id(), action1.id())


        # if default action is removed, should be reset to -1
        self.manager.clearActions()
        self.assertFalse(self.manager.defaultAction('Feature').isValid())

    def check_action_result(self, temp_file):
        with open(temp_file, 'r') as result:
            output = result.read()
        return output

    @unittest.expectedFailure(platform.system() != 'Linux')
    @unittest.skipIf(os.environ.get('QGIS_CONTINUOUS_INTEGRATION_RUN', 'true'), 'Test is flaky on Travis environment')
    def testDoAction(self):
        """ test running action """

        self.manager.clearActions()

        # simple action
        temp_file = self.get_temp_filename()
        id1 = self.manager.addAction(QgsAction.Unix, 'test_action', self.create_action(temp_file, 'test output'))

        fields = QgsFields()
        fields.append(QgsField('my_field'))
        fields.append(QgsField('my_other_field'))

        f = QgsFeature(fields, 1)
        f.setAttributes([5, 'val'])

        c = QgsExpressionContext()
        self.manager.doAction(id1, f, c)
        time.sleep(0.5)

        self.assertEqual(self.check_action_result(temp_file), 'test output')




if __name__ == '__main__':
    unittest.main()
    TestQgsActionManager.setUpClass()
    TestQgsActionManager.create_action()
    TestQgsActionManager.testAddAction()