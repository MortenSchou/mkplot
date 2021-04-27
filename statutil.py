#!/usr/bin/env python3
#-*- coding:utf-8 -*-
##
## statutil.py
##
##  Created on: May 22, 2013
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

#
#==============================================================================
from __future__ import print_function
import json
import sys


#
#==============================================================================
class JSONException(Exception):
    pass


#
#==============================================================================
class Stat:
    """
        Simple statistical data class.
    """

    def __init__(self, legend=None, filename=None):
        """
            Constructor.
        """

        if filename is None:
            self.insts_own = []
            self.preamble = {}
            self.data = {}
            self.label = ''
        elif type(filename) is list:
            print( 'in case of several files use "StatArray" class', file=sys.stderr)
        else:
            self.read(legend, filename)
    def _set_insts_own(self):
        self.insts_own = sorted(list(set(self.data.keys())))

    def read(self, legend, filename=None):
        """
            Reads a file into a Stat object.
        """

        if filename is None:
            print( 'no filename was specified', file=sys.stderr)
            return

        with open(filename, 'r') as fp:
            #print('reading {0}'.format(filename), file=sys.stderr)
            try:
                data_full = json.load(fp)
            except:
                raise JSONException('Unable to parse \'{0}\'.'.format(filename))

            self.data = data_full['stats']
            self.preamble = data_full['preamble']
            self.preamble['origin'] = filename
            if type(legend) is list:
                self.label = ' '.join([self.preamble[k] for k in legend])
            else:
                self.label = self.preamble[legend]
            self.label = self.label.strip()
        self._set_insts_own()

    def write(self, to=None):
        """
            Writes a Stat object to a file.
        """

        to_write = {'preamble': self.preamble, 'stats': self.data}

        if to is None:
            to = self.preamble['origin']

        # 'origin' field is not needed anymore
        del(self.preamble['origin'])

        if type(to) is str:
            with open(to, 'w') as fp:
                json.dump(to_write, fp, indent=4, separators=(',', ': '))
        elif type(to) is file:
            json.dump(to_write, to, indent=4, separators=(',', ': '))
        else:
            print('don\'t know how to write to {0}'.format(type(to)), file=sys.stderr)

    def update(self, success=None, failure=None):
        """
            Updates stats using additional success and failure signs.
        """

        if success:
            pass

        if failure:
            sign = lambda x: x
            key = failure
            if failure[:3] == 'no-':
                sign = lambda x: not x
                key = failure[3:]

            for inst in self.insts_own:
                if inst in self.data and self.data[inst]['status'] == True:
                    if sign(key in self.data[inst]):
                        print('updating', inst, file=sys.stderr)
                        self.data[inst]['status'] = False

        self.write()

    def filterinsts(self,filters=None):
        def filter_inst(d):
            def filter_stuff(filter_key, filter_value):
                if filter_key not in d:
                    return False
                if isinstance(filter_value, list):
                    return (d[filter_key] in filter_value)
                return d[filter_key] == filter_value
            for filter_key, filter_val in filters.items():
                if not filter_stuff(filter_key, filter_val):
                    return False
            return True
        if filters:
            self.data = {inst: val for inst,val in self.data.items() if filter_inst(val)}
            self._set_insts_own()

    def get_data(self, options, min_value, max_value):
        vals = []
        num_solved = 0
        last_val = -1
        for inst in self.insts_own:  # insts_own are sorted
            val = self.data[inst][options['key']] if options['key'] in self.data[inst] else max_value
            if self.data[inst]['status'] == True:
                if val > last_val:
                    last_val = val
                if val >= float(options['timeout']):
                    val = max_value
                elif val <= min_value:
                    val = min_value
                num_solved += 1
            else:
                val = max_value
            vals.append(val)
        return (self.label, vals, num_solved, last_val)

    def list(self, crit=None):
        """
            Lists instances satisfying the criterion.
        """

        if crit:
            pred = lambda x: x == crit['val']
            if crit['pred'] == '<':
                pred = lambda x: x < crit['val']
            elif crit['pred'] == '<=':
                pred = lambda x: x <= crit['val']
            elif crit['pred'] == '>':
                pred = lambda x: x > crit['val']
            elif crit['pred'] == '>=':
                pred = lambda x: x >= crit['val']

            for inst in self.insts_own:
                if inst in self.data and self.data[inst]['status'] == True:
                    if pred(self.data[inst][crit['key']]):
                        print('{0}: {1} = {2}'.format(inst, crit['key'], self.data[inst][crit['key']]))


