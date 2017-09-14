#Get an adaptor from stdin, run the setup method, print the result
import sys, importlib
def main(adaptor):
	adapt = importlib.import_module(adaptor)

	a = getattr(adapt,adaptor)()

	print a.setup()


if __name__ == '__main__':
	main(sys.argv[1])