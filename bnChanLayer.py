##  bnChanLayer Tool
############################################################
## Tool for creating channel layers.
## -------------------
## Install: Copy this file to your user Mari/Scripts folder.
## (Create a Scripts directory if there is none)
## Versions supported: 2.x
## -------------------
## Copyright Ben Neall 2013-2014
## Contact: bneall@gmail.com
############################################################

import PythonQt.QtGui as Gui

icon_path = mari.resources.path('ICONS')

def makeCL(sourceChannel, mode):
	currentChannel = mari.geo.current().currentChannel()
	currentLayer = currentChannel.currentLayer()
	layerName = currentLayer.name()
	channelLayerName = sourceChannel.name()
	
	if mode == 'layer':
		currentChannel.createChannelLayer(channelLayerName, sourceChannel, None, 16)	
	else:
		mari.history.startMacro('Create group channel mask')
		
		if mode == 'maskgroup':
			## New Group Layer
			layerGroupName = '%s_grp' % layerName
			groupLayer = currentChannel.groupLayers([currentLayer], None, None, 16)
			groupLayer.setName(layerGroupName)
			layerStack = groupLayer
		elif mode == 'mask':
			layerStack = currentLayer
		
		## New Layer Mask Stack
		layerMaskStack = layerStack.makeMaskStack()
		layerMaskStack.removeLayers(layerMaskStack.layerList())
		
		## Create Mask Channel Layer
		maskChannelLayerName = '%s(Shared Channel)' % channelLayerName
		layerMaskStack.createChannelLayer(maskChannelLayerName, sourceChannel)
		
		mari.history.stopMacro()

class CLCreate(Gui.QDialog):
	'''GUI to select channel to make into a channel-layer in the current channel
	modes: 'groupmask', 'mask', 'layer'
	'''
	def __init__(self, mode):
		super(CLCreate, self).__init__()
		## Dialog Settings
		self.setFixedSize(300, 100)
		self.setWindowTitle('Select Channel')
		## Vars
		self.mode = mode
		## Layouts
		layoutV1 = Gui.QVBoxLayout()
		layoutH1 = Gui.QHBoxLayout()
		self.setLayout(layoutV1)
		## Widgets
		self.chanCombo = Gui.QComboBox()
		self.okBtn = Gui.QPushButton('Ok')
		self.cancelBtn = Gui.QPushButton('Cancel')
		## Populate 
		layoutV1.addWidget(self.chanCombo)
		layoutV1.addLayout(layoutH1)
		layoutH1.addWidget(self.cancelBtn)
		layoutH1.addWidget(self.okBtn)
		## Connections
		self.okBtn.connect("clicked()", self.runCreate)
		self.cancelBtn.connect("clicked()", self.close)
		## Init
		self.init()
	
	def init(self):
		currentChannel = mari.geo.current().currentChannel()
		channelList = mari.geo.current().channelList()
		for channel in channelList:
			if channel is not currentChannel:
				self.chanCombo.addItem(channel.name(), channel)
	
	def selectedChannel(self):
		return self.chanCombo.itemData(self.chanCombo.currentIndex, 32)
	
	def runCreate(self):
		sourceChannel = self.selectedChannel()
		makeCL(sourceChannel, self.mode)
		self.close()

## Channel Layer ACTIONS
chanLayerITEM = mari.actions.create('Add Channel Layer', 'CLCreate("layer").exec_()')
chanLayerITEM.setIconPath('%s/DuplicateChannel.png' % icon_path)
chanLayerMaskITEM = mari.actions.create('Add Channel Mask', 'CLCreate("mask").exec_()')
chanLayerMaskITEM.setIconPath('%s/AddChannel.png' % icon_path)
chanLayerGrpMaskITEM = mari.actions.create('Add Channel Mask (Group)', 'CLCreate("maskgroup").exec_()')
chanLayerGrpMaskITEM.setIconPath('%s/NewFolder.png' % icon_path)
chanLayerITEM.setEnabled(False)
chanLayerMaskITEM.setEnabled(False)
chanLayerGrpMaskITEM.setEnabled(False)

mari.menus.addAction(chanLayerITEM, 'MainWindow/&Layers', 'Add Adjustment Layer')
mari.menus.addAction(chanLayerMaskITEM, 'MainWindow/&Layers/Layer Mask/Add Mask')
mari.menus.addAction(chanLayerGrpMaskITEM, 'MainWindow/&Layers/Layer Mask/Add Mask')

## Mari UI Init ##
def toggleUI():
	if mari.projects.current():
		chanLayerITEM.setEnabled(True)
		chanLayerMaskITEM.setEnabled(True)
		chanLayerGrpMaskITEM.setEnabled(True)
	elif not mari.projects.current():
		chanLayerITEM.setEnabled(False)
		chanLayerMaskITEM.setEnabled(False)
		chanLayerGrpMaskITEM.setEnabled(False)

## Connections
mari.utils.connect(mari.projects.openedProject, toggleUI)
mari.utils.connect(mari.projects.projectClosed, toggleUI)