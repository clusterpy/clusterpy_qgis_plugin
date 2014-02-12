from qgis.core import *
from PyQt4 import QtCore, QtGui

__all__ = ['Broker', 'MaxPWorker']

class Broker():
    def startWorker(self, worker):
        child = QtCore.QThread(self)
        worker.moveToThread(child)
        worker.finished.connect(finishWorker)
        thread.started.connect(worker.run)
        thread.start()
        self.thread = thread
        self.worker = worker

    def finishWorker(self, success, outputmsg):
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thead.deleteLater()
        if success:
            ## emit signal to add to canvas
            pass
        else:
            # we have an error, emit signal to display errormsg
            pass

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(object, basestring)

    def __init__(self):
        QtCore.QObject.__init__(self)

    def run(self):
        pass

class MaxPWorker(Worker):
    ERROR_MSG = u"There are features from the shapefile that are disconnected. \
                Check the following areas for errors in the geometry: "

    def __init__(self, info={}):
        Worker.__init__(self)
        for prop in info:
            self.__dict__[prop] = info[prop]

    def run(self):
        provider = self.layer.dataProvider()
        maxpfield = QgsField(name = "MAXP", type = 2)
        newfields = QgsFields()
        newfields.extend(provider.fields())
        newfields.append(maxpfield)

        clspyfeatures = {}
        for feat in provider.getFeatures():
            uid = feat.id()
            featids = []
            for _ftr in provider.getFeatures():
                if feat != _ftr and feat.geometry().touches(_ftr.geometry()):
                    featids.append(_ftr.id())
            neighbors = set(featids)
            neighbors.discard(uid)
            thresholdval = feat.attribute(self.thresholdattr)
            attributeval = feat.attribute(self.attrname)
            clspyfeatures[uid] = ClusterpyFeature(uid, thresholdval,
                                                neighbors, attributeval)

        outputmsg = None
        valid, islands = validtopology(clspyfeatures)
        if valid:
            regions = execmaxp(clspyfeatures,
                                self.threshold,
                                self.maxit,
                                self.tabusize,
                                self.tabumax)

            newlayer = QgsVectorFileWriter( self.output_path,
                                                        None,
                                                        newfields,
                                                        provider.geometryType(),
                                                        provider.crs())

            for area in self.layer.getFeatures():
                newarea = QgsFeature()
                newarea.setGeometry(area.geometry())
                attrs = area.attributes()
                attrs.append(regions[area.id()])
                newarea.setAttributes(attrs)
                newlayer.addFeature(newarea)

            del newlayer
            outputmsg = self.output_path
        else:
            outputmsg = self.ERROR_MSG + str(islands)

        self.finished.emit(valid, outputmsg)
