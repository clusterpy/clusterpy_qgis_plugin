# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Sergio Botero'
__date__ = 'Nov 2014'
__copyright__ = '(C) 2014, RiSE Group'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

__all__ = ['execmaxp', 'ClusterpyFeature', 'validtopology']

from random import choice, sample

MAXNUM = 99999

# Global information about the execution
LAYERFEATURES = None
REQTHRESHOLD = None
EPSILON = 1e-5

class ClusterpyFeature:
    """ Structure to represent a QGIS feature with the attributes of interest
    for Clusterpy
    """
    def __init__(self, uid, threshold = 0, neighbors = set(), attribute = 0):
        """ ClusterpyFeature initialiazer
        Parameters are:
        [1] uid         -> An Int value with the id of the feature.
        [2] threshold   -> A double with the value used for the threshold
                requirement in the creation of regions.
        [3] neighbors   -> A set of ids (Integers) that are considered to be
                neighboring features.
        [4] attribute   -> A double value that holds the attribute to use for
                clustering.

        A feature is never considered to be its own neighbor. If the set
        contains it, it will be removed.
        """
        if uid in neighbors:
            neighbors.remove(uid)

        self.uid = uid
        self.threshold = threshold
        self.neighbors = neighbors
        self.attribute = attribute

class ClusterpyMap(list):
    """ Structure to represent a feasible regions configuration """
    def __init__(self, *args):
        list.__init__(self, *args)
        self.objfunction = 99999

    @property
    def regions(self):
        """ Returns an array of length |self| where position i holds the value
        of the region for feature i"""
        region = 0
        regions = dict()
        for partition in self:
            for feature in partition:
                regions[feature.uid] = region
            region += 1
        return regions.values()

    def computeobjfunction(self):
        """ Perform computation of the objective function for the current
        region configuration """
        tmpobjfunc = 0.0
        for region in self:
            rcentroid = centroid(region)
            for feature in region:
                tmpobjfunc += distancetoregion(feature, rcentroid)
        self.objfunction = tmpobjfunc
        return self.objfunction

    def clone(self):
        """ Creates a clone of the distribution of the sets but does not make
        copies of the features to ensure consistency.
        This method will work as a copy.deepcopy but without going to the last
        level (the ClusterpyFeature)

        Returns a new copy of the ClusterpyMap
        """
        clone = ClusterpyMap()
        for region in self:
            clone.append(ClusterpyRegion(region))
        return clone

class SetOfFeatures(set):
    """ Set subclass with additions to hold ClusterpyFeatures """
    @property
    def ids(self):
        """ Returns a list with the ids of every feature contained """
        return [feat.uid for feat in self]

class ClusterpyRegion(SetOfFeatures):
    """ A class to represent an already formed region """
    def thresholdsum(self):
        """ Returns the sum of threshold values from the features contained
        in the clusterpyregion"""
        return sum([feat.threshold for feat in self])

    def canremovefeature(self, featuretoremove):
        """ Returns a boolean indicating if the feature (featuretoremove) can
        leave the region without breaking contiguity of the region and without
        leaving the total threshold of the region without the required
        threshold

        Parameters are:
        [1] feturetoremove -> A feature from the region

        """
        fcount = len(self)
        canremove = False
        if fcount == 1:
            pass
        elif fcount == 2:
            newthreshold = self.thresholdsum() - featuretoremove.threshold
            if newthreshold >= REQTHRESHOLD:
                canremove = True
        elif fcount > 2:
            _tmpneighbors = featuretoremove.neighbors.difference(self.ids)
            if len(_tmpneighbors) > 0:
                newthreshold = self.thresholdsum() - featuretoremove.threshold
                if newthreshold >= REQTHRESHOLD:
                    regionids = set(self.ids)
                    regionids.remove(featuretoremove.uid)
                    iterator = iter(self)
                    seed = iterator.next()
                    if seed == featuretoremove:
                        seed = iterator.next()
                    nextneighbors = set([seed])
                    while len(nextneighbors) > 0:
                        nextneighbor = nextneighbors.pop()
                        regionids.remove(nextneighbor.uid)
                        for uid in nextneighbor.neighbors:
                            if uid in regionids:
                                nextneighbors.add(LAYERFEATURES[uid])
                    if len(regionids) == 0:
                        canremove = True
        return canremove

def sendprogress(progressobj, value):
    if progressobj is not None:
        progressobj(value)

def execmaxp(layer, threshold, maxit, tabulength, maxtabusteps, progress=None):
    """ Max-p clustering algorithm
    Parameters are:
    [1] layer       -> A dictionary where keys are feature IDs and values are
            ClusterpyFeatures
    [2] threshold   -> A double value that has to be satisfied for each region.
    [3] maxit       -> An Int value, the number of initial configurations to
            start exloring.
    [4] tabulength  -> An Int value that sets the number of tabu features for
            the local search phase.
    [5] maxtabusteps-> An Int value that sets the number of maximum number of
            steps allowed to try a non-optimal possibility in local search.

    Returns a list where the value at position i is the number of the region to
            which feature i belongs.
    """
    global LAYERFEATURES, REQTHRESHOLD
    LAYERFEATURES = layer
    REQTHRESHOLD = threshold
    feasiblepartitions = list()
    maxp = 0
    sendprogress(progress, 10.0)
    for _tmp in xrange(maxit):
        partitions, enclaves, assignedfeatures = growregions()
        numregions = len(partitions)
        if numregions > maxp:
            del feasiblepartitions[:]
            feasiblepartitions.append((partitions, enclaves, assignedfeatures))
            maxp = numregions
        elif numregions == maxp:
            feasiblepartitions.append((partitions, enclaves, assignedfeatures))
    sendprogress(progress, 50.0)
    bestobjfunction = MAXNUM
    bestpartition = None
    for partitions, enclaves, assigned in feasiblepartitions:
        regions = assignenclaves(partitions, enclaves, assigned)
        localsearch(regions, tabulength, maxtabusteps)
        if regions.objfunction < bestobjfunction or bestpartition == None:
            bestobjfunction = regions.objfunction
            bestpartition = regions.clone()
    sendprogress(progress, 90.0)
    return bestpartition.regions

def growregions():
    """ Phase 1 of maxp algorithm [Not to be called explicitly] """
    partitions = ClusterpyMap()
    unassigned = SetOfFeatures(LAYERFEATURES.values())
    assigned   = SetOfFeatures()
    visited    = SetOfFeatures()

    featurescount = len(LAYERFEATURES)
    while len(visited) < featurescount:
        unvisited = unassigned.difference(visited)
        feature = choice(list(unvisited))
        unassigned.remove(feature)
        assigned.add(feature)
        visited.add(feature)
        feasible = True
        if feature.threshold >= REQTHRESHOLD:
            region = ClusterpyRegion([feature])
        else:
            region = ClusterpyRegion([feature])
            neighbors = feature.neighbors.difference(assigned.ids)
            acumthreshold = 0
            while acumthreshold < REQTHRESHOLD:
                if len(neighbors) > 0:
                    fneighbors = [LAYERFEATURES[uid] for uid in neighbors]
                    nextfeature = selectnextfeature(fneighbors, region)
                    region.add(nextfeature)
                    neighbors.remove(nextfeature.uid)
                    newneighbors = nextfeature.neighbors.difference(assigned.ids)
                    neighbors.update(newneighbors)
                    acumthreshold += nextfeature.threshold
                    unassigned.remove(nextfeature)
                    assigned.add(nextfeature)
                elif acumthreshold < REQTHRESHOLD:
                    feasible = False
                    unassigned.update(region)
                    assigned.difference_update(region)
                    break
        if feasible:
            partitions.append(region)
            visited.update(region)
    return partitions, unassigned, assigned

def assignenclaves(partitions, enclaves, assignedfeatures):
    """ Phase 2 of Maxp algorithm [Not to be called explicitly] """
    while len(enclaves) > 0:
        feature = None
        assignedneighbor = None
        for feat in enclaves:
            _tmpneighbors = feat.neighbors.intersection(assignedfeatures.ids)
            if len(_tmpneighbors) > 0:
                assignedneighbor = [LAYERFEATURES[uid] for uid in _tmpneighbors]
                feature = feat
                break
        neighborregions = list()
        for partition in partitions:
            for neighbor in assignedneighbor:
                if neighbor in partition:
                    neighborregions.append(partition)
                    break
        selectedregion = selectnextregion(neighborregions, feature)
        selectedregion.add(feature)
        assignedfeatures.add(feature)
        enclaves.remove(feature)
    return partitions

def localsearch(regions, tabulength, maxtabusteps):
    """ Local search phase in Max-p. TabuMove [Not to be called explicitly] """
    bestregions = regions
    tmpregions = regions.clone()
    tabulist = list()
    tabusteps = 0
    aspirationfit = regions.computeobjfunction()
    while tabusteps < maxtabusteps:
        tabusteps += 1
        randomfeature, inregion, toregions = randomcandidatefeature(tmpregions)
        if randomfeature:
            destregion = choice(toregions)
            inregion.remove(randomfeature)
            destregion.add(randomfeature)
            currentfit = tmpregions.computeobjfunction()

            if (randomfeature, destregion) not in tabulist:
                tabulist.append((randomfeature, destregion))
                if aspirationfit - currentfit > EPSILON:
                    bestregions = tmpregions.clone()
                    tabusteps = 0
            else:
                if aspirationfit - currentfit > EPSILON:
                    bestregions = tmpregions.clone()
                    tabusteps = 0
                else:
                    destregion.remove(randomfeature)
                    inregion.add(randomfeature)
            tabulist[:] = tabulist[-tabulength:]
        else:
            tabusteps = maxtabusteps
    regions = bestregions

def selectnextfeature(possiblefeatures, regiontojoin):
    """ Selects the best feature from possiblefeature to add to regiontojoin
    using the minimum distance
    Parameters are:
    [1] possiblefeatures    -> list of clusterpyfeatures, candidates to join
    [2] regiontojoin        -> set of clusterpyfeatures already in a region

    [Not to be called explicitly]
    """
    rcentroid = centroid(regiontojoin)
    mindistance = MAXNUM
    selectedfeature = None
    for feature in possiblefeatures:
        distance = distancetoregion(feature, rcentroid)
        if distance < mindistance:
            mindistance = distance
            selectedfeature = feature

    if selectedfeature == None:
        selectedfeature = choice(possiblefeatures)
    return selectedfeature

def selectnextregion(possibleregions, featuretoadd):
    """ Selects the best region from possibleregions to receive featuretoadd
    using the minimum distance
    Parameters are:
    [1] possibleregions -> list of sets containing clusterpyfeatures, the region
    [2] featuretoadd    -> clusterpyfeature, candidate to join a region

    Returns a ClusterpyRegion
    [Not to be called explicitly]
    """
    mindistance = MAXNUM
    selectedregion = None
    for region in possibleregions:
        rcentroid = centroid(region)
        distance = distancetoregion(featuretoadd, rcentroid)
        if distance < mindistance:
            mindistance = distance
            selectedregion = region

    if selectedregion == None:
        selectedregion = choice(possibleregions)
    return selectedregion

def centroid(region):
    """ Returns the attribute centroid of a given region.
    Parameters are:
    [1] region -> A set of clusterpyfeatures.

    Returns a double with the centroid of attribute for the entire region (since
    the first version works only on one attribute, later this should be an array
    of values, one for each attribute).

    [Not to be called explicitly]
    """
    centroidval = 0.0
    for feature in region:
        centroidval += feature.attribute
    centroidval /= float(len(region))
    return centroidval

def distancetoregion(feature, regioncentroid):
    """ Returns the attribute distance from a feature to the centroid
    of a region.
    Parameters are:
    [1] feature         -> A ClusterpyFeature
    [2] regioncentroid  -> A double value for the centroid of a region.
            (In future versions this should be an array of attributes to allow
            a multivariable clustering).

    Returns the distance.

    [Not to be called explicitly]
    """
    distance = 0.0
    distance = feature.attribute - regioncentroid
    distance *= distance
    return distance

def randomcandidatefeature(clspmap):
    """ Returns a random feature from the ClusterpyMap that can be moved from
    the current region and the region.
    Parameters are:
    [1] clspmap -> A ClusterpyMap

    Returns a ClusterpyFeature its region and neighboring regions tuple or None
    [Not to be called explicitly]
    """
    sampledregions = sample(clspmap, len(clspmap))
    for region in sampledregions:
        sampledfeatures = sample(region, len(region))
        for feature in sampledfeatures:
            if region.canremovefeature(feature):
                toregions = featureneighborregions(clspmap, feature, region)
                return feature, region, toregions
    return None, None, None

def featureneighborregions(regions, feature, fromregion):
    """ Returns the regions (partitions) next to the feature
    Parameters are:
    [1] regions     -> A ClusterpyMap
    [2] feature     -> A ClusterpyFeature
    [3] fromregion  -> A ClusterpyRegion

    Returns a list of ClusterpyRegions
    """
    _tmpneighbors = feature.neighbors.difference(fromregion.ids)
    assignedneighbor = [LAYERFEATURES[uid] for uid in _tmpneighbors]
    neighborregions = list()
    for partition in regions:
        for neighbor in assignedneighbor:
            if neighbor in partition:
                neighborregions.append(partition)
                break
    return neighborregions

def validtopology(features):
    """ Checks if the topology of the shapefile is valid for running
    Clusterpy.
    Parameters are:
    [1] A dictionary of ClusterpyFeature

    Returns a tuple. A boolean value: True if valid, False otherwise.
    And an array containing the uids of the features causing trouble.
    """
    topology = { }
    feature = None
    for feature in features.values():
        if len(feature.neighbors) < 1:
            return False, [feature.uid]
        topology[feature.uid] = feature.neighbors

    tovisit = set([feature.uid])
    visitedareas = set([feature.uid])
    while len(tovisit) > 0:
        area = tovisit.pop()
        visitedareas.add(area)
        tovisit.update(topology[area])
        tovisit.difference_update(visitedareas)
    islands = visitedareas.symmetric_difference(topology.keys())
    return len(islands) == 0, list(islands)
