from __future__ import absolute_import
import numpy as np


class Accumulators(object):

    _accumulator_library = {}

    def __init__(self):
        self.accumulator_library = {}
        for key, value in Accumulators._accumulator_library.items():
            self.accumulator_library[key] = value()

    @staticmethod
    def register(name, accumulator):
        Accumulators._accumulator_library[name] = accumulator

    def keys(self):
        return self.accumulator_library.keys()

    def add(self, x):
        for accumulator in self.accumulator_library.values():
            accumulator.add(x)

    def compute(self, name):
        return self.accumulator_library[name].compute(self)

    def __getattr__(self, name):
        return self.compute(name)

    @staticmethod
    def register_decorator(name):
        def wrap(cls):
            Accumulators.register(name, cls)
            return cls
        return wrap


@Accumulators.register_decorator("min")
class Min(object):

    def __init__(self):
        self.min = None

    def add(self, x):
        self.min = x if self.min is None else np.min([self.min, x], axis=0)

    def compute(self, host):
        return self.min


@Accumulators.register_decorator("max")
class Max(object):

    def __init__(self):
        self.max = None

    def add(self, x):
        self.max = x if self.max is None else np.max([self.max, x], axis=0)

    def compute(self, host):
        return self.max


@Accumulators.register_decorator("count")
class Count(object):

    def __init__(self):
        self.count = 0

    def add(self, x):
        self.count += 1

    def compute(self, host):
        return self.count


@Accumulators.register_decorator("sum")
class Sum(object):

    def __init__(self):
        self.sum = 0

    def add(self, x):
        self.sum += x

    def compute(self, host):
        return self.sum


@Accumulators.register_decorator("mean")
class Mean(object):

    def __init__(self):
        pass

    def add(self, x):
        pass

    def compute(self, host):
        if host.compute('count') == 0:
            return 0
        else:
            return host.compute('sum') / host.compute('count')


@Accumulators.register_decorator("var")
class Var(object):

    def __init__(self):
        self.squared_sum = 0

    def add(self, x):
        self.squared_sum += x ** 2

    def compute(self, host):
        return self.squared_sum / host.compute('count') - host.compute('mean') ** 2


@Accumulators.register_decorator("std")
class Std(object):

    def __init__(self):
        pass

    def add(self, x):
        pass

    def compute(self, host):
        return np.sqrt(host.compute('var'))
