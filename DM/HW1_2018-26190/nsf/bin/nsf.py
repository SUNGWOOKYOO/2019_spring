#!/usr/bin/env python

"""
Impelements non-symmetric fellow-shop
Input : directed graph
    e.g.) "3   4" indicates that person 3 has 4 followers.
Output : (node, node)
    e.g.) "1 2" node 1 => node 2 is non-symmetric
"""
# DOCS_INCLUDE_START
import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pipes


class Mapper(api.Mapper):

    def map(self, context):
        # implements your code
        #context.emit(context.value, 1)
        x = context.value.split()
        if(x[0]<x[1]):
            context.emit(context.value, 1)
        else:
            context.emit(x[1]+"\t"+x[0], 1)

class Reducer(api.Reducer):

    def reduce(self, context):
        # implements your code
        s = sum(context.values)
        if(s == 1):
               context.emit(context.key, "")

FACTORY = pipes.Factory(Mapper, reducer_class=Reducer)


def main():
    pipes.run_task(FACTORY)


if __name__ == "__main__":
    main()
