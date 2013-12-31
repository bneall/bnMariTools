##  bnImageResize Tool
############################################################
## Tool for resizing per patch images.
## -------------------
## Install: Copy this file to your user Mari/Scripts folder.
## (Create a Scripts directory if there is none)
## Versions supported: 2.x
## -------------------
## Copyright Ben Neall 2013-2014
## Contact: bneall@gmail.com
############################################################

#import PythonQt.QtCore as QtCore

icon_path = mari.resources.path('ICONS')

def resizeImage(res):
	"""This function resizes the targeted imageSet"""
	#img_size = QtCore.QSize(256, 256)
	img_size = res

	mariObj = mari.geo.current()
	mariChan = mariObj.currentChannel()
	mariLayer = mariChan.currentLayer()
	udimList = mariObj.selectedPatches()
		
	try:
		layerImageSet = mariLayer.imageSet()
		mari.history.startMacro('Image Resize')
		##resize paint layer
		for patch in udimList:
			image = mariObj.patchImage(patch, layerImageSet)
			image.resize(img_size)
			print "Resized %s(%s) to %sx%s" % (mariLayer.name(), patch.udim(), res, res)
		mari.history.stopMacro()
	except:
		mari.utils.message('Error. Make sure layer is paintable')

## UI
resOptions = [256, 512, 1024, 2048, 4096, 8192]
for item in resOptions:
	resizeITEM = mari.actions.create('%s x %s' % (str(item),str(item)), 'resizeImage(%d)' % item)
	resizeITEM.setIconPath('%s/TransformScale.png' % icon_path)
	## Recursive menu creation
	mari.menus.addAction(resizeITEM, 'MainWindow/P&atches/Resize Selected Image')