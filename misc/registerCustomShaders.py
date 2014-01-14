import mari
import os
import xml.etree.ElementTree as ET

mari_version = '%d.%d' % (mari.app.version().major(), mari.app.version().minor())

base_path = os.path.dirname(__file__)
default_shader_path = '%s/NodeLibrary' % base_path
default_lib_path = '%s/FunctionLibrary' % base_path

def loadLibraries():
    '''Loads custom shader libraries'''

    libDict = {}
    for path, subdirs, files in os.walk(default_lib_path):
        for name in files:
            libDict[name]=path

    for lib in libDict:
        full_lib_path = libDict[lib]
        libPath = '%s/%s' % (full_lib_path, lib)
        libName = lib.split(".")[0]

        try:
            if lib.endswith('glslh'):
                mari.gl_render.registerCustomHeaderFile(libName, libPath)
                print 'Registered Library: %s' % libName
            elif lib.endswith('glslc'):
                mari.gl_render.registerCustomCodeFile(libName, libPath)
                print 'Registered Library: %s' % libName
        except Exception as exc:
                print 'Error Registering Library: %s : %s' % (libName, str(exc))

def loadShaders():
    '''Loads custom shaders'''

    #Find Shaders
    shaderDict = {}
    for path, subdirs, files in os.walk(default_shader_path):
        for name in files:
            shaderDict[name]=path

    #Determine attributes
    for shader in shaderDict:
        full_shader_path = shaderDict[shader]
        xml = ET.parse('%s/%s' % (full_shader_path,shader))
        root = xml.getroot()

        #Shader info
        shaderPath= full_shader_path.replace(default_shader_path, "")
        shaderPath = shaderPath.replace("\\", "/")
        shaderType = shaderPath.split("/")[1]
        shaderName = root.find('DefaultName').text
        #Register info
        nodeName = "/%s/Custom/%s" % (shaderType, shaderName)
        nodePath = "%s/%s" % (full_shader_path, shader)

        #Sub Category
        try:
            shaderSub = shaderPath.split("/")[2]
            shaderLocation = '/%s/Custom/%s/%s' % (shaderType, shaderSub, shaderName)
        except:
            shaderLocation = '/%s/Custom/%s' % (shaderType, shaderName)
            pass

        try:
            if shaderType == 'Procedural' or shaderType == 'Geometry':
                mari.gl_render.registerCustomProceduralLayerFromXMLFile(shaderLocation, nodePath)
            elif shaderType == 'Adjustment':
                mari.gl_render.registerCustomAdjustmentLayerFromXMLFile('/Custom/%s' % shaderName, nodePath)
            print 'Registered %s Node: %s' % (shaderType, shaderName)
        except Exception as exc:
            print 'Error Registering %s Node : %s : %s' % (shaderType, shaderName, str(exc))

if mari_version == '2.5':
    ##Load All
    print '\nInitializing Shader Libraries.....'
    print '-----------------------------------------'
    loadLibraries()
    print '\nLoading Shaders.....'
    print '-----------------------------------------'
    loadShaders()
