# -*- coding: utf-8 -*-

#-----------------------------------------------------------
#
# fTools
# Copyright (C) 2008-2011  Carson Farmer
# EMAIL: carson.farmer (at) gmail.com
# WEB  : http://www.ftools.ca/fTools.html
#
# A collection of data management and analysis tools for vector data
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

# Utility functions ***THE ORIGINAL FILE CONTAINS MANY MORE METHODS***
# -------------------------------------------------
#
# addShapeToCanvas( QString *file path )
# saveDialog( QWidget *parent )
#
# -------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import locale

# Convinience function to add a vector layer to canvas based on input shapefile path ( as string )
def addShapeToCanvas( shapefile_path ):
    file_info = QFileInfo( shapefile_path )
    if file_info.exists():
        layer_name = file_info.completeBaseName()
    else:
        return False
    vlayer_new = QgsVectorLayer( shapefile_path, layer_name, "ogr" )
    if vlayer_new.isValid():
        QgsMapLayerRegistry.instance().addMapLayers( [vlayer_new] )
        return True
    else:
        return False

# Generate a save file dialog with a dropdown box for choosing encoding style
def saveDialog( parent, filtering="Shapefiles (*.shp *.SHP)"):
    settings = QSettings()
    dirName = settings.value( "/UI/lastShapefileDir" )
    encode = settings.value( "/UI/encoding" )
    fileDialog = QgsEncodingFileDialog( parent, "Save output shapefile", dirName, filtering, encode )
    fileDialog.setDefaultSuffix( "shp" )
    fileDialog.setFileMode( QFileDialog.AnyFile )
    fileDialog.setAcceptMode( QFileDialog.AcceptSave )
    fileDialog.setConfirmOverwrite( True )
    if not fileDialog.exec_() == QDialog.Accepted:
            return None, None
    files = fileDialog.selectedFiles()
    settings.setValue("/UI/lastShapefileDir", QFileInfo( unicode( files[0] ) ).absolutePath() )
    return ( unicode( files[0] ), unicode( fileDialog.encoding() ) )

