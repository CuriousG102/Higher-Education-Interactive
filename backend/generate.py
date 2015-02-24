import settings
import io
import os
import shutil

import infoToJSON
from downloadAssets import makeRepImagesLocal

def generate():
	infoToJSON.produceBillJSONFiles(os.path.join(settings.web_files_path, 'bills'))
	enhanceJSON(os.path.join(settings.web_files_path, 'enhancedSenate.json'), 'senate.json', 'upper')
	enhanceJSON(os.path.join(settings.web_files_path, 'enhancedHouse.json'), 'house.json', 'lower')
	makeRepImagesLocal(os.path.join(settings.web_files_path, 'images/'))
	shutil.rmtree(settings.copy_web_path)
	shutil.copytree(settings.web_files_path, settings.copy_web_path)

def enhanceJSON(enhancedName, sourceName, chamber):
	with io.open(enhancedName, mode='w', encoding='utf8') as f:
		with io.open(sourceName, mode='r', encoding='utf8') as g:
			enhancedString = infoToJSON.produceEnhancedDistrictJSONString(g.read(), chamber)
		f.write(enhancedString)

if __name__ == '__main__': generate()