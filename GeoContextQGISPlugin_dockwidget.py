# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoContextQGISPluginDockWidget
                                 A QGIS plugin
 QGIS plugin to connect to GeoContext
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-11-22
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Kartoza
        email                : divan@kartoza.com
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

import os
import sys
import time

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QTableWidgetItem
from qgis.core import QgsSettings

# Directory for third party modules
third_party_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'third_party'))
if third_party_path not in sys.path:
    sys.path.append(third_party_path)

from coreapi.client import Client

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GeoContextQGISPlugin_dockwidget_base.ui'))


class GeoContextQGISPluginDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, canvas, point_tool, parent=None):
        """Constructor."""
        super(GeoContextQGISPluginDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Retrieves the schema data from the URL stored using the options dialog
        settings = QgsSettings()
        schema = settings.value('geocontext-qgis-plugin/schema', '', type=str)
        url = settings.value('geocontext-qgis-plugin/url', '', type=str)

        self.canvas = canvas  # QGIS project canvas
        self.point_tool = point_tool  # Canvas point tool - cursor used to selected locations
        self.cursor_active = True  # Sets to True because the point tool is now active

        # Get the list of context layers
        client = Client()
        self.document = client.get(schema)  # Retrieve the API schema
        self.list_context = client.action(document=self.document, keys=["csr", "list"])

        # Groups
        self.list_group = [{'key': 'bioclimatic_variables_group', 'name': 'Bioclimatic layers', 'description': 'N/A'},
                           {'key': 'monthly_precipitation_group', 'name': 'Monthly Precipitation', 'description': 'N/A'},
                           {'key': 'monthly_solar_radiation_group', 'name': 'Monthly Solar Radiation', 'description': 'N/A'},
                           {'key': 'monthly_max_temperature_group', 'name': 'Monthly Maximum Temperature', 'description': 'N/A'}]

        # Collections
        self.list_collection = [{'key': 'global_climate_collection', 'name': 'Global climate collection', 'description': 'N/A'},
                                {'key': 'healthy_rivers_collection', 'name': 'Healthy rivers collection', 'description': 'N/A'},
                                {'key': 'healthy_rivers_spatial_collection', 'name': 'Healthy rivers spatial filters', 'description': 'N/A'},
                                {'key': 'hydrological_regions', 'name': 'Hydrological regions', 'description': 'N/A'},
                                {'key': 'ledet_collection', 'name': 'LEDET collection', 'description': 'N/A'},
                                {'key': 'sa_boundary_collection', 'name': 'South African boundary collection', 'description': 'N/A'},
                                {'key': 'sa_climate_collection', 'name': 'South African climate collection', 'description': 'N/A'},
                                {'key': 'sa_land_cover_land_use_collection', 'name': 'South African land use collection', 'description': 'N/A'},
                                {'key': 'sa_river_ecosystem_collection', 'name': 'South African river collection', 'description': 'N/A'},
                                {'key': 'sedac_collection', 'name': 'Socioeconomic data and application center collection', 'description': 'N/A'}]

        # Creates a list of the key names and sorts it alphabetically
        list_key_names = []
        for context in self.list_context:
            name = context['name']
            list_key_names.append(name)
        list_key_names = sorted(list_key_names)

        # Adds the keys to the panel
        self.cbKey.addItems(list_key_names)

        # Retrieves panel parameters
        registry = self.cbRegistry.currentText()
        current_name = self.cbKey.currentText()

        # Retrieves the set information and updates the description table with it
        dict_current = self.find_name_info(current_name, registry)
        self.tblDetails.setItem(0, 0, QtWidgets.QTableWidgetItem(dict_current['key']))
        self.tblDetails.setItem(0, 1, QtWidgets.QTableWidgetItem(dict_current['name']))
        self.tblDetails.setItem(0, 2, QtWidgets.QTableWidgetItem(dict_current['description']))

        self.cbRegistry.currentTextChanged.connect(self.registry_changed)  # Triggered when the registry changes
        self.cbKey.currentTextChanged.connect(self.key_changed)  # Triggers when the key value changes

        self.btnClear.clicked.connect(self.clear_results_table)  # Triggers when the Clear button is clicked
        self.btnFetch.clicked.connect(self.fetch_btn_click)  # Triggers when the Fetch button is pressed
        self.btnCursor.clicked.connect(self.cursor_btn_click)  # Triggers when the Cursor button is pressed

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def registry_changed(self):
        """This method is called when the registry option is changed.
        The list in the panel which contains the key names will be updated.
        """

        registry = self.cbRegistry.currentText()  # Gets the registry type
        self.update_key_list(registry)  # Update the key list

    def key_changed(self):
        """This method is called when the key option in the panel window is changed.
        The information in the table which provides a description on the selected
        key will be update.
        """

        # Retrieved registry and newly selected key ID
        registry = self.cbRegistry.currentText()
        key_name = self.cbKey.currentText()

        # If the key name is empty, this step is skipped
        # This happens when the key list is cleared, which then triggers prior to the updating the list
        if len(key_name) > 0:
            dict_current = self.find_name_info(key_name, registry)

            # Updates the table
            self.tblDetails.setItem(0, 0, QtWidgets.QTableWidgetItem(dict_current['key']))
            self.tblDetails.setItem(0, 1, QtWidgets.QTableWidgetItem(dict_current['name']))
            self.tblDetails.setItem(0, 2, QtWidgets.QTableWidgetItem(dict_current['description']))

    def fetch_btn_click(self):
        """This method is called when the Fetch button on the panel window is pressed.
        The location (x and y) currently shown in the panel will be retrieved with no need to click
        in the canvas using the cursor.
        """

        settings = QgsSettings()

        # Gets the longitude and latitude
        x = self.lineLong.value()
        y = self.lineLat.value()

        # Request starts
        start = time.time()

        # Requests the data
        current_key_name = self.cbKey.currentText()
        data = self.point_request_panel(x, y)

        # Request ends
        end = time.time()
        rounding_factor = settings.value('geocontext-qgis-plugin/dec_places_panel', 3, type=int)
        request_time_ms = round((end - start) * 1000, rounding_factor)
        self.lblRequestTime.setText("Request time (ms): " + str(request_time_ms))

        registry = self.cbRegistry.currentText()  # Registry: Service, group or collection
        # The user has Service selected
        if registry.lower() == 'service':
            settings = QgsSettings()

            # If set, the table will automatically be cleared. This can be set in the options dialog
            auto_clear_table = settings.value('geocontext-qgis-plugin/auto_clear_table', False, type=bool)
            if auto_clear_table:
                self.clear_results_table()

            # Updates the table
            self.tblResult.insertRow(0)  # Always add at the top of the table
            self.tblResult.setItem(0, 0, QTableWidgetItem(current_key_name))
            self.tblResult.setItem(0, 1, QTableWidgetItem(str(data['value'])))
        # The user has Group selected
        elif registry.lower() == "group":  # UPDATE
            group_name = data['name']
            list_dict_services = data["services"]  # Service files for a group
            for dict_service in list_dict_services:
                key = dict_service['key']
                point_value = dict_service['value']
                service_key_name = dict_service['name']

                self.tblResult.insertRow(0)  # Always add at the top of the table
                self.tblResult.setItem(0, 0, QTableWidgetItem(service_key_name))  # Sets the key in the table
                self.tblResult.setItem(0, 1, QTableWidgetItem(str(point_value)))  # Sets the description
        # The user has Collection selected
        elif registry.lower() == "collection":
            list_dict_groups = data["groups"]  # Each group contains a list of the 'Service' data associated with the group
            for dict_group in list_dict_groups:
                group_name = dict_group['name']
                list_dict_services = dict_group["services"]  # Service files for a group
                for dict_service in list_dict_services:
                    key = dict_service['key']
                    point_value = dict_service['value']
                    service_key_name = dict_service['name']

                    self.tblResult.insertRow(0)  # Always add at the top of the table
                    self.tblResult.setItem(0, 0, QTableWidgetItem(service_key_name))  # Sets the key in the table
                    self.tblResult.setItem(0, 1, QTableWidgetItem(str(point_value)))  # Sets the description

    def cursor_btn_click(self):
        """This method is called when the Cursor button on the panel is clicked.
        The method will either enable or disable the cursor location selection, which
        retrieves the coordinates when the user clicks in the canvas
        """

        if self.cursor_active:
            self.canvas.unsetMapTool(self.point_tool)
            self.cursor_active = False
        else:
            self.canvas.setMapTool(self.point_tool)
            self.cursor_active = True

    def point_request_panel(self, x, y):
        """Return the value rettrieved from the ordered dictionary containing the requested data
        from the server. This method is used by the docket widget panel of the plugin.

        This method requests the data from the server for the given point coordinates.

        :param x: Longitude coordinate
        :type x: Numeric

        :param y: Latitude coordinate
        :type y: Numeric

        :returns: The value retrieved for the request for the provided location
        :rtype: Numeric
        """

        settings = QgsSettings()

        api_url = settings.value('geocontext-qgis-plugin/url')  # Base request URL
        registry = (self.cbRegistry.currentText())  # Registry type
        key_name = self.cbKey.currentText()  # Key name

        # Retrieves the key ID
        dict_key = self.find_name_info(key_name, registry)
        key = dict_key['key']

        # Performs the request
        client = Client()
        url_request = api_url + "query?" + 'registry=' + registry.lower() + '&key=' + key + '&x=' + str(x) + '&y=' + str(y) + '&outformat=json'

        data = client.get(url_request)
        return data

    def clear_results_table(self):
        """Clears the table in the panel. This can be called when the user clicks the
        Clear button, or if the user has automatic clearing enabled.
        """

        row_count = self.tblResult.rowCount()
        while row_count >= 0:
            self.tblResult.removeRow(row_count)
            row_count = row_count - 1

    def find_name_info(self, search_name, registry):
        """The method finds the key ID of a provided key name. It checks each case until
        the correct case is found.

        :param search_name: The search name to retrieve
        :type search_name: str

        :param registry: The registry type selected by the user in the panel
        :type registry: String

        :returns: The key ID of the searched key name; or None if the key could not be found
        :rtype: String
        """

        if registry == "Service":
            for context in self.list_context:
                current_name = context['name']
                if current_name == search_name:
                    return context
        elif registry == "Group":
            for group in self.list_group:
                current_name = group['name']
                if current_name == search_name:
                    return group
        elif registry == "Collection":
            for collection in self.list_collection:
                current_name = collection['name']
                if current_name == search_name:
                    return collection

        return None

    def update_key_list(self, registry_type="Service"):
        """This method updates the key name list shown in the panel. It will be called when
        the user changes the registry type
        """

        # Clears the combobox list prior to adding the updated list
        self.cbKey.clear()

        # Service type is the new selection
        if registry_type == "Service":
            settings = QgsSettings()

            # Docs which contains the schema of geocontext. Link can be changed in the options dialog
            schema = settings.value('geocontext-qgis-plugin/schema', '', type=str)

            # Requests the schema
            client = Client()
            self.document = client.get(schema)  # Retrieve the API schema

            # Requests the context list, which will contain the updated information
            self.list_context = client.action(document=self.document, keys=["csr", "list"])  # Get the list of context layers

            # Adds the names to a list, and then sorts the list alphabetically
            list_key_names = []
            for context in self.list_context:
                name = context['name']
                list_key_names.append(name)
            list_key_names = sorted(list_key_names)

            # Applies the updated list
            self.cbKey.addItems(list_key_names)
        elif registry_type == "Group":
            # Creates a list of the group layers
            list_key_names = []
            for group in self.list_group:
                name = group['name']
                list_key_names.append(name)

            # Updates the keys in the processing dialog
            self.cbKey.addItems(list_key_names)
        elif registry_type == "Collection":
            # Creates a list of the collection layers
            list_key_names = []
            for collection in self.list_collection:
                name = collection['name']
                list_key_names.append(name)

            # Updates the keys in the processing dialog
            self.cbKey.addItems(list_key_names)
