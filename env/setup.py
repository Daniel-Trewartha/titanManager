#Get an adaptor from stdin, run the setup method, print the result
#Write adaptor into the config file
import os, sys
import ConfigParser
def main(adaptor):
	adapt =  __import__(adaptor,fromlist=[''])

	a = getattr(adapt,adaptor)()

	config = ConfigParser.ConfigParser()
	configFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],'config.ini')
	config.read(configFile)
	if (not 'Adaptor' in config.sections()):
		config.add_section("Adaptor")
		config.set("Adaptor","adaptor",adaptor)
		with open(configFile,'wb') as f:
			config.write(f)

	print a.setup()


if __name__ == '__main__':
	main(sys.argv[1])
