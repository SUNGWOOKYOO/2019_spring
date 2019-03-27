#!/usr/bin/env python

"""
Filter top-50 follower countings
"""

import struct

from pydoop.mapreduce.pipes import run_task, Factory
from pydoop.mapreduce.api import Mapper, Reducer

class FilterMapper(Mapper):

    def map(self, context):
        # Implements your codes
	context.emit(context.key,context.value)
	#	pass

class FilterReducer(Reducer):

    def reduce(self, context):
        # Implements your codes
	context.emit("","")
	
	#	pass

if __name__ == "__main__":
    factory = Factory(FilterMapper, FilterReducer)
    run_task(factory)
