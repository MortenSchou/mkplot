#!/usr/bin/env python3
#-*- coding:utf-8 -*-
##
## load.py
##
##  Created on: Jun 05, 2015
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

#
#==============================================================================
import csv
import json
import statutil
import six
import sys


#
#==============================================================================
def load_data(files, options):
    """
        Loads data from the input files.
    """

    try:  # if JSON data
        return load_json(statutil.StatArray(options['legend'], files), options)
    except statutil.JSONException as e:
        sys.stderr.write('\033[33;1mWarning:\033[m ' + str(e) + '\033[m\n')
        sys.stderr.write('Probably not a JSON format. Trying to read as CSV.\n')

        # reading CSV
        # expecting exactly one input file
        with open(files[0], 'r') as fp:
            # try:
            rows = csv.reader(fp, delimiter=' ', quotechar='|')
            rows = [row for row in rows]

            stats = []
            names = [n.strip() for n in rows[0][1:] if n.strip()]
            for row in rows[1:]:
                stats.append([val.strip() for val in row[1:] if val.strip()])

            return load_csv(names, stats, options)
            # except:
            #     sys.stderr.write('\033[31;1mError:\033[m Unable to read input file(s).\n')


#
#==============================================================================
def load_json(stat_arr, options):
    """
        Loads runtime data from STAT objects.
    """

    # preparing data
    if options['join_key']:
        stat_arr.cluster(use_key=options['join_key'])

    if options['filter']:
        stat_arr.filterinsts(options['filter'])

    data = []

    # choosing the minimal value
    min_value = 0.000000001
    if options['plot_type'] == 'scatter':
        if options['x_min']:
            min_value = max(options['x_min'], options['y_min'])
        else:
            min_value = options['y_min']  # options['y_min'] is always defined
    max_value = float(options['timeout']) if options['plot_type'] == 'scatter' else 10 * float(options['timeout'])
    
    # make VBSes
    if options['vbs']:
        for vbs_name, tools in options['vbs'].items():
            stat_arr.make_vbs(vbs_name, tools, options['key'])
    
    # processing (normal) separate data
    for stat_obj in stat_arr:
        data.append(stat_obj.get_data(options, min_value, max_value))

    if options['ratio']:
        max_value = float(options['timeout']) if options['plot_type'] == 'scatter' else 10 * float(options['y_max'] if options['y_max'] else options['timeout'])
        for ratio_name, tools in options['ratio'].items():
            data.append(stat_arr.create_ratio(ratio_name, tools, options['key'], options['timeout'], max_value))

    if options['only']:
        data = [d for d in data if d[0] in options['only']]

    if options['repls']:
        data = [(options['repls'][n], v, s, l) if n in options['repls'] else (n, v, s, l) for n, v, s, l in data]

    # use given order, do not sort
    if (options['ordering'] == "fixed"):
        return data

    return sorted(data, key=lambda x: x[2] + len(x[1]) / sum(x[1]), reverse=not (options['ordering'] == "reverse"))


#
#==============================================================================
def load_csv(names, stats, options):
    """
        Loads runtime CSV data.
    """

    # choosing the minimal value
    min_val = 0.000000001
    if options['plot_type'] == 'scatter':
        if options['x_min']:
            min_val = max(options['x_min'], options['y_min'])
        else:
            min_val = options['y_min']  # options['y_min'] is always defined

    names_orig = names[:]

    if options['repls']:
        names = [options['repls'][n] if n in options['repls'] else n for n in names]

    # processing (normal) separate data
    lens = [0 for n in names]
    vals_all = [[] for n in names]
    last_vals = [-1 for n in names]

    for vlist in stats:
        vlist = [float(val) for val in vlist]

        for i, val in enumerate(vlist):
            if val < float(options['timeout']):
                if val > last_vals[i]:
                    last_vals[i] = val

                if val < min_val:
                    val = min_val

                lens[i] += 1
            else:
                val = float(options['timeout'])
                if options['plot_type'] == 'cactus':
                    val *= 10

            vals_all[i].append(val)

    # processing VBSes
    if options['vbs']:
        for vbs_name, tools in options['vbs'].items():
            vals = []
            len_ = 0
            last_val = -1

            if tools != 'all':
                tools = [n if n in tools else '' for n in names_orig]

                for vlist in stats:
                    vlist = [float(val) for i, val in enumerate(vlist) if tools[i]]
                    val = min(vlist)

                    if val < float(options['timeout']):
                        if val > last_val:
                            last_val = val

                        if val < min_val:
                            val = min_val

                        len_ += 1
                    else:
                        val = options['timeout']
                        if options['plot_type'] == 'cactus':
                            val *= 10

                    vals.append(val)
            else:  # VBS among all the tools
                for vlist in stats:
                    val = min([float(val) for val in vlist])

                    if val < float(options['timeout']):
                        if val > last_val:
                            last_val = val

                        if val < min_val:
                            val = min_val

                        len_ += 1
                    else:
                        val = options['timeout']
                        if options['plot_type'] == 'cactus':
                            val *= 10

                    vals.append(val)

            names.append(vbs_name)
            names_orig.append(vbs_name)
            vals_all.append(vals)
            lens.append(len_)
            last_vals.append(last_val)

    data = [[n, t, s, l] for n, t, s, l in zip(names, vals_all, lens, last_vals)]

    if options['only']:
        data = [d for i, d in enumerate(data) if names_orig[i] in options['only']]

    # use given order, do not sort
    if (options['ordering'] == "fixed"):
        return data
    return sorted(data, key=lambda x: x[2] + len(x[1]) / sum(x[1]), reverse=not (options['ordering'] == "reverse"))
