#!/usr/bin/env python3
#-*- coding:utf-8 -*-
##
## mkplot.py
##
##  Created on: Jan 31, 2014
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

#
#==============================================================================
from __future__ import print_function
import matplotlib
matplotlib.use('pdf')  # for not loading GUI modules

from cactus import Cactus
import getopt
import json
from load import load_data
import os
from scatter import Scatter
import sys


#
#==============================================================================
def parse_options():
    """
        Parses command-line options:
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'a:b:c:df:hj:k:lp:r:t:',
                                   ['title=',
                                    'alpha=',
                                    'backend=',
                                    'config=',
                                    'dry-run',
                                    'filter=',
                                    'font=',
                                    'font-sz=',
                                    'title-sz=',
                                    'axis-label-sz=',
                                    'no-grid',
                                    'help',
                                    'join-key=',
                                    'key=',
                                    'latex',
                                    'lalpha=',
                                    'legend=',
                                    'lloc=',
                                    'lncol=',
                                    'only=',
                                    'plot-type=',
                                    'replace=',
                                    'ratio=',
                                    'ordering=',
                                    'save-to=',
                                    'shape=',
                                    'timeout=',
                                    'tol',
                                    'tlabel=',
                                    'tol-loc=',
                                    'transparent',
                                    'vbs=',
                                    'use_tick_sep',
                                    'xkcd',
                                    'xlabel=',
                                    'xlog',
                                    'xmin=',
                                    'xmax=',
                                    'ylabel=',
                                    'ylog',
                                    'ymin=',
                                    'ymax=',
                                    'markevery=',
                                    'scatter-color='
                                    ])
    except getopt.GetoptError as err:
        sys.stderr.write(str(err).capitalize() + '\n')
        usage()
        sys.exit(1)

    # loading default options
    for opt, arg in opts:
        if opt in ('-c', '--config'):
            def_path = str(arg)
            break
    else:
        def_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'defaults.json')

    with open(def_path, 'r') as fp:
        options = json.load(fp)['settings']
        options['def_path'] = def_path

    options['title'] = ""
    options['tol'] = False
    options['title_sz'] = 20.0
    options['axis_label_sz'] = 12.0
    options['ordering'] = "sorted"
    options['markevery'] = -1
    options['filter'] = False
    options['ratio'] = None
    options['use_tick_sep'] = False
    # parsing command-line options
    for opt, arg in opts:
        if opt == '--title':
            options['title'] = str(arg)
        elif opt in ('-a', '--alpha'):
            options['alpha'] = float(arg)
        elif opt in ('-b', '--backend'):
            options['backend'] = str(arg)
        elif opt in ('-c', '--config'):
            pass  # already processed
        elif opt in ('-d', '--dry-run'):
            options['dry_run'] = True
        elif opt == '--filter':
            options['filter'] = json.loads(str(arg))
        elif opt in ('-f', '--font'):
            options['font'] = str(arg)
        elif opt == '--font-sz':
            options['font_sz'] = float(arg)
        elif opt == '--title-sz':
            options['title_sz'] = float(arg)
        elif opt == '--axis-label-sz':
            options['axis_label_sz'] = float(arg)
        elif opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt == '--no-grid':
            options['no_grid'] = True
        elif opt in ('-j', '--join-key'):
            options['join_key'] = [k.strip() for k in str(arg).split(',')]
        elif opt in ('-k', '--key'):
            options['key'] = str(arg)
        elif opt in ('-l', '--latex'):
            options['usetex'] = True
        elif opt == '--lalpha':
            options['lgd_alpha'] = float(arg)
        elif opt == '--legend':
            options['legend'] = [k.strip() for k in str(arg).split(',')]
        elif opt == '--lloc':
            options['lgd_loc'] = str(arg)
        elif opt == '--lncol':
            options['lgd_ncol'] = int(arg)
        elif opt == '--only':
            options['only'] = [t.strip() for t in str(arg).split(',')]
        elif opt in ('-p', '--plot-type'):
            options['plot_type'] = str(arg)
        elif opt in ('-r', '--replace'):
            options['repls'] = json.loads(str(arg))
        elif opt == '--ratio':
            options['ratio'] = json.loads(str(arg))
        elif opt == '--ordering':
            options['ordering'] = str(arg)
        elif opt == '--save-to':
            options['save_to'] = str(arg)
        elif opt == '--shape':
            options['shape'] = str(arg)
        elif opt in ('-t', '--timeout'):
            options['timeout'] = float(arg)
        elif opt == '--tol':
            options['tol'] = True
        elif opt == '--tlabel':
            options['t_label'] = str(arg)
        elif opt == '--tol-loc':
            options['tlb_loc'] = str(arg)
        elif opt == '--transparent':
            options['transparent'] = True
        elif opt == '--vbs':
            options['vbs'] = json.loads(str(arg))
        elif opt == '--use_tick_sep':
            options['use_tick_sep'] = True
        elif opt == '--xkcd':
            options['xkcd'] = True
        elif opt == '--xlabel':
            options['x_label'] = str(arg)
        elif opt == '--xlog':
            options['x_log'] = True
        elif opt == '--xmin':
            options['x_min'] = float(arg)
        elif opt == '--xmax':
            options['x_max'] = float(arg)
        elif opt == '--ylabel':
            options['y_label'] = str(arg)
        elif opt == '--ylog':
            options['y_log'] = True
        elif opt == '--ymin':
            options['y_min'] = float(arg)
        elif opt == '--ymax':
            options['y_max'] = float(arg)
        elif opt == '--markevery':
            options['markevery'] = int(arg)
        elif opt == '--scatter-color':
            options['scatter-color'] = str(arg)
        else:
            assert False, 'Unhandled option: {0} {1}'.format(opt, arg)

    return options, args


#
#==============================================================================
def usage():
    """
        Prints usage message.
    """

    print('Usage:', os.path.basename(sys.argv[0]), ' [options] stat-files')
    print('Options:')
    print('        --title=<string>                Title to diagram (default="")')
    print('        -a, --alpha=<float>             Alpha value (only for scatter plots)')
    print('                                        Available values: [0 .. 1] (default = 0.3)')
    print('        -b, --backend=<string>          Backend to use')
    print('                                        Available values: pdf, pgf, png, ps, svg (default = pdf)')
    print('        -c, --config=<string>           Path to the default configuration file (default = $MKPLOT/defaults.json)')
    print('        -d, --dry-run                   Do not create a plot but instead show the tools sorted in the terminal')
    print('        --filter=<json-string>          Only include instances with key=value. Format: {"key": value}. (default = none)')
    print('        -f, --font=<string>             Font to use')
    print('                                        Available values: cmr, helvetica, palatino, times (default = times)')
    print('        --font-sz=<int>                 Font size to use')
    print('                                        Available values: [0 .. INT_MAX] (default = 12)')
    print('        --title-sz=<int>                Font size to use for title')
    print('                                        Available values: [0 .. INT_MAX] (default = 20)')
    print('        --axis-label-sz=<int>           Font size to use for axis labels')
    print('                                        Available values: [0 .. INT_MAX] (default = 12)')
    print('        -h, --help                      Show this message')
    print('        --no-grid                       Do not show the grid')
    print('        -j, --join-key=<string-list>    Comma-separated list of keys to join all benchmarks per each tool')
    print('        -k, --key=<string>              Key to measure')
    print('                                        Available values: \'rtime\', for others look at the STAT file (default = \'rtime\')')
    print('        -l, --latex                     Use latex')
    print('        --lalpha=<float>                Legend transparency level')
    print('                                        Available values: [0 .. 1] (default = 1.0)')
    print('        --legend=<string-list>          Comma-separated list of keys to use in the legend of a plot')
    print('                                        Format: "program,prog_args" (default = program)')
    print('        --lloc=<string>                 Legend location')
    print('                                        Available values: upper/center/lower left/right, center, best, off (default = upper left)')
    print('        --lncol=<int>                   Number of columns in the legend')
    print('                                        Available values: [1 .. INT_MAX] (default = 1)')
    print('        --only=<string-list>            Comma-separated list of names')
    print('                                        Format: "tool1,tool2" (default = none)')
    print('        -p, --plot-type=<string>        Plot type to produce')
    print('                                        Available values: cactus or scatter (default = cactus)')
    print('        -r, --replace=<json-string>     List of name replacements')
    print('                                        Format: {"name1": "$nice_name1$", "name2": "$nice_name2$"} (default = none)')
    print('        --ratio=<json-string>           List of ratios to calculate: a/b per instance')
    print('                                        Format: {"ratio-name1": ["solver-a", "solver-b"], "ratio-name2": ["solver-a", "solver-b"]} (default = none)')
    print('        --ordering=<string>             Define how to ordering for scatter plot (cactus?)')
    print('                                        Values: sorted, reverse, fixed (default = sorted)')
    print('        --save-to=<string>              Where result figure should be saved')
    print('                                        Default value: plot')
    print('        --shape=<string>                Shape of the plot')
    print('                                        Available values: long, squared, standard (default = standard)')
    print('        -t, --timeout=<int>             Timeout value')
    print('                                        Available values: [0 .. INT_MAX] (default = 3600)')
    print('        --tol                           Whether to print timeout labels (default=false)')
    print('        --tlabel=<string>               Timeout label (for scatter plots only)')
    print('        --tol-loc=<string>              Where to put the timeout label')
    print('                                        Available values: before, after (default = after)')
    print('        --transparent                   Save the file in the transparent mode')
    print('        --vbs=<json-string>             List of VBSes')
    print('                                        Format: {"vbs1": ["tool1", "tool2"], "vbs2": "all"} (default = none)')
    print('        --use_tick_sep                  Use thousand separator for x and y tick labels. E.g. 10,000 instead of 10000')
    print('        --xkcd                          Use xkcd-style sketch plotting')
    print('        --xlabel=<string>               X label')
    print('        --xlog                          Use logarithmic scale for X axis')
    print('        --xmax=<int>                    X axis ends at this value')
    print('                                        Available values: [0 .. INT_MAX] (default = none)')
    print('        --xmin=<int>                    X axis starts from this value')
    print('                                        Available values: [0 .. INT_MAX] (default = 0)')
    print('        --ylabel=<string>               Y label')
    print('        --ylog                          Use logarithmic scale for Y axis')
    print('        --ymax=<int>                    Y axis ends at this value')
    print('                                        Available values: [0 .. INT_MAX] (default = none)')
    print('        --ymin=<int>                    Y axis starts from this value')
    print('                                        Available values: [0 .. INT_MAX] (default = 0)')
    print('        --markevery=<int>               Marker every X points')
    print('                                        Available values: [0 .. INT_MAX] (default = read from json)')
    print('        --scatter-color=<string>        Color of points in scatter plot')
    print('                                        Available values: [] (default = read from json)')

#
#==============================================================================
if __name__ == '__main__':
    options, fns = parse_options()

    if not fns:
        pass  # error handling

    data = load_data(fns, options)

    if options['dry_run']:
        for d in data:
            d1 = list(map(lambda x: min(x, options['timeout']), d[1]))

            print('{0}:'.format(d[0]))
            print('    # solved: {0}'.format(d[2]))
            print('    min. val: {0:.1f}'.format(float(min(d1))))
            print('    max. val: {0:.1f}'.format(float(max(d1))))
            print('    avg. val: {0:.1f}'.format(float(sum(d1)) / len(d1)))
    else:
        if options['plot_type'] == 'cactus':
            plotter = Cactus(options)
        else:
            plotter = Scatter(options)

        plotter.create(data)
