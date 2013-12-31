##  bnExport GUI
############################################################
## GUI for exporting multiple object/channel/udim combos.
## -------------------
## Install: Copy this file to your user Mari/Scripts folder.
## (Create a Mari/Scripts directory if there is none)
## Versions supported: 2.5.x
## Linux64, Win64 Tested.
## -------------------
## Copyright Ben Neall 2013-2014
## Contact: bneall@gmail.com
############################################################

import time
import datetime
import PythonQt.QtGui as QtGui
import PythonQt.QtCore as QtCore

icon_path = mari.resources.path('ICONS')
imgFormats = mari.images.supportedWriteFormats()

## Defaults ##
defaultFormat = 'tif'
defaultTemplate = '$ENTITY_$CHANNEL.$UDIM'

def selectPatch(object, udim):
	'''Selectes patch indicated in GUI'''
	geo = mari.geo.find(object)
	for patch in geo.patchList():
		patch.setSelected(False)
	patch = geo.patch(int(udim)-1001)
	patch.setSelected(True)

def sceneData(mode):
	'''Gets Mari scene data'''
	geo = mari.geo.current()
	channel = geo.currentChannel()
	patchList = geo.selectedPatches()
	udimList = [(str(patch.udim())) for patch in patchList]
	bitDepth = channel.depth()
	resolution = channel.width()
	
	if mode == 'geo':
		return geo.name()
	elif mode == 'chan':
		return channel.name()
	elif mode == 'udim':
		return udimList
	elif mode == 'depth':
		return bitDepth
	elif mode == 'res':
		return resolution
	
def report(reportList, path):
		'''Report log for complete exports'''
		print '\n---------------Export Report------------------'
		print 'Export Path: %s\n' % path
		for item in reportList:
			object = item[0]
			channel = item[1]
			udims = item[2]
			time = item[3]
			print 'Export for: %s:%s' % (object, channel)
			print '----------------------------------------------'
			print 'UDIMs exported:\n%s' % [str(udim) for udim in udims]
			print 'Elapsed Time: %s' % time
			print '----------------------------------------------\n'
	
def exportMaps(objDict, path, format, template):
	'''Exports maps from dictionary supplied by GUI'''
	## Missing options
	if not objDict:
		mari.utils.message('Nothing to export')
		return
	elif not path:
		mari.utils.message('No export path set')
		return
	
	## Report data
	reportList = []
	
	## Progress maximum
	maxStep = 0
	for x in objDict:
		for i in objDict[x]:
			maxStep += 1
	
	# Progress Dialog
	progressDiag = ProgressDialog(maxStep)
	progressDiag.show()
	
	progStep = 0
	startJobTime = time.time()
	for object in objDict:
		mariGeo = mari.geo.find(object)
		for channel in objDict[object]:
			mariChan = mariGeo.findChannel(channel)
			udims = objDict[object][channel]
			uvs = [(int(x)-1001) for x in udims]
			file_template = '%s/%s.%s' % (path, template, format)
			
			## Progress settings
			progressDiag.label.setText('Exporting %s\nUDIM Count: %d' % (channel, len(uvs)))
			mari.app.processEvents()
			if progressDiag.breakBake == True:
				progressDiag.close()
				return
			
			## Export
			startBakeTime = time.time()
			if len(mariChan.layerList()) > 1:
				mariChan.exportImagesFlattened(file_template, 0, uvs)
			else:
				mariChan.exportImages(file_template, 0, uvs)
			endBakeTime = time.time()
			elapsedBakeTime = endBakeTime - startBakeTime
			elapsedBakeTime = str(datetime.timedelta(seconds=elapsedBakeTime))
			
			## Report
			reportList.append([object, channel, udims, elapsedBakeTime])
			
			## Progress step
			progStep += 1
			progressDiag.pbar.setValue(progStep)
		
	endJobTime = time.time()
	elapsedJobTime = endJobTime - startJobTime
	elapsedJobTime = str(datetime.timedelta(seconds=elapsedJobTime))
	report(reportList, path)
	mari.utils.message('Exporting finished.\nElapsed time: %s' % elapsedJobTime)
	
