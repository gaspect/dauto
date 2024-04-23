class OutSignal:
    """
    Description:
        This class represents a context manager for disconnecting and reconnecting signal handlers.

    Methods:
    - __init__(self, signal, receiver, sender, dispatch_uid=None):
        Initializes an instance of the OutSignal class.

        Parameters:
        - signal: The signal object to be disconnected and reconnected.
        - receiver: The receiver object whose signal handler will be disconnected and reconnected.
        - sender: The sender object that will trigger the signal handler.
        - dispatch_uid: An optional unique identifier for the signal handler. If provided, only the signal handler with
          matching dispatch_uid will be disconnected and reconnected.

    - __enter__(self):
        Disconnects the signal handler by calling signal.disconnect() with the specified receiver, sender, and dispatch_uid.
        This method is automatically called when the class is used with the 'with' statement.

    - __exit__(self, type, value, traceback):
        Reconnects the signal handler by calling signal.connect() with the specified receiver, sender, and dispatch_uid.
        This method is automatically called when the exit from the 'with' statement is reached or an exception is raised.
    Example:
        from django.dispatch import Signal

        # The signal we will be disconnecting and reconnecting
        my_signal = Signal(providing_args=["message"])

        # The receiver function for my_signal
        def my_receiver(sender, **kwargs):
            print("Received signal from ", sender)
            print("Message: ", kwargs['message'])

        # The sender function for my_signal
        def my_sender():
            my_signal.send(sender=my_sender, message="Hello, world!")

        # We connect the receiver to the signal initially
        my_signal.connect(receiver=my_receiver, sender=my_sender, weak=False)

        # Now, we can use the OutSignal class to temporarily disconnect my_receiver from my_signal
        with OutSignal(my_signal, my_receiver, my_sender) as out_signal:
            # In this block, my_receiver is disconnected from my_signal
            # So, if we send a signal, it won't be received
            print("In the 'with' block:")
            my_sender()
        # Now, we're out of the 'with' block, so my_receiver has been reconnected to my_signal
        # If we send a signal, it will be received
        print("Out of the 'with' block:")
        my_sender()
    """
    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid
        )

    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid
        )
