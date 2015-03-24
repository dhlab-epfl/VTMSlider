# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VeniceTimeMachine
                                 A QGIS plugin
 VeniceTimeMachine
                              -------------------
        begin                : 2014-03-13
        copyright            : (C) 2014 by Olivier Dalang
        email                : olivier.dalang@gmail.com
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import * 
from PyQt4.QtWebKit import *
from PyQt4 import uic

from qgis.core import *
from qgis.gui import *

from VTMHelp import VTMHelp
from VTMLoadData import VTMLoadData

from qgis.core import *

import os.path
import re

dateRange = [0,2050]

class VTMToolBar(QDockWidget):

    def __init__(self, iface, main):

        self.iface = iface
        self.main = main

        QDockWidget.__init__(self)
        uic.loadUi(os.path.dirname(__file__)+'/ui/vtmtoolbar.ui', self)

        self.helpButton.pressed.connect(self.doHelp)  
        self.idButton.pressed.connect(self.doShowId)   
        self.openButton.pressed.connect(self.doOpenFile)   
        self.loadDataButton.pressed.connect(self.doLoadData)  
        #TODOself.updatejoinsButton.pressed.connect(self.doUpdatejoins)   
        self.mergeButton.pressed.connect(self.doMerge)
        self.explodeButton.pressed.connect(self.doExplode)

        self.notexistButton.pressed.connect(self.doNotexist)
        self.copytodateButton.pressed.connect(self.doCopytodate)

        self.createrelationsButton.pressed.connect(self.doCreaterelations)
        self.removerelationsButton.pressed.connect(self.doRemoverelations)

        self.viewEntityButton.pressed.connect(self.doViewentity)
        self.listEventsButton.pressed.connect(self.doListproperties)
        self.viewRelationsButton.pressed.connect(self.doViewrelations)

        self.slider.valueChanged.connect( self.spinboxYear.setValue )
        self.spinboxYear.valueChanged.connect( self.slider.setValue )

        self.slider.valueChanged.connect( self.doDate )
        self.spinboxYear.valueChanged.connect( self.doDate )

        self.minValueSpinBox.valueChanged.connect( self.slider.setMinimum )
        self.maxValueSpinBox.valueChanged.connect( self.slider.setMaximum )
        self.minValueSpinBox.valueChanged.connect( self.spinboxYear.setMinimum )
        self.maxValueSpinBox.valueChanged.connect( self.spinboxYear.setMaximum )

    def enablePlugin(self):
        self.activeWidget.setEnabled(True)
    def disablePlugin(self):
        self.activeWidget.setEnabled(False)



    def doOpenFile(self):
        path = os.path.join( os.path.dirname(__file__),'qgis','dataentry.qgs')
        self.iface.addProject( path )
        self.main.loadLayers()

    def doDate(self, date):

        for layer in self.main.filteredEventsLayers:
            layer.setSubsetString( re.sub('\/\*\*\/[0-9.]*\/\*\*\/','/**/'+str(date)+'/**/',self.main.sqlFilter) )

        self.iface.mapCanvas().refresh()

    def doHelp(self):
        dlg = VTMHelp()
        dlg.exec_()

    def doShowId(self):
        QgsMessageLog.logMessage(self.iface.activeLayer().id(),'VTM Slider')
        #self.configDialog.exec_()

    def doLoadData(self):
        loadDataDialog = VTMLoadData(self.iface, self.main)
        loadDataDialog.exec_()
    
    """
    TODO
    def doUpdatejoins(self):
        for layerId in self.configDialog.timelayers:

            layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
            if layer is None or not isinstance(layer,QgsVectorLayer):
                continue

            joins = layer.vectorJoins()

            for join in joins:"""



    def doMerge(self):
        layer = self.iface.activeLayer()

        if layer not in self.main.filteredEventsLayers:
            self.iface.messageBar().pushMessage("VTM Slider","You can't merge on a layer that is not set as a time feature layer.", QgsMessageBar.WARNING, 2)
            return

        provider = layer.dataProvider()
        fieldIdx = provider.fieldNameIndex('entity_id')

        features = layer.selectedFeatures()
        smallestEntityId = None

        for f in features:
            entityId = f.attribute('entity_id')
            if smallestEntityId is None or entityId<smallestEntityId:
                smallestEntityId = entityId

        updateMap = {}
        for f in features:
            updateMap[f.id()] = { fieldIdx: smallestEntityId }
        provider.changeAttributeValues( updateMap )

        layer.removeSelection()

    def doExplode(self):
        layer = self.iface.activeLayer()

        if layer not in self.main.filteredEventsLayers:
            self.iface.messageBar().pushMessage("VTM Slider","You can't explode on a layer that is not set as a time feature layer.", QgsMessageBar.WARNING, 2)
            return

        provider = layer.dataProvider()
        fieldIdx = provider.fieldNameIndex('entity_id')

        features = layer.selectedFeatures()

        updateMap = {}
        for f in features:
            updateMap[f.id()] = { fieldIdx: None }
        provider.changeAttributeValues( updateMap )

        layer.removeSelection()


    def doNotexist(self):

        layer = self.iface.activeLayer()

        if layer not in self.main.filteredEventsLayers:
            self.iface.messageBar().pushMessage("VTM Slider","You can't set non existence on a layer that is not set as a time feature layer.", QgsMessageBar.WARNING, 2)
            return

        provider = layer.dataProvider()
        myFields = provider.fields()

        fieldEttyIdx = provider.fieldNameIndex('entity_id')
        fieldDateIdx = provider.fieldNameIndex('date')
        fieldKeyIdx = provider.fieldNameIndex('property_type_id')

        features = layer.selectedFeatures()
        newEvents = []
        for f in features:
            entityId = f.attribute('entity_id')
            feat = QgsFeature()
            feat.setFields( myFields )
            feat.setAttribute(fieldEttyIdx, entityId)
            feat.setAttribute(fieldDateIdx, self.spinboxYear.value())
            feat.setAttribute(fieldKeyIdx, 'geom')
            newEvents.append( feat )

        provider.addFeatures(newEvents)

        layer.removeSelection()

    def doListproperties(self):     

        self.main.eventsLayer.removeSelection()


        layer = self.iface.activeLayer()
        provider = layer.dataProvider()

        fieldEttyIdx = provider.fieldNameIndex('entity_id')
        fieldDateIdx = provider.fieldNameIndex('date')
        fieldKeyIdx = provider.fieldNameIndex('property_type_id')

        features = layer.selectedFeatures()

        for f in features:
            it = self.main.eventsLayer.getFeatures( QgsFeatureRequest().setFilterExpression ( '"entity_id" = '+str( f.attribute('entity_id') ) ) )
            self.main.eventsLayer.setSelectedFeatures( [ f.id() for f in it ] )
            break

        self.iface.showAttributeTable(self.main.eventsLayer)

    def doViewentity(self):

        self.main.entitiesLayer.removeSelection()


        layer = self.iface.activeLayer()
        provider = layer.dataProvider()
        fieldIdx = provider.fieldNameIndex('entity_id')

        features = layer.selectedFeatures()

        idsToSelect = []
        for f in features:
            idsToSelect.append( f.attribute('entity_id') )
        self.main.entitiesLayer.setSelectedFeatures(idsToSelect)

        self.iface.showAttributeTable(self.main.entitiesLayer)

    def doViewrelations(self):

        self.main.relationsLayer.removeSelection()


        layer = self.iface.activeLayer()
        provider = layer.dataProvider()
        fieldIdx = provider.fieldNameIndex('entity_id')

        features = layer.selectedFeatures()

        idsToSelect = []
        for f in features:
            idsToSelect.append( str(f.attribute('entity_id')) )

        # The important part: get the feature iterator with an expression
        ids = ','.join(idsToSelect)
        req = QgsFeatureRequest().setFilterExpression ( u'"a_id" IN ('+ids+') OR "b_id" IN ('+ids+')' )
        it = self.main.relationsLayer.getFeatures( req )
        self.main.relationsLayer.setSelectedFeatures( [ g.id() for g in it ] )

        self.iface.showAttributeTable(self.main.relationsLayer)

    def doCopytodate(self):
        layer = self.iface.activeLayer()

        if layer not in self.main.filteredEventsLayers:
            self.iface.messageBar().pushMessage("VTM Slider","You can't copy to date on a layer that is not set as a time feature layer.", QgsMessageBar.WARNING, 2)
            return

        provider = layer.dataProvider()
        myFields = provider.fields()

        fieldDateIdx = provider.fieldNameIndex('date')
        fieldEntityIdx = provider.fieldNameIndex('entity_id')

        features = layer.selectedFeatures()

        newFeatures = []
        for f in features:

            feat = QgsFeature()
            feat.setFields( myFields )
            feat.setAttribute( fieldDateIdx, self.spinboxYear.value() )
            feat.setAttribute( fieldEntityIdx, f.attribute('entity_id') )
            feat.setGeometry( f.geometry() )
            newFeatures.append( feat )
        layer.dataProvider().addFeatures(newFeatures)


    def doCreaterelations(self):


        provider = self.main.relationsLayer.dataProvider()
        myFields = provider.fields()
        fieldIdAIdx = provider.fieldNameIndex('a_id')
        fieldIdBIdx = provider.fieldNameIndex('b_id')

        # 2. Get the selected features        
        layer = self.iface.activeLayer()
        if layer not in self.main.filteredEventsLayers:
            self.iface.messageBar().pushMessage("VTM Slider","You can't create relations on a layer that is not set as a time feature layer.", QgsMessageBar.WARNING, 2)
            return
        features = layer.selectedFeatures()
        entities_ids = []
        for f in features:
            entities_ids.append( f.attribute('entity_id') )

        # 3. For each pair of selected features, create a relation
        newRelations = []
        for ent_id_a in entities_ids:
            for ent_id_b in entities_ids:
                if ent_id_a == ent_id_b:
                    continue
                feat = QgsFeature()
                feat.setFields( myFields )
                feat.setAttribute(fieldIdAIdx, ent_id_a)
                feat.setAttribute(fieldIdBIdx, ent_id_b)
                newRelations.append( feat )
                QgsMessageLog.logMessage('trying to add relation '+str(feat.attributes()),'VTM Slider')
                
        success = provider.addFeatures(newRelations)
        QgsMessageLog.logMessage('success ? '+str(success),'VTM Slider')

        layer.removeSelection()

    def doRemoverelations(self):
        layer = self.iface.activeLayer()

        if layer not in self.main.filteredEventsLayers:
            self.iface.messageBar().pushMessage("VTM Slider","You can't remove relations on a layer that is not set as a time feature layer.", QgsMessageBar.WARNING, 2)
            return

        relationsProvider = self.main.relationsLayer.dataProvider()

        features = layer.selectedFeatures()
        idsToUnrelate = []
        for f in features:
            idsToUnrelate.append( str(f.attribute('entity_id')) )
        ids = ','.join(idsToUnrelate)

        req = QgsFeatureRequest().setFilterExpression ( u'"a_id" IN ('+ids+') OR "b_id" IN ('+ids+')' )
        it = self.main.relationsLayer.getFeatures( req )
        relationsProvider.deleteFeatures( [ g.id() for g in it ] )