class ProgressDialog(QtGui.QDialog):
	'''progress thing'''
	def __init__(self, maxStep):
		super(ProgressDialog, self).__init__()
		self.setWindowTitle('bnExporter')
	#--# Var
		self.breakBake = False
	#--# Layout
		layout = QtGui.QVBoxLayout()
		self.setLayout(layout)
		self.pbar = QtGui.QProgressBar(self)
		self.pbar.setRange(0, maxStep)
		self.pbar.setGeometry(30, 40, 200, 25)
		self.label = QtGui.QLabel('Exporting..')
	#--# Connection
		self.pbar.connect("valueChanged (int)", self.status)
	#--# Progress GUI
		layout.addWidget(self.label)
		layout.addWidget(self.pbar)
	
	def status(self):
		if self.pbar.value == self.pbar.maximum:
			self.close()
	
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_Escape:
			self.breakBake = True

class ExportDialog(QtGui.QFileDialog):
	'''File Dialog with Directory Mode'''
	def __init__(self):
		super(ExportDialog, self).__init__()
		self.setFileMode(2)
		self.setReadOnly(False)

class ExportQtGui(QtGui.QWidget):
	'''Export Tool GUI'''
	def __init__(self):
		super(ExportQtGui, self).__init__()
	#--# Create Groups
		self.mainGroup = QtGui.QGroupBox('Export List')
		self.optionGroup = QtGui.QGroupBox('Options')
	#--# Create Layouts
		layoutV1_main = QtGui.QVBoxLayout()
		layoutV2_grp = QtGui.QVBoxLayout()
		layoutV3_grp = QtGui.QVBoxLayout()
		layoutH1_wdg = QtGui.QHBoxLayout()
		layoutH2_wdg = QtGui.QHBoxLayout()
		layoutH3_wdg = QtGui.QHBoxLayout()
		layoutH4_wdg = QtGui.QHBoxLayout()
		layoutH5_wdg = QtGui.QHBoxLayout()
		## Build Layouts
		self.setLayout(layoutV1_main)
		self.mainGroup.setLayout(layoutV2_grp)
		self.optionGroup.setLayout(layoutV3_grp)
		layoutV2_grp.addLayout(layoutH1_wdg)
		layoutV2_grp.addLayout(layoutH2_wdg)
		layoutV3_grp.addLayout(layoutH3_wdg)
		layoutV3_grp.addLayout(layoutH4_wdg)
		layoutV3_grp.addLayout(layoutH5_wdg)
	#--# Export List TreeWidget
		self.exportList = QtGui.QTreeWidget()
		self.exportList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.exportList.setSortingEnabled(True)
		self.exportList.setAlternatingRowColors(True)
	#--# Create Widgets
		self.addBtn = QtGui.QToolButton(self)
		self.removeBtn = QtGui.QToolButton(self)
		self.clearBtn = QtGui.QToolButton(self)
		self.browseBtn = QtGui.QPushButton('Browse')
		self.exportBtn = QtGui.QPushButton('Export')
		self.formatCombo = QtGui.QComboBox()
		self.exportLabel = QtGui.QLabel('Path: ')
		self.formatLabel = QtGui.QLabel('Format: ')
		self.templateLabel = QtGui.QLabel('Template: ')
		self.templateLn = QtGui.QLineEdit(defaultTemplate)
		self.exportLn = QtGui.QLineEdit()
		## Set Icons
		self.addBtn.setIcon(QtGui.QIcon('%s/Plus.png' % icon_path))
		self.removeBtn.setIcon(QtGui.QIcon('%s/Minus.png' % icon_path))
		self.clearBtn.setIcon(QtGui.QIcon('%s/Quit.png' % icon_path))
	#--# Populate Layouts
		layoutH1_wdg.addWidget(self.exportList)
		layoutH2_wdg.addWidget(self.addBtn)
		layoutH2_wdg.addWidget(self.removeBtn)
		layoutH2_wdg.addWidget(self.clearBtn)
		layoutH2_wdg.addStretch()
		layoutH3_wdg.addWidget(self.exportLabel)
		layoutH3_wdg.addWidget(self.exportLn)
		layoutH3_wdg.addWidget(self.browseBtn)
		layoutH4_wdg.addWidget(self.templateLabel)
		layoutH4_wdg.addWidget(self.templateLn)
		layoutH4_wdg.addWidget(self.formatLabel)
		layoutH4_wdg.addWidget(self.formatCombo)
		layoutH5_wdg.addWidget(self.exportBtn)
		## Final 
		layoutV1_main.addWidget(self.mainGroup)
		layoutV1_main.addWidget(self.optionGroup)
	#--# StyleSheets
		self.setStyleSheet("\
		QTreeWidget { alternate-background-color: rgb(100, 100, 100); } \
		")
	#--# Keyboard shortcuts
		self.deleteKey = QtGui.QShortcut(QtGui.QKeySequence('Delete'), self)
	#--# Connections
		self.addBtn.connect("clicked()", self.addUDIM)
		self.removeBtn.connect("clicked()", lambda: self.manageTree(remove=True))
		self.clearBtn.connect("clicked()", self.clear)
		self.browseBtn.connect("clicked()", self.getExportPath)
		self.exportBtn.connect("clicked()", self.export)
		self.deleteKey.connect("activated()", lambda: self.manageTree(remove=True))
		self.exportList.connect("itemDoubleClicked (QTreeWidgetItem *,int)", lambda: self.manageTree(pick=True))
	#--# Init
		self.init()
		self.setHeader()
		
	def init(self):
		self.formatCombo.addItems(imgFormats)
		self.formatCombo.setCurrentIndex(self.formatCombo.findText(defaultFormat, 0))
		
	def setHeader(self):
		'''Configures header'''
		headerTitles = ['Name', 'Count', 'Depth', 'Size']
		self.headerCount = len(headerTitles)
		self.exportList.setColumnCount(self.headerCount)
		self.exportList.setHeaderLabels(headerTitles)
		self.exportList.setColumnWidth(1, 50)
		trickedout = self.exportList.headerItem()
		trickedout.setTextAlignment(1, 0x0004)
		trickedout.setTextAlignment(2, 0x0004)
		self.resize()
	
	def resize(self):
		'''Resizes tree columns'''
		for column in range(self.exportList.columnCount()):
			self.exportList.resizeColumnToContents(column)
	
	def addObject(self):
		'''Adds Object Items'''
		geo = sceneData('geo')
		geo_items = []
		## Check for existing
		try:
			objectItem = self.exportList.findItems(geo, 0, 0)[0]
			return objectItem
		## Create and Build Object items
		except:
			objectItem = QtGui.QTreeWidgetItem([geo, '', '', ''])
			objectItem.setIcon(0, QtGui.QIcon('%s/Objects.png' % icon_path))
			objectItem.setData(0, 32, 'OBJECT')
			geo_items.append(objectItem)
			self.exportList.insertTopLevelItems(0, geo_items)
			objectItem.setExpanded(True)
			return objectItem
	
	def addChannel(self):
		'''Adds Channel Items'''
		parent = self.addObject()
		resolution = '%sk' % str(sceneData('res'))[0]
		bitDepth = '%sbit' % sceneData('depth')
		channel = sceneData('chan')
		chan_items = []
		## Check for existing
		try:
			for index in range(parent.childCount()):
				child = parent.child(index)
				if child.text(0) == channel:
					chanItem = child
					return chanItem
		except:
			pass
		
		## Create and Build Channel items
		chanItem = QtGui.QTreeWidgetItem([channel, '', bitDepth, resolution])
		chanItem.setTextAlignment(1, 0x0004)
		chanItem.setTextAlignment(2, 0x0004)
		chanItem.setIcon(0, QtGui.QIcon('%s/Channel.png' % icon_path))
		chanItem.setData(0, 32, 'CHANNEL')
		chan_items.append(chanItem)
		parent.insertChildren(0, chan_items)
		return chanItem
	
	def addUDIM(self):
		'''Adds UDIM to list. Note: chain trigger, this function builds everything,
		Nothing will be built if no UDIM selected.
		'''
		selected_udim = sceneData('udim')
		## Exit if no UDIM selected
		if not selected_udim:
			return
		
		parent = self.addChannel()
		exists_udim = []
		add_udim = []
		udim_items = []
		
		## Check for existing
		try:
			for index in range(parent.childCount()):
				child = parent.child(index)
				exists_udim.append(child.text(0))
			for patch in selected_udim:
				if patch not in exists_udim:
					add_udim.append(patch)
		except:
			pass
		
		## Create and Build UDIM items
		for patch in add_udim:
			udimItem = QtGui.QTreeWidgetItem([patch, '', '', ''])
			udimItem.setIcon(0, QtGui.QIcon('%s/Plus.png' % icon_path))
			udimItem.setData(0, 32, 'UDIM')
			udim_items.append(udimItem)
		parent.insertChildren(0, udim_items)
		
		self.udimCount()
		
		## Resize
		self.resize()
	
	def udimCount(self):
		for index in range(self.exportList.topLevelItemCount):
			objectItem = self.exportList.topLevelItem(index)
			
			for index in range(objectItem.childCount()):
				chanItem = objectItem.child(index)
				chanItem.setText(1, chanItem.childCount())
	
	def clear(self):
		'''Clears entire tree'''
		## Clear & Resize
		self.exportList.clear()
		self.resize()
	
	def getExportPath(self):
		'''Define export path'''
		exportDirDialog = ExportDialog()
		if exportDirDialog.exec_():
			browsedExportPath = exportDirDialog.directory().path()
			self.exportLn.setText(browsedExportPath)
	
	def manageTree(self, remove=False, pick=False):
		treeWidget=self.exportList
		selectedItems = treeWidget.selectedItems()
		
		for item in selectedItems:
			#Objects
			if item.data(0,32) == 'OBJECT':
				objectIndex = treeWidget.indexOfTopLevelItem(item)
				objectName = item.text(0)
				if remove:
					treeWidget.takeTopLevelItem(objectIndex)
			#Channels
			elif item.data(0,32) == 'CHANNEL':
				objectItem = item.parent()
				channelIndex = objectItem.indexOfChild(item)
				channelName = item.text(0)
				if remove:
					objectItem.takeChild(channelIndex)
			#UDIMs
			elif item.data(0,32) == 'UDIM':
				objectItem = item.parent().parent()
				objectName = objectItem.text(0)
				channelItem = item.parent()
				udimIndex = channelItem.indexOfChild(item)
				udimName = item.text(0)
				if remove:
					channelItem.takeChild(udimIndex)
				if pick:
					selectPatch(objectName, udimName)
		if remove:
			self.resize()
		
	def getExportDict(self):
		treeWidget=self.exportList
		exportDict = {}
		
		## Object ITEMS
		for objIndex in range(treeWidget.topLevelItemCount):
			object = treeWidget.topLevelItem(objIndex)
			objectName = object.text(0)
			channelDict = {}
			##Channel ITEMS
			for chanIndex in range(object.childCount()):
				channel = object.child(chanIndex)
				channelName = channel.text(0)
				udim_list = []
				## UDIM ITEMS
				for udimIndex in range(channel.childCount()):
					udim = channel.child(udimIndex)
					udimName = udim.text(0)
					udim_list.append(udimName)
				
				## Channel Dict
				channelDict[channelName] = udim_list
				
			## Object Dict
			exportDict[objectName] = channelDict
		
		return exportDict

	def export(self):
		#Export
		objDict = self.getExportDict()
		template = self.templateLn.text
		export_path = self.exportLn.text
		export_format = self.formatCombo.currentText
		exportMaps(objDict, export_path, export_format, template)


##------------------------------------------------------------------------------------------------------------------------------
## Mari UI Init ##
##------------------------------------------------------------------------------------------------------------------------------
exportUI =  ExportQtGui()
#exportUI.setDisabled(True)
mari.palettes.create('bnExporter', exportUI)
exportPalette = mari.actions.find('/Mari/Palettes/bnExporter')
exportPalette.setIconPath('%s/ExportFile.png' % icon_path)

def toggleUI():
	if mari.projects.current():
		exportUI.setEnabled(True)
	elif not mari.projects.current():
		exportUI.setDisabled(True)

## Connections
mari.utils.connect(mari.projects.openedProject, toggleUI)
mari.utils.connect(mari.projects.projectClosed, toggleUI)