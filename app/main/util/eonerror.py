class EonError(Exception):
    """
    Custom Exception class

    methods of service classes raise exceptions which 
    contain the http code for the controllers to return
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.code = args[1]
        else:
            self.message = None
            self.code = 500

    def __str__(self):
        if self.message:
            return 'message: {0} '.format(self.message)
        else:
            return 'EonError has been raised'