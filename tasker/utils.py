import math


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def d_sigmoid(x: float) -> float:
    return sigmoid(x) * (1 + sigmoid(x))
