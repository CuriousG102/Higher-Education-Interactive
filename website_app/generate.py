import infoToJSON
import io

def generate():
	infoToJSON.produceBillJSONFiles('bills')
	enhanceJSON('enhancedSenate.json', 'senate.json', 'upper')
	enhanceJSON('enhancedHouse.json', 'house.json', 'lower')

def enhanceJSON(enhancedName, sourceName, chamber):
	with io.open(enhancedName, mode='w', encoding='utf8') as f:
		with io.open(sourceName, mode='r', encoding='utf8') as g:
			enhancedString = infoToJSON.produceEnhancedDistrictJSONString(g.read(), chamber)
		f.write(enhancedString)

if __name__ == '__main__': generate()