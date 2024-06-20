# # Signals

# Signals and circular calls sucks and when we use signals this happen frequently then we made a method
# for execute code  without a signal. This work with a python contex manager used as a pun so:

# ```python
# with OutSignal(signal,sender, receiver):
#     <code>
# ```

# Will execute the `code` section with the signal unplugged, avoiding circular imports and nested signal calls

class OutSignal:
    """
    This class represents a context manager for disconnecting and reconnecting signal handlers.
    """

    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        """
        Initializes an instance of the OutSignal class.

        Parameters:
        - signal: The signal object to be disconnected and reconnected.
        - receiver: The receiver object whose signal handler will be disconnected and reconnected.
        - sender: The sender object that will trigger the signal handler.
        - dispatch_uid: An optional unique identifier for the signal handler. If provided, only the signal handler with
          matching dispatch_uid will be disconnected and reconnected.
        """
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

    # noinspection PyShadowingBuiltins
    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid
        )
