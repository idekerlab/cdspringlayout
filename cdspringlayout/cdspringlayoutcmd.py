#!/usr/bin/env python

import os
import sys
import argparse
import traceback
import json
from contextlib import redirect_stdout

import ndex2
import networkx


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


def _parse_arguments(desc, args):
    """
    Parses command line arguments
    :param desc:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('input',
                        help='CX file')
    parser.add_argument('--k', type=float, default=None,
                        help='Optimal distance between nodes. '
                             'If None the distance is set to '
                             '1/sqrt(n) where n is the number '
                             'of nodes. Increase this value '
                             'to move nodes farther apart')
    parser.add_argument('--iterations', type=int, default=50,
                        help='Maximum number of iterations taken')
    parser.add_argument('--weight', default='weight',
                        help='The edge attribute that holds the '
                             'numerical value used for the edge weight. '
                             'Larger means a stronger attractive force. '
                             'If None, then all edge weights are 1.')
    parser.add_argument('--scale', type=float, default='500.0',
                        help='Scale factor for positions.')
    parser.add_argument('--threshold', type=float, default=0.0001,
                        help='Threshold for relative error in node '
                             'position changes. The iteration stops if '
                             'the error is below this threshold.')
    return parser.parse_args(args)


def run_layout(theargs, out_stream=sys.stdout,
               err_stream=sys.stderr):
    """
    Runs networkx Spring layout

    :param theargs: Holds attributes from argparse
    :type theargs: `:py:class:`argparse.Namespace`
    :param out_stream: stream for standard output
    :type out_stream: file like object
    :param err_stream: stream for standard error output
    :type err_stream: file like object
    :return: 0 upon success otherwise error
    :rtype: int
    """

    if theargs.input is None or not os.path.isfile(theargs.input):
        err_stream.write(str(theargs.input) + ' is not a file')
        return 3

    if os.path.getsize(theargs.input) == 0:
        err_stream.write(str(theargs.input) + ' is an empty file')
        return 4

    try:
        with redirect_stdout(sys.stderr):
            net = ndex2.create_nice_cx_from_file(theargs.input)
            g = net.to_networkx(mode='default')
            del net
            pos = networkx.spring_layout(g, k=theargs.k,
                                         iterations=theargs.iterations,
                                         threshold=theargs.threshold,
                                         weight=theargs.weight,
                                         scale=theargs.scale)
            new_layout = []
            for node_id, coordinates in pos.items():
                new_layout.append({
                    'node': node_id,
                    'x': coordinates[0],
                    'y': -coordinates[1]  # See note below!!!
                })

            cart_aspect = {ndex2.constants.CARTESIAN_LAYOUT_ASPECT: new_layout}
            # write cartesianLayout aspect to output stream
            json.dump(cart_aspect, out_stream)
        return 0
    except Exception as e:
        err_stream.write(str(e))
        return 5
    finally:
        err_stream.flush()
        out_stream.flush()


def main(args):
    """
    Main entry point for program
    :param args: command line arguments usually :py:const:`sys.argv`
    :return: 0 for success otherwise failure
    :rtype: int
    """
    desc = """
    Runs spring layout on command line, sending cartesianLayout aspect
    to standard out
    """
    theargs = _parse_arguments(desc, args[1:])
    try:
        return run_layout(theargs, sys.stdout, sys.stderr)
    except Exception as e:
        sys.stderr.write('\n\nCaught exception: ' + str(e))
        traceback.print_exc()
        return 2


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
