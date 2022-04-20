#!/usr/bin/env python3
#-*- coding:utf-8 -*-
##
## analyse.py

from __future__ import print_function

import getopt
import json
import statutil
from load import load_data
import os
import sys

def parse_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'c:hj:k:r:t:',
                                   ['config=',
                                    'filter=',
                                    'help',
                                    'join-key=',
                                    'key=',
                                    'legend=',
                                    'only=',
                                    'replace=',
                                    'ordering=',
                                    'save-to=',
                                    'timeout=',
                                    'vbs=',
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
    
    options['ordering'] = "sorted"
    options['filter'] = False
    # parsing command-line options
    for opt, arg in opts:
        if opt in ('-c', '--config'):
            pass  # already processed
        elif opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt == '--filter':
            options['filter'] = json.loads(str(arg))
        elif opt in ('-j', '--join-key'):
            options['join_key'] = [k.strip() for k in str(arg).split(',')]
        elif opt in ('-k', '--key'):
            options['key'] = str(arg)
        elif opt == '--legend':
            options['legend'] = [k.strip() for k in str(arg).split(',')]
        elif opt == '--only':
            options['only'] = [t.strip() for t in str(arg).split(',')]
        elif opt in ('-r', '--replace'):
            options['repls'] = json.loads(str(arg))
        elif opt == '--ordering':
            options['ordering'] = str(arg)
        elif opt == '--save-to':
            options['save_to'] = str(arg)
        elif opt in ('-t', '--timeout'):
            options['timeout'] = float(arg)
        elif opt == '--vbs':
            options['vbs'] = json.loads(str(arg))
        else:
            assert False, 'Unhandled option: {0} {1}'.format(opt, arg)

    return options, args

#==============================================================================
def usage():
    """
        Prints usage message.
    """

    print('Usage:', os.path.basename(sys.argv[0]), ' [options] stat-files')
    print('Options:')
    print('        -c, --config=<string>           Path to the default configuration file (default = $MKPLOT/defaults.json)')
    print('        -h, --help                      Show this message')
    print('        -j, --join-key=<string-list>    Comma-separated list of keys to join all benchmarks per each tool')
    print('        -k, --key=<string>              Key to measure')
    print('                                        Available values: \'rtime\', for others look at the STAT file (default = \'rtime\')')
    print('        --legend=<string-list>          Comma-separated list of keys to use in the legend of a plot')
    print('                                        Format: "program,prog_args" (default = program)')
    print('        --only=<string-list>            Comma-separated list of names')
    print('                                        Format: "tool1,tool2" (default = none)')
    print('        -r, --replace=<json-string>     List of name replacements')
    print('                                        Format: {"name1": "$nice_name1$", "name2": "$nice_name2$"} (default = none)')
    print('        --ordering=<string>             Define how to ordering for scatter plot (cactus?)')
    print('                                        Values: sorted, reverse, fixed (default = sorted)')
    print('        --save-to=<string>              Where result figure should be saved')
    print('                                        Default value: plot')
    print('        -t, --timeout=<int>             Timeout value')
    print('                                        Available values: [0 .. INT_MAX] (default = 3600)')
    print('        --vbs=<json-string>             List of VBSes')
    print('                                        Format: {"vbs1": ["tool1", "tool2"], "vbs2": "all"} (default = none)')

#
#==============================================================================

def is_unique(x):
    if len(x) <= 1:
        return True
    y=[]
    for e in x:
        if isinstance(e,list):
            y.append(tuple(e))
        else:
            y.append(e)
    return len(set(y)) <= 1

if __name__ == '__main__':
    options, files = parse_options()

    if not files:
        pass  # error handling

    stat_arr = statutil.StatArray(options['legend'], files)
    
    # preparing data
    if options['join_key']:
        stat_arr.cluster(use_key=options['join_key'])
    
    if options['filter']:
        stat_arr.filterinsts(options['filter'])
    
    if options['vbs']:
        for vbs_name, tools in options['vbs'].items():
            stat_arr.make_vbs(vbs_name, tools, options['key'])

    max_val = float(options['timeout'])

    # # Median runtime for each tool    
    # for stat_obj in stat_arr:
    #     vals = []
    #     for inst in stat_arr.inst_full:
    #         vals.append(stat_obj.data[inst][options['key']] if options['key'] in stat_obj.data[inst] else max_val)
    #     vals = sorted(vals)
    #     print(stat_obj.label)
    #     print(len(vals))
    #     print(vals[int(len(vals)/2)])
    #     print()

    # results = {}
    # weights = {}
    # stat_arr.compare('result')
    # stat_arr.compare('weight')

    for inst in stat_arr.inst_full:
        results = []
        inst_pre = inst.split('@')[0]
        conf_i = inst.split('@')[1].split('-')[-1]
        for stat_obj in stat_arr:
            if inst in stat_obj.data:
                cur_data = stat_obj.data[inst]
            elif (inst_pre + '@v2-conf-' + conf_i) in stat_obj.data:
                cur_data = stat_obj.data[inst_pre + '@v2-conf-' + conf_i]
            elif (inst_pre + '@v2-latency-conf-' + conf_i) in stat_obj.data:
                cur_data = stat_obj.data[inst_pre + '@v2-latency-conf-' + conf_i]
            elif (inst_pre + '@v2-hops-latency-conf-' + conf_i) in stat_obj.data:
                cur_data = stat_obj.data[inst_pre + '@v2-hops-latency-conf-' + conf_i]
            else:
                continue
            if cur_data['status']:
                results.append(cur_data['result'])
        if not is_unique(results): # or not is_unique(weights):
            print(inst)
            print(results)
            # print(weights)
    # sys.exit(0)
    for inst in stat_arr.inst_full:
        weights = []
        weight_dict = {}
        max_weights = []
        for stat_obj in stat_arr:
            if inst in stat_obj.data and stat_obj.data[inst]['status'] == True and 'weight' in stat_obj.data[inst]:
                if stat_obj.label.startswith("E2-T3"):
                    max_weights.append(stat_obj.data[inst]['weight'])
                else:
                    weights.append(stat_obj.data[inst]['weight'])
                if not isinstance(stat_obj.data[inst]['weight'], list):
                    if stat_obj.data[inst]['weight'] in weight_dict:
                        weight_dict[stat_obj.data[inst]['weight']].append(stat_obj.label)
                    else:
                        weight_dict[stat_obj.data[inst]['weight']] = [stat_obj.label]
        if not is_unique(weights) or not is_unique(max_weights):
            print(inst)
            print(weights)
            print(max_weights)
            print(weight_dict)
    # sys.exit(0)


    # count_inconclusive = 0
    # for inst in stat_arr.inst_full:
    #     if ('result' in stat_arr[0].data[inst] and stat_arr[0].data[inst]['result'] is None):
    #         for stat_obj in stat_arr:
    #             print(stat_obj.label, inst, stat_obj.data[inst]['status'])
    #         print()
    #         print(stat_arr[0].label, stat_arr[0].data[inst])
    #         count_inconclusive += 1
    #     # for inst in stat_obj.insts_own:
    #     #     if stat_obj.data[inst]['status'] == False or options['key'] not in stat_obj.data[inst] or stat_obj.data[inst][options['key']] > max_val :
    #     #         count_inconclusive += 1
    # print(stat_arr[0].label, stat_arr[1].label)
    # print(count_inconclusive, "inconclusive instances")
    # sys.exit(0)

    # count=0
    # for inst in stat_arr.inst_full:
    #     if stat_arr[0].data[inst]['status'] and stat_arr[0].data[inst][options['key']] < max_val and all((not stat_arr[i].data[inst]['status']) or stat_arr[i].data[inst][options['key']] >= max_val for i in range(1,len(stat_arr))):
    #         count+=1
    #         print(inst)
    # print(count)
    # exit(0)

    # for stat_obj in stat_arr:
    #     if stat_obj.label in ["config10-E2-T3-Whops", "config10-E2-T3-Wlatency"]:
    #         tool_name = options['repls'][stat_obj.label] if "repls" in options and stat_obj.label in options['repls'] else stat_obj.label
    #         print(tool_name)
    #         for inst in stat_obj.insts_own:
    #             if 'result' in stat_obj.data[inst] and stat_obj.data[inst]['result'] == True and options['key'] in stat_obj.data[inst] and stat_obj.data[inst][options['key']] < max_val:
    #                 # result=True
    #                 if 'weight' in stat_obj.data[inst] and stat_obj.data[inst]['weight'] is not None and stat_obj.data[inst]['weight'] != "infinite":
    #                     print(stat_obj.data[inst])
    #         print()
    #         print()


    # exit(0)


    from tabulate import tabulate
    stats = []
    for stat_obj in stat_arr:
        tool_name = options['repls'][stat_obj.label] if "repls" in options and stat_obj.label in options['repls'] else stat_obj.label
        counts = {"name": tool_name, "true": 0, "false":0, "inconclusive":0, "time-out":0, "infinity": 0, "conclusive":0, "unanswered": 0, "all":0}
        # count_inconclusive = 0
        for inst in stat_obj.insts_own:
            counts["all"] += 1
            if 'result' in stat_obj.data[inst] and stat_obj.data[inst]['result'] == True and options['key'] in stat_obj.data[inst] and stat_obj.data[inst][options['key']] < max_val:
                counts["true"] += 1
                counts["conclusive"] += 1
            if 'result' in stat_obj.data[inst] and stat_obj.data[inst]['result'] == False and options['key'] in stat_obj.data[inst] and stat_obj.data[inst][options['key']] < max_val:
                counts["false"] += 1
                counts["conclusive"] += 1
            if 'result' in stat_obj.data[inst] and stat_obj.data[inst]['result'] is None and options['key'] in stat_obj.data[inst] and stat_obj.data[inst][options['key']] < max_val:
                counts["inconclusive"] += 1
            if options['key'] not in stat_obj.data[inst] or stat_obj.data[inst][options['key']] >= max_val:
                counts["time-out"] += 1
            if stat_obj.data[inst]['status'] == False or options['key'] not in stat_obj.data[inst] or stat_obj.data[inst][options['key']] >= max_val:
                counts["unanswered"] += 1
            if 'weight' in stat_obj.data[inst] and stat_obj.data[inst]['weight'] == "infinity" and options['key'] in stat_obj.data[inst] and stat_obj.data[inst][options['key']] < max_val:
                counts["infinity"] += 1
        stats.append(counts.values())
        # print(count, "inconclusive instances")
    print(tabulate(stats, headers=["name", "true", "false", "inconclusive", "time-out", "infinite trace (of true)", "true + false", "inconclusive + time-out", "all"]))
    exit(0)

    for stat_obj in stat_arr:
        count_inconclusive = 0
        for inst in stat_obj.insts_own:
            if 'result' in stat_obj.data[inst] and stat_obj.data[inst]['result'] is None and options['key'] in stat_obj.data[inst] and stat_obj.data[inst][options['key']] < max_val:
                count_inconclusive += 1
        print(stat_obj.label)
        print(count_inconclusive, "inconclusive instances")

    for stat_obj in stat_arr:
        count_unanswered = 0
        for inst in stat_obj.insts_own:
            if stat_obj.data[inst]['status'] == False or options['key'] not in stat_obj.data[inst] or stat_obj.data[inst][options['key']] > max_val :
                count_unanswered += 1
        print(stat_obj.label)
        print(count_unanswered, "unanswered instances")
    
    for stat_obj in stat_arr:
        count_infinities = 0
        for inst in stat_obj.insts_own:
            if 'weight' in stat_obj.data[inst] and stat_obj.data[inst]['weight'] == "infinity" :
                count_infinities += 1
        print(stat_obj.label)
        print(count_infinities, "with trace_weight=infinite")
    sys.exit(0)

    # 
    # -----------------
    # 

    for stat_obj in stat_arr:
        print(stat_obj.label)
        print("Instance: ", '1184@Colt-config500-benchmark5')
        d = stat_obj.data['1184@Colt-config500-benchmark5']
        if options['key'] in d:
            print(d[options['key']])
        print("The 49629'th fastest for this tool:")
        val = sorted(stat_obj.data.items(), key=lambda item: min(max_val,item[1][options['key']] if item[1]['status'] and options['key'] in item[1] else max_val))[49629-1]
        print(val)
    sys.exit(0)

    max_inst = ""
    max_keyv = 0
    counsttt=0
    # for x in sorted(stat_arr[0].data.items(), key=lambda item: min(max_val, (item[1][options['key']] if item[1]['status'] and options['key'] in item[1] else max_val*10)))[:45645]:
    #     print(x[1]['rtime'], x[1]['status'])
    
    for inst, val in stat_arr[0].data.items():
        if val['status'] and val[options['key']] <= max_val:
            counsttt += 1
            if val[options['key']] > max_keyv:
                max_keyv = val[options['key']]
                max_inst = inst
    print(stat_arr[0].label)
    print(counsttt)
    print("Last query before timeout:")
    print(max_inst, stat_arr[0].data[max_inst])
    sys.exit(0)

    # parsing_times = []
    # for stat in stat_arr:
    #     for inst in stat.insts_own:
    #         if 'parsing' in stat.data[inst]:
    #             parsing_times.append(stat.data[inst]['parsing'])
    # print("len:", len(parsing_times))
    # print("avg parsing:", float(sum(parsing_times)) / len(parsing_times))
    # print("median parsing:", sorted(parsing_times)[int(len(parsing_times)/2)])
    # sys.exit(0)

    if len(stat_arr) != 2:
        sys.stderr.write("Error: analyse.py requires exactly two solvers.\n")
        sys.exit(1)

    # Analysis of ET
    # print(stat_arr[0].label)
    # print(stat_arr[1].label)
    # rats = []
    # vals0 = []
    # vals1 = []
    # for inst in stat_arr.inst_full:
    #     val0 = stat_arr[0].data[inst][options['key']] if inst in stat_arr[0].data and options['key'] in stat_arr[0].data[inst] else max_val
    #     val1 = stat_arr[1].data[inst][options['key']] if inst in stat_arr[1].data and options['key'] in stat_arr[1].data[inst] else max_val
    #     val0 = min(val0, max_val)
    #     val1 = min(val1, max_val)
    #     if val0 < max_val or val1 < max_val:
    #         vals0.append(val0)
    #         vals1.append(val1)
    #         rats.append(val0/val1)
    # print("Avg ratio: ", float(sum(rats))/len(rats))
    # avg_val_0 = float(sum(vals0))/len(vals0)
    # avg_val_1 = float(sum(vals1))/len(vals1)
    # print("Avg val0:", avg_val_0)
    # print("Avg val1:", avg_val_1)
    # print("their ratio:", avg_val_0 / avg_val_1)
    # rats = sorted(rats)
    # print("median ratio:", rats[int(len(rats)/2)])


    # for inst, d in stat_arr[0].data.items():
    #     val = d[options['key']] if options['key'] in d else max_val
    #     vals0.append(vals0)

    # for inst, d in stat_arr[0].data.items():
    #     val0 = d[options['key']] if options['key'] in d else max_val
    
    # sys.exit(0)
    

    # Analysis of CEGAR results

    e0 = stat_arr[0].data
    e1 = stat_arr[1].data
    #if (e0.keys() != e1.keys()):
    #    sys.stderr.write("Error: The two files does not contains the same experiments.\n")
    #    sys.exit(1)
    if any(("cegar-iterations" in v) for v in e0.values()):
        e0, e1 = e1, e0

    ratios={}
    cegar_iterations_faster = []
    cegar_iterations_slower = []
    not_counted = 0
    cegar_win = 0
    dual_win = 0
    for inst in stat_arr.inst_full:
        val0 = e0[inst][options['key']] if inst in e0 and options['key'] in e0[inst] else max_val
        val1 = e1[inst][options['key']] if inst in e1 and options['key'] in e1[inst] else max_val
        val0 = min(val0, max_val)
        val1 = min(val1, max_val)
        if val1 < val0:
            cegar_win += 1
            ratios[inst] = val0 / val1
            #if val0 == max_val:
            #    print("** barf **", inst)
        if val0 < val1:
            dual_win += 1
        if inst in e1 and "cegar-iterations" in e1[inst]:
            if val1 < val0:
                cegar_iterations_faster.append(e1[inst]["cegar-iterations"])
            else:
                cegar_iterations_slower.append(e1[inst]["cegar-iterations"])
        else:
            not_counted += 1
    
    cegariters = sorted(cegar_iterations_faster)
    print(len(cegar_iterations_faster))
    for i in range(86):
        countit = cegar_iterations_faster.count(i)
        if countit > 0:
            print('Iterations {0}. Count: {1}'.format(i,countit))
    # print(cegariters)
    sys.exit(0)

    print("CEGAR win: ", cegar_win, "(", 100*(cegar_win/(cegar_win + dual_win)), "%)")
    print("dual* win: ", dual_win)
    print("Total: ", cegar_win + dual_win)
    print()
    
    print("Faster: ")
    print('    count   :', len(cegar_iterations_faster))
    if len(cegar_iterations_faster) > 0: 
        print('    min. iterations:', int(min(cegar_iterations_faster)))
        print('    max. iterations:', int(max(cegar_iterations_faster)))
        print('    med. iterations:', int(cegar_iterations_faster[int(len(cegar_iterations_faster)/2)]))
        print('    avg. iterations: {0:.1f}'.format(float(sum(cegar_iterations_faster)) / len(cegar_iterations_faster)))
    print("Slower: ")
    print('    count   :', len(cegar_iterations_slower))
    if len(cegar_iterations_slower) > 0: 
        print('    min. iterations:', int(min(cegar_iterations_slower)))
        print('    max. iterations:', int(max(cegar_iterations_slower)))
        print('    med. iterations:', int(cegar_iterations_slower[int(len(cegar_iterations_slower)/2)]))
        print('    avg. iterations: {0:.1f}'.format(float(sum(cegar_iterations_slower)) / len(cegar_iterations_slower)))
    print('not counted:', not_counted)
    print()
    # print("Topology & Query & CEGAR time & dual* time & ratio \\\\ \\hline")
    # for inst, value in sorted(ratios.items(), key=lambda item: item[1])[-10:]:
    #     val0 = e0[inst][options['key']] if inst in e0 and options['key'] in e0[inst] else max_val
    #     val1 = e1[inst][options['key']] if inst in e1 and options['key'] in e1[inst] else max_val
    #     val0 = min(val0, max_val)
    #     val1 = min(val1, max_val)
    #     print('{0} & {1} & {2:.2f}s & {3:.2f}s & {4:.2f} \\\\ \\hline'.format(inst.split('@')[1].split('-')[0], e1[inst]['query'], val1, val0, value))
    