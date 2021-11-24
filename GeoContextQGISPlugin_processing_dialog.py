# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GeoContextQGISPlugin_processing_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


import os

from PyQt5.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsSettings

from coreapi import Client

import subprocess

# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2
# do it before Qt imports

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GeoContextQGISPlugin_processing_dialog_base.ui'))


class ProcessingDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ProcessingDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        QDialog.__init__(self, parent)
        self.setupUi(self)

        settings = QgsSettings()
        url = settings.value('geocontext-qgis-plugin/url', '', type=str)

        client = Client()
        document = client.get(url)  # Retrieve the API schema

        self.lineUrl.setValue(url)
        registry = self.cbRegistry.currentText()

        list_context = client.action(document=document, keys=["csr", "list"])  # Get the list of context layers

        list_key_names = []
        for context in list_context:
            key = context['key']
            name = context['name']

            list_key_names.append(key)

        self.cbKey.addItems(list_key_names)
        self.lineEditFieldName.setText(self.cbKey.currentText() + "_value")

    def set_point_layer(self):
        input_points = self.cbInputPoints.currentLayer()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/input_points', input_points)

    def set_selected_features(self):
        selected_features = self.cbSelection.isChecked()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/selected_features', selected_features)

    def set_registry(self):
        registry = self.cbRegistry.currentText()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/registry', registry.lower())

    def set_key(self):
        key = self.cbKey.currentText()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/key', key)

    def set_field_name(self):
        field_name = self.lineEditFieldName.text()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/field_name', field_name)

    def set_output_points(self):
        output_dir = self.fwOutputPoints.filePath()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/output_points', output_dir)

    def set_open_file(self):
        open_file = self.cbOpenTable.isChecked()

        settings = QgsSettings()
        settings.setValue('geocontext-qgis-plugin/open_file', open_file)

    def get_point_layer(self):
        settings = QgsSettings()
        input_points = settings.value('geocontext-qgis-plugin/input_points')

        return input_points

    def get_key(self):
        settings = QgsSettings()
        key = settings.value('geocontext-qgis-plugin/key')

        return key

    def get_output_points(self):
        settings = QgsSettings()
        output_dir = settings.value('geocontext-qgis-plugin/output_points')

        return output_dir
