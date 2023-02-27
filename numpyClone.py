class NumpyClone():
    def __init__(self) -> None:
        pass
    @staticmethod
    def min(array):
        current_min = 0
        for el in array:
            if el < current_min:
                current_min = el
        return current_min