#
#==============================================================================
class StatArray:
    """
        Contains statistical data for several files.
    """

    def __init__(self, legend, files=None):
        """
            Constructor.
        """

        if files is None:
            self.inst_full = []
            self.stat_objs = []
        elif type(files) is list:
            self.read(legend, files)
        else:
            print('in case of just one file use "Stat" class', file=sys.stderr)
            self.read(legend, [files])

    def __getitem__(self, key):
        if key < len(self.stat_objs):
            return self.stat_objs[key]

    def __len__(self):
        return len(self.stat_objs)

    def __iter__(self):
        for stat_obj in self.stat_objs:
            yield stat_obj

    def read(self, legend, files=None):
        """
            Reads several files into a StatArray object.
        """

        if files is None:
            print('no files was specified', file=sys.stderr)
            return

        self.stat_objs = []
        for f in files:
            self.stat_objs.append(Stat(legend, f))
        self._set_inst_full()

    def _set_inst_full(self):
        inst_set = set()
        for stat_obj in self.stat_objs:
            inst_set = inst_set.union(set(stat_obj.insts_own))
        self.inst_full = sorted(list(inst_set))

    def write(self, files=None):
        """
            Writes a StatArray object to given files.
        """

        if files is None:
            files = [stat_obj.preamble['origin'] for stat_obj in self.stat_objs]

        assert len(files) == len(self.stat_objs), 'wrong number of filenames'

        for f, stat_obj in zip(files, self.stat_objs):
            stat_obj.write(f)

    def cluster(self, use_key=['program', 'prog_args']):
        """
            Clasters Stat objects according to their preamble values.
        """

        # the key should be a list
        if type(use_key) is not list:
            use_key = [use_key]

        clusters = {}

        for stat_obj in self.stat_objs:
            # updating the Stat object
            for i, i_old in enumerate(stat_obj.insts_own):
                i_new = '{0}@{1}'.format(i_old, stat_obj.preamble['benchmark'])
                stat_obj.insts_own[i] = i_new
                stat_obj.data[i_new] = stat_obj.data.pop(i_old)

            key = ' '.join([stat_obj.preamble[one_key] for one_key in use_key])
            if key in clusters:
                # update the cluster
                clusters[key].insts_own.extend(stat_obj.insts_own)
                clusters[key].data.update(stat_obj.data)

                clusters[key].preamble['benchmark'].append(stat_obj.preamble['benchmark'])
                clusters[key].preamble['program'].append(stat_obj.preamble['program'])
            else:
                # add new cluster
                clusters[key] = stat_obj
                clusters[key].preamble['benchmark'] = [clusters[key].preamble['benchmark']]
                clusters[key].preamble['program'] = [clusters[key].preamble['program']]

        self.stat_objs = [cl for cl in clusters.values()]
        self._set_inst_full()

    def unclaster(self):
        """
            Unclasters previously clastered Stat objects.
        """

        print('unclaster() method is not implemented yet', file=sys.stderr)

    def filterinsts(self,filters=None):
        """
            Filters instances from all stat_objs based on the filters parameter.
        """
        for stat_obj in self.stat_objs:
            stat_obj.filterinsts(filters)
        self._set_inst_full()

    def make_vbs(self, vbs_name, tools, key):
        """
            Makes vbs with label vbs_name from tools using the status to filter, and key as the measurement.
        """
        vbs_stat_objs = self.stat_objs if tools == 'all' else [stat_obj for stat_obj in self.stat_objs if stat_obj.label in tools]

        vbs = Stat()
        vbs.label = vbs_name

        # Not sure if this part is used...
        vbs.preamble = vbs_stat_objs[0].preamble
        vbs.preamble['program'] = 'best of ' + ','.join(tools)
        vbs.preamble['prog_args'] = ''
        vbs.preamble['origin'] = [obj.preamble['origin'] for obj in vbs_stat_objs]

        inst_set = set()
        for stat_obj in vbs_stat_objs:
            inst_set = inst_set.union(set(stat_obj.insts_own))
        vbs.insts_own = sorted(list(inst_set))

        for inst in vbs.insts_own:
            alts = []
            for stat_obj in vbs_stat_objs:
                if inst in stat_obj.data and stat_obj.data[inst]['status'] == True:
                    alts.append(stat_obj.data[inst])
            if alts:
                vbs.data[inst] = min(alts, key=lambda x: x[key] if key in x else float('inf'))
            else:
                # all fail; choose any:
                vbs.data[inst] = self.stat_objs[0].data[inst]

        self.stat_objs.append(vbs)
    
    def create_ratio(self, ratio_name, tools, key, timeout, max_value, weird_ratio = False):
        """
            Make a ratio stat_obj with label ratio_name, as the ratio tools[0] / tools[1]. 
        """
        ratio_stat_objs = [stat_obj for stat_obj in self.stat_objs if stat_obj.label in tools]

        ratio = Stat()
        ratio.label = ratio_name
        inst_set = set()
        for stat_obj in ratio_stat_objs:
            inst_set = inst_set.union(set(stat_obj.insts_own))
        insts = sorted(list(inst_set))

        def get_inst_val(inst, stat_obj):
            if inst in stat_obj.data and stat_obj.data[inst]['status'] == True and stat_obj.data[inst][key] < timeout:
                return stat_obj.data[inst][key]
            else:
                return timeout
        vals = []
        num_solved = 0
        last_val = float('-inf') if weird_ratio else -1
        for inst in insts:
            a = get_inst_val(inst, ratio_stat_objs[0])
            b = get_inst_val(inst, ratio_stat_objs[1])
            if a < timeout and b < timeout:
                val = (a / b - 1 if a >= b else 1 - b / a) if weird_ratio else a / b
                vals.append(val)
                #if val < 1:
                #    print(ratio_stat_objs[0].data[inst]['cegar-iterations'])
                if last_val < val:
                    last_val = val
            elif a < timeout:
                vals.append(float('-inf') if weird_ratio else 0)
            elif b < timeout:
                vals.append(max_value)
                last_val = max_value
            else:
                continue
            num_solved += 1
        return (ratio_name, vals, num_solved, last_val)

    def compare(self, cmp_key=None):
        """
            Compares values for a specific key. Do nothing if cmp_key is None.
        """

        if cmp_key:
            for inst in self.inst_full:
                vals = {}

                for stat_obj in self.stat_objs:
                    if inst in stat_obj.data and stat_obj.data[inst]['status'] == True and cmp_key in stat_obj.data[inst]:
                        if stat_obj.data[inst][cmp_key] in vals:
                            vals[stat_obj.data[inst][cmp_key]].append(stat_obj.preamble['origin'])
                        else:
                            vals[stat_obj.data[inst][cmp_key]] = [stat_obj.preamble['origin']]

                if len(vals.keys()) > 1:
                    print('different values found', file=sys.stderr)
                    print('instance:', inst, file=sys.stderr)
                    print('values:', vals, file=sys.stderr)

    def list_simple(self, to_list='all'):
        """
            Shows instances required by user.
        """

        if to_list:
            print('showing {0}:'.format(to_list))
            if to_list == 'all':
                for inst in self.inst_full:
                    print(inst)

            else:
                status = False if to_list == 'failed' else True

                for inst in self.inst_full:
                    objs = []

                    for stat_obj in self.stat_objs:
                        if inst in stat_obj.data and stat_obj.data[inst]['status'] == status:
                            p = stat_obj.preamble
                            if 'prog_alias' in p:
                                objs.append(p['prog_alias'])
                            else:
                                objs.append(p['program'] + ' ' + p['prog_args'])

                    if objs:
                        if len(self.stat_objs) > 1:
                            objs = '[{0}]'.format(', '.join(obj for obj in objs))
                            print('{0}: {1}'.format(inst, objs))
                        else:
                            print(inst)

    def list(self, crit=None):
        """
            Shows instances required by user.
        """

        if crit:
            for stat_obj in self.stat_objs:
                stat_obj.list(crit)

    def update(self, success=None, failure=None):
        """
            Update stats using additional success and failure signs.
        """

        if success or failure:
            for stat_obj in self.stat_objs:
                stat_obj.update(success, failure)
