"""
	The blur3d.scenes package creates an abstract wrapper from a 3d system
	to use when dealing with scenes.  If you need to debug why a software module 
	is failing to load, set _useDebug, and _modName.
"""

import glob
import os
import sys

import blurdev as _blurdev
# If you need to test why a package is failing to import set this to true
_useDebug = _blurdev.debug.debugLevel() == _blurdev.debug.DebugLevel.High
# specify the module you wish to check. This way it will not report the fail to load softimage if you are in max, as this is a expected failure
_modName = _blurdev.core.objectName()

from classes import FCurve
from classes import Exceptions
from classes import ValueRange
from classes import FrameRange
from classes import FileSequence
from classes import Timecode
from classes import Clipboard
from classes import FlipBook
from classes import Dispatch as _Dispatch

# Global Dispatch object.  This is the main entry point for connecting to events and signals generated by the 3D environment.
dispatch = _Dispatch()

def _methodNames():
	filenames = glob.glob(os.path.split(__file__)[0] + '/*/__init__.py')
	ret = []
	for filename in filenames:
		modname = os.path.normpath(filename).split(os.path.sep)[-2]
		if (modname != 'abstract'):
			ret.append(os.path.normpath(filename).split(os.path.sep)[-2])
	return ret

def packageName(modname):
	return 'blur3d.api.%s' % modname

def init():
	# import any overrides to the abstract symbols
	for modname in _methodNames():
		pckg = packageName(modname)

		# try to import the overrides
		if _useDebug and (not _modName or modname == _modName):
			__import__(pckg)
		else:
			try:
				__import__(pckg)
			except ImportError:
				continue

		mod = sys.modules[pckg]
		if _useDebug and (not _modName or modname == _modName):
			mod.init()
		else:
			try:
				mod.init()
				break
			except:
				continue

	# import the abstract api for default implementations of api
	import abstract
	abstract.init()

def external(appName):
	appName = appName.lower()
	# classes should not have a external implementation
	if appName == 'classes':
		raise KeyError('classes does not have a external implementation.')
	import blur3d.api
	try:
		__import__(packageName(appName))
		return getattr(getattr(getattr(blur3d.api, appName), 'external'), 'External')
	except AttributeError:
		return blur3d.api.abstract.external.External

def registerSymbol(name, value, ifNotFound=False):
	"""
		Used by the *adaptors* to register their own classes and functions as
		part of the blur3d.api.  
	"""
	# initialize a value in the dictionary
	import blur3d.api
	if ifNotFound and name in blur3d.api.__dict__:
		return

	blur3d.api.__dict__[name] = value
