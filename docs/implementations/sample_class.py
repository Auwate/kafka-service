"""
A sample class for usage with the json encoder 
"""

import datetime
from typing import Dict, List


class SampleClass:
    """
    A parent class that shows a nested, complex class structure for use in serialization
    """

    def __init__(self, dep1 = "test", dep2 = 2412512):
        self._dependencies: Dict[str, object] = {
            "dep1": dep1,
            "dep2": dep2
        }
        self._id = 104890124

    def __repr__(self):
        """
        Override the __repr__ function
        """
        return f"SampleClass(dependencies={self._dependencies!r}, id={self._id!r})"

    def as_dict(self):
        """
        Simple as_dict method
        """
        return {"SampleClass": {"dependencies": self._dependencies, "id": self._id}}


class DependencyClass1(SampleClass):
    """
    A sample dependency class that contains some standard fields
    """

    def __init__(self):
        super().__init__("Dependency1", 12904812)
        self._target: str = "Something"
        self._time: datetime.datetime = datetime.datetime.now()

    def __repr__(self):
        """
        This dependency class overrides the __repr__ function
        """
        return f"DependencyClass1(target={self._target!r}, time={self._time!r}, dependencies={self._dependencies}, id={self._id})"


class DependencyClass2(SampleClass):
    """
    Another dependency class, but this one is compositely made from DependencyClass1.
    """

    def __init__(self):
        self._members: List[DependencyClass1] = [
            DependencyClass1(),
            DependencyClass1(),
            DependencyClass1(),
        ]
        super().__init__({"dep1": 20, "dep2": 30}, True)

    def __repr__(self):
        return f"DependencyClass2(members={self._members!r}, dependencies={self._dependencies!r}, id={self._id!r})"

    def as_dict(self):
        """
        Implements a method to return the function as a dict
        """
        return {"DependencyClass2": {"members": self._members}}
