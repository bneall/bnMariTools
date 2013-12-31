##  bnSelectionMask Tool
############################################################
## Tool for creating mask from active patch selection.
## -------------------
## Install: Copy this file to your user Mari/Scripts folder.
## (Create a Scripts directory if there is none)
## Versions supported: 2.x
## -------------------
## Copyright Ben Neall 2013-2014
## Contact: bneall@gmail.com
############################################################

icon_path = mari.resources.path('ICONS')

def selectionMask(invert):
	currentObj = mari.geo.current()
	currentChan = currentObj.currentChannel()
	currentLayer = currentChan.currentLayer()
	selectedPatches = currentObj.selectedPatches()
	
	newMaskImageSet = currentLayer.makeMask()
	mari.history.startMacro('Create custom mask')
	for image in newMaskImageSet.imageList():
		if invert == False:
			image.fill(mari.Color(0.0, 0.0, 0.0, 1.0))
		else:
			image.fill(mari.Color(1.0, 1.0, 1.0, 1.0))
	
	for patch in selectedPatches:
		selectedImage = currentObj.patchImage(patch, newMaskImageSet)
		if invert == False:
			selectedImage.fill(mari.Color(1.0, 1.0, 1.0, 1.0))
		else:
			selectedImage.fill(mari.Color(0.0, 0.0, 0.0, 1.0))
	mari.history.stopMacro()

## Layer mask from selection ACTION
selectMaskITEM = mari.actions.create('From Selection', 'selectionMask(invert=False)')
selectMaskITEM.setIconPath('%s/SelectAll.png' % icon_path)
selectMaskInvertITEM = mari.actions.create('From Selection(Invert)', 'selectionMask(invert=True)')
selectMaskInvertITEM.setIconPath('%s/SelectInvert.png' % icon_path)

mari.menus.addAction(selectMaskITEM, 'MainWindow/&Layers/Layer Mask/Add Mask')
mari.menus.addAction(selectMaskInvertITEM, 'MainWindow/&Layers/Layer Mask/Add Mask')