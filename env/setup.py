#Get an adaptor from stdin, run the setup method, print the result
#Write adaptor into the config file
import sys, importlib
import configParser
def main(adaptor):
	adapt = importlib.import_module(adaptor)

	a = getattr(adapt,adaptor)()

	Config = ConfigParser.ConfigParser()
	Config.read(os.path.join(os.path.split(os.path.abspath(__file__))[0],'config.ini'))
	if (not 'Adaptor' in Config.sections()):
		

	print a.setup()


if __name__ == '__main__':
	main(sys.argv[1])