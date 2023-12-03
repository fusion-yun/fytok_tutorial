#!/task/imd/python/bin/python
"""
A generalized, standard "ordered" dictionary

OPTIONS:
 - CASE   : if None   , case-sensitive (default)
            if "upper", case-insensitive and upper-character displayed
            if "lower", case-insensitive and lower-character displayed
"""
"""
UPDATE HISTORY:
- Upgrade to multiple function such as write, update k file. Chenguang Wan
- Upgrade to python 3 compatiable.
                                                                 - Chenguang Wan
- A method 'copy()' upgraded in order to copy real values, not references.
                                                                  - 20080722 YMJ
- New option for CASE-SENSITIVITY added and some basic corrections made
                                                                  - 20080412 YMJ
- First created                                                   - 20080201 YMJ
"""




import re
from typing import List, Optional
import numpy as np
import sys
# sys.path.append("/gpfs/scratch/chgwang/Papers")
# sys.path.append("/scratch/liuxj/01_work_2022/sources/spdb_for_efit/")
# from private_modules.mdsData import getDataLocal
# from SpDB_to_get_east_data import get_eastdata_from_spdb
# from SpDB_to_get_east_data_remote import get_eastdata_from_spdb_remote
# from SpDB_to_get_east_data import get_eastdata_from_spdb_remote
class odict:
    """ """

    def __init__(self, dict=None, case=None, **kwargs):
        self.data = {}
        self.okeys = []
        self.case = case
        if dict:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def __repr__(self):
        str = "{"
        for key in self.okeys:
            str += "'%s': %s, " % (key, self[key])
        if len(str) == 1:
            str += "}"
        else:
            str = str[:-2]+"}"

        return str

    def __len__(self): return len(self.data)

    def __getitem__(self, key):
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if key in self.okeys:
            return self.data[key]
        else:
            print("key not found")
            return

    def __setitem__(self, key, item):
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if hasattr(item, "items"):
            self.data[key] = odict(item, case=self.case)
        else:
            self.data[key] = item

        if not key in self.okeys:
            self.okeys.append(key)

    def __delitem__(self, key):
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if key in self.okeys:
            self.okeys.remove(key)
            del self.data[key]

    def __add__(self, other):
        new_odict = self.copy()
        new_odict.update(other)
        return new_odict

    def clear(self): self.data.clear(); self.okeys = []

    def copy(self):
        """
        This copy is not same with intrinsic copy() of python. Intrinsic copy() just copies
        its value, so that for a dictionary or a list it copies its reference, not value. 
        Here this copy() is designed to copy its corresponding value. 
        Note that in most cases it works well, but if it has a dictionary as its value, then
        it copies its reference. (It's impossible to generalize this functionality to a
        dictionary-type value, because there is no way to figure out how many levels that
        dictionary has.)
        """
        import copy
        return copy.deepcopy(self)

    def keys(self): return self.okeys[:]

    def items(self):
        item = []
        for k in self.okeys:
            item.append((k, self[k]))
        return item

    def has_key(self, key):
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if key in self.okeys:
            return True
        return False

    def update(self, dict=None, **kwargs):
        """ This update means adding new ones and replacing existing ones. """
        # For dict
        if dict:
            for k, v in dict.items():
                if self.case:
                    if self.case.lower() == "upper":
                        k = k.upper()
                    if self.case.lower() == "lower":
                        k = k.lower()
                if hasattr(v, "items"):
                    self.data[k] = odict(v, case=self.case)
                else:
                    self.data[k] = v
                if not k in self.okeys:
                    self.okeys.append(k)
        # For kwargs
        if len(kwargs):
            for k, v in kwargs.items():
                if self.case:
                    if self.case.lower() == 'upper':
                        k = k.upper()
                    if self.case.lower() == 'lower':
                        k = k.lower()
                if hasattr(v, "items"):
                    self.data[k] = odict(v, case=self.case)
                else:
                    self.data[k] = v
                if not k in self.okeys:
                    self.okeys.append(k)

    def get(self, key, notkey=None):
        """
        Get the value corresponding to the key. If the given key is not
        recognized, then the notkey's value is returned
        """
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if key in self.okeys:
            return self[key]
        elif notkey:
            return notkey
        else:
            return None

    def pop(self, key, notkey=None):
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if key in self.okeys:
            self.okeys.remove(key)
            return self.data.pop(key)
        elif notkey:
            return notkey
        else:
            return None

    def popitem(self):
        if len(self.okeys):
            key = self.okeys.pop()
            val = self.data.pop(key)
            return (key, val)
        else:
            return (None, None)

    def __contains__(self, key):
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        return self.data._contains_(key)

#======================================================================#


class Namelist(odict):
    """ 
    A class that handles all namelist related functions.
    """
    #-------------------------------------------------------------------#

    def __init__(self, filename="", string="", nml=None, case="upper"):
        """
        A constructor. If argument 'filename' is given, then it will read that
        file automatically. The read data is stored to a dictionary, whose key
        is names of each namelist and value is another dictionary, whose key 
        is names of variables and value is their value list.
        """
        # initialize
        self.case = case
        self.head = ""
        self.tail = ""
        self.look = odict(case=self.case)
        self.namelist = odict(case=self.case)

        self.data = self.namelist.data
        self.okeys = self.namelist.okeys

        if nml:
            self.update(nml)

        if (filename != ""):
            self.read(filename=filename)
        elif (string != ""):
            self.read(string=string)
        else:
            pass

    #-------------------------------------------------------------------#
    def __repr__(self):
        """ display the namelist contents in a certain form """
        str0 = ""
        for key, value in self.namelist.items():
            str0 += "[[%s]]\n" % (key)
            strtmp = ""
            for k, v in value.items():
                strtmp += "%s = %s\n" % (k, v)
            if strtmp == "":
                strtmp = "{}\n"
            str0 += strtmp
        if str0 == "":
            str0 = "{}"
        return str0

    #-------------------------------------------------------------------#
    def __setitem__(self, key, item):
        """ """
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if hasattr(item, "keys"):
            self.data[key] = odict(item, case=self.case)
        else:
            print(
                "[Error] in '%s'.__setitem__() : value must be a dictionary" % (__name__))
            return

        if not key in self.okeys:
            self.okeys.append(key)

    def __getitem__(self, key):
        """
        Note that this method of Namelist.py has special feature, that is,
        if user tries to access non-existing key (namelist blockname), then
        that key is created automatically and return empty dictionary.
        """
        if self.case:
            if self.case.lower() == "upper":
                key = key.upper()
            if self.case.lower() == "lower":
                key = key.lower()
        if key in self.okeys:
            return self.data[key]
        else:
            self.__setitem__(key, {})
            return self.__getitem__(key)

    #-------------------------------------------------------------------#
    def __add__(self, other):
        """ sum two objects and return new combined one """
        new_nml = self.copy()
        new_nml.update(other)
        return new_nml

    #-------------------------------------------------------------------#
    def copy(self):
        """ 
        This copy is not same with intrinsic copy() of python. Intrinsic copy() just copies
        its value, so that for a dictionary or a list it copies its reference, not value. 
        Here this copy() is designed to copy its corresponding value. 
        Note that in most cases it works well, but if it has a dictionary as its value, then
        it copies its reference. (It's impossible to generalize this functionality to a
        dictionary-type value, because there is no way to figure out how many levels that
        dictionary has.)
        """
        import copy
        return copy.deepcopy(self)

        namelist = self.namelist
        data = self.data
        okeys = self.okeys
        head = self.head
        tail = self.tail
        look = self.look
        try:
            self.namelist = odict(case=self.case)
            self.data = self.namelist.data
            self.okeys = self.namelist.okeys
            self.head = ""
            self.tail = ""
            self.look = odict(case=self.case)
            c = copy.copy(self)  # shallow copy
        finally:
            self.namelist = namelist
            self.data = data
            self.okeys = okeys
            self.head = head
            self.tail = tail
            self.look = look
        c.update(self)
        c.head = head[:]
        c.tail = tail[:]
        return c

    #-------------------------------------------------------------------#
    def clear(self):
        """ Reset namelist """
        # Make inherited functions work by making same object variables
        # <-- Should I have to define variables with same names as parent class???
        self.head = ""
        self.tail = ""
        self.look = odict(case=self.case)
        self.namelist = odict(case=self.case)

        self.data = self.namelist.data
        self.okeys = self.namelist.okeys

    #-------------------------------------------------------------------#
    def update(self, nml):
        """
        Update the elements. Only self.namelist and self.look are updated
        ('head' and 'tail', and 'case' attribute are kept with original
        values.). 
        """
        if not isinstance(nml, Namelist):
            print("Error : Must be an instance of Namelist")
            return None

        for k in nml.keys():
            if self.case:
                if self.case.lower() == "upper":
                    k = k.upper()
                if self.case.lower() == "lower":
                    k = k.lower()
            self[k].update(nml[k])

    #-------------------------------------------------------------------#
    def getHead(self):
        """ Return a string of the head """
        return self.head[:]

    def setHead(self, str):
        """ Set a head """
        self.head = str[:]

    #===================================================================#
    def read(self, filename="", string="", only=None):
        """
        Read a namelist from a file. Returns a dictionary whose key is names 
        of each namelist and value is another dictionary, whose key is names
        of variables and value is their value list.

        INPUTS:
          filename   : filename to be read
          string     : string to be read
        """
        self.clear()

        # Convert to a String
        if filename != "":
            try:
                f = open(filename, "r")
                lines = f.read()
                f.close()
            except:
                print("[Error] in %s.read() : Given file not found" %
                      (__name__))
                return
        elif (string != ""):
            lines = string[:]
        else:
            print("[Error] in %s.read() : proper input required" % (__name__))
            return
        if only:
            only = [k.upper() for k in only]
        """
       # Take all comments off
       lines = self.__CommentOut__(lines)
       
       # Figure out names of each namelist
       blocks = self.__getBlocks__(lines)
       """
        blocks = self.__splitBlocks__(lines)
        for k, v in blocks.items():
            if only:
                if k.upper() not in only:
                    continue
            # figure out each variable assignment
            varDict, look = self.__getAssignments__(v)
            self.look[k] = look[:]
            self.namelist[k] = varDict

    def __splitBlocks__(self, str):
        """
        Split whole string into each strings of namelist blocks. Also figures out the 
        heading and tailing comments separately. Comments contained in each lines also
        removed. Return value is a dictionary whose key is a name of namelist-block and
        whose value is a string of each namelist block.
        """
        idx_start = []   # a list of starting point index
        idx_end = []   # a list of ending   point index
        dict = odict()  # a set of pairs whose key is the name of namelist-block
        # and whose value is a block string

        # Find out rough positions of starting of namelist-block
        #iter = re.finditer(r"^[ \t\r\f\v]*?[&$](?=\w)",str,re.I|re.M)
        iter = re.finditer(r"^[ \t\r\f\v]*?[&$](?=(\w)+?\s)", str, re.I | re.M)
        for match in iter:
            dtmp = match.span()
            if str[dtmp[1]:dtmp[1]+3].lower() == 'end':
                continue  # if [$&]end, then skip
            idx_start.append(dtmp[1])
            idx_end.append(dtmp[0])
        try:  # Find the head comments
            if idx_end[0] > 0:
                self.head = str[:idx_end[0]]
        except:
            pass

        # Find out rough positions of ending of namelist-block
        nblock = len(idx_start)
        if nblock == 0:
            return []
        else:  # old value of idx_end indicates each start-index of matched patterns
            for i in range(0, nblock-1):
                idx_end[i] = idx_end[i+1]
            idx_end[nblock-1] = len(str)

        # Figure out the names of namelist-blocks and find out exact block ranges
        for i in range(0, nblock):
            str1 = str[idx_start[i]: idx_end[i]]  # '+1' means excluding '$|&'

            # Name of namelist-block
            res = re.match(r"\w+?(?=\s)", str1, re.I | re.M)
            name = res.group()
            idx_start[i] = idx_start[i]+len(name)
            str1 = str1[len(name):]

            # Figure out the end of namelist block exactly
            pat = re.compile(r"[!;].*?$", re.I | re.M)
            str2 = pat.sub(" ", str1)  # Comments taked away

            iter = re.finditer(r"[$&/](?=(end)?\s)", str2, re.I | re.M)
            iend = None
            for match in iter:
                dtmp = match.span()
                iend = dtmp[0]
            # therefore ... returned blocks are ...
            if iend:
                dict[name.upper()] = str2[:iend]

            # Find the tail comments
            if i < nblock-1:
                continue  # go next iteration
            # before comments taken out
            iter = re.finditer(r"[$&/](end)?\s", str1, re.I | re.M)
            itail = 0
            for match in iter:
                dtmp = match.span()
                itail = dtmp[1]
            self.tail = str1[itail:]
            if str1[itail-1] != "\n":
                res = re.match(r".*?\n", self.tail, re.I | re.M)
                try:
                    dtmp = res.span()
                    self.tail = self.tail[dtmp[1]:]
                except:
                    pass
        return dict

    #####################################################################
    def __CommentOut__(self, str):
        """
        Comment out the comment part from string lines. A input is a multi-line
        string, and the comment-out lines are returned.
        Comment symbols are '!' and ';'.
        """
        # Get header
        try:
            pat = re.compile(r"^[ \t\r\f\v]*?[&$]\w+?", re.I | re.M)
            range = pat.search(str).span()
            self.head = str[:range[0]]
            str = str[range[0]:]
        except:
            pass

        # Get tail
        try:
            # iterator = re.compile(r"^[ \t\r\f\v]*?([/]|([$]end)|(&end)).*?$",\
            #           re.I | re.M).finditer(str)
            iterator = re.compile(r"^[ \t\r\f\v]*?.*?([/]|([$]end)|(&end))",
                                  re.I | re.M).finditer(str)
            id_end = 0
            for match in iterator:
                dtmp = match.span()
                id_end = dtmp[1]
            self.tail = str[id_end:]
            str = str[:id_end]
        except:
            pass

        # Take all comments off
        pattern1 = re.compile(r"!+.*?$", re.M)
        pattern2 = re.compile(r";+.*?$", re.M)

        if pattern1.search(str):  # symbol "!"
            str = pattern1.sub("", str)
        if pattern2.search(str):  # symbol ";"
            str = pattern2.sub("", str)

        return str

    #####################################################################
    def __getBlocks__(self, lines):
        """
        Get names and blocks of each namelists.
        return a dictionay with the name of the namelist as the key and
        the contens of the namelist as its value.
        The starting of each namelist block is specified with '&name' or
        '$name', and ending is specified with '&end', '$end', or '\'.
        """
        dict = odict()
        pattern = re.compile(r""" 
                                 # '.' = any character except newline. In DOTALL, any character
                                 # '+' = 1 or more matching
                                 # '*' = 0 or more matching
                                 # '?' = 0 or 1 matching
                  [$&]           # '[...]' = a set of character. Therefore, inside it,
                                 #     '$' is not special character. [$&] = '$' or '&'.
                  (
                   (?i)          # set a flag 're.I'. re.I = 'ignore case'
                   \w+           # '\w'= match any alphanumeric character and '_'
                  )              
                  \s*?           # '\s'= any white space
                  $             
                  (.*?)          # any things
                  (
                  ([$&](?i)end)  # '$end' or '&END' or '$End' etc
                  |              # or
                  [$&]           # '$' or '&' etc
                  |
                  /              # '/'
                  )
                  \s*?$          # any white space + newline
                  """, re.S | re.X | re.M)  # S(dotall), X(verbose), M(multiline)
        for pair in pattern.findall(lines):
            dict[pair[0].upper()] = pair[1]
        print("block = ")
        print(dict)

        return dict

    #####################################################################
    def __getAssignments__(self, str):
        """
        Get a dictionary of (variable, value) from an input string. Input 'str'
        is a multiline string which contains a series of 'variable = values'.
        First it splits 'str' to substrings of 'variable = values', and then
        calls 'splitAssing()' function to get its variable name and values.
        Return value is a dictionary whose key is each variable name and value
        is each value such as [ 'variable1 = value','variable2 =value2'].
        """
        pattern = re.compile(r"""
                                 # '.' = any character except newline. In DOTALL, any character
                                 # '+' = 1 or more matching
                                 # '*' = 0 or more matching
                                 # '?' = 0 or 1 matching
                  #\w+           # any alphanumeric character and '_'
                  [a-zA-Z0-9_]+
                  [0-9(),]*?
                  \s* = \s*       # search ' = ' things
                  .*?            # any characters
                  (?=            # '(?=...)' means that matched if following string matches
                                 #           with '...'
                  #\w+
                  [a-zA-Z0-9_]+
                  [0-9(),]*?
                  \s*
                  =
                  |$            # '$' = end of the string or just before newline
                  )
                 """, re.DOTALL | re.VERBOSE)
        # First, let's delete a space between "(" and ")".
        fiter = re.compile(r"[(].*?[)]").finditer(str)
        spans = []
        str_new = ""
        for match in fiter:
            spans.append(match.span())
        #     if t==0, then
        if (len(spans) != 0):
            start = spans[0][0]
            end = spans[0][1]
            tgt_str = str[start:end]
            tgt_str = re.compile(r"\s").sub("", tgt_str)
            str_new = str_new + str[:spans[0][0]] + tgt_str
        for t in range(1, len(spans)):
            start = spans[t][0]
            end = spans[t][1]
            tgt_str = str[start:end]
            tgt_str = re.compile(r"\s").sub("", tgt_str)
            str_new = str_new + str[spans[t-1][1]:start] + tgt_str
        #     for end part of string
        if (len(spans) != 0):
            str_new = str_new + str[spans[len(spans)-1][1]:]
        if (len(spans) == 0):
            str_new = str[:]

        # Split whole string to blocks
        dict = odict()
        dict["__sequence__"] = []  # saving the sequence of variables
        dict["__look__"] = []  # saving the sequence of variables
        for pat in pattern.findall(str_new):
            variable, value = self.__splitAssign__(pat)
            dict = self.__updateElements__(
                variable, value, dict)  # updating dict

        dict.pop("__sequence__")
        look = dict["__look__"][:]
        dict.pop("__look__")
        return dict, look

    #####################################################################
    def __splitAssign__(self, str):
        """
        Get a variable name and its value from a 'str'. Input 'str' has a 
        form, 'variable = values'. Values can be one of followings; scalar,
        1d-array, string, string-array. To indicate a string, one can use
        "'" or '"' symbol. To distinguish each elements, one can use white-
        space or ",". Return value is a dictionary whose key is its variable
        name and value is its value (single value or list).
        """
        variable, value = str.split("=")
        variable = variable.strip().upper()
        if re.compile(r"\n").search(value):  # if newline, then substitute by " "
            value = re.compile(r"\n").sub(" ", value)

        if re.compile(r"(\'.*?\')|(\".*?\")").search(value):  # if string or character
            value1 = re.compile(r"""['].*?[']""").findall(value)
            value2 = re.compile(r"""["].*?["]""").findall(value)
            value = []
            for val in value1:
                value.append(val[1:-1])
            for val in value2:
                value.append(val[1:-1])
        elif re.compile(r"([.]true[.])|([.]false[.])|([.]t[.])|([.]f[.])|t|f|true|false",
                        re.I).search(value):  # boolean
            value0 = re.compile(r",").sub(
                " ", value)  # substitute ',' with ' '
            value0 = value0.split()
            value = []
            for val in value0:
                val0 = val.lower()
                if val0 in [".true.", "true", ".t.", "t"]:
                    value.append(True)
                else:
                    value.append(False)
        else:  # if numeric
            if re.compile(r",").search(value):  # if it split with ',', then
                value = re.compile(r",").sub(
                    " ", value)  # substitute ',' with ' '
            value0 = value.split()
            value1 = []
            # type conversion
            if re.compile(r"[.eE]").search(value):  # if float type,
                for val in value0:
                    if re.compile(r"[*]").search(val):
                        res = val.split("*")
                        n = int(res[0])
                        for t in range(0, n):
                            value1.append(float(res[1]))
                    else:
                        value1.append(float(val))
            else:                                  # integer
                for val in value0:
                    if re.compile(r"[*]").search(val):
                        res = val.split("*")
                        n = int(res[0])
                        for t in range(0, n):
                            value1.append(int(res[1]))
                    else:
                        value1.append(int(val))
            value = value1[:]

        return variable, value

    #####################################################################
    def __updateElements__(self, variable, value, dict):
        """
        Update special assignments for single element. For example, 'var(3)=3.0'.
        Before calling this routine, 'var(3)' and 'var' were considered as distinct
        different variables. 
        """
        varlist = dict.keys()
        if re.search(r"[(][0-9]+?[)]", variable):  # for accessing 1-d element
            varname = re.match(r"[a-zA-Z0-9_]+?(?=[(])", variable).group()
            varindx = int(variable[len(varname)+1:-1])

            if (varname in varlist):
                val = dict[varname]
                nlen = len(val)
                if nlen < varindx:  # means that accessing non-existing element
                    ntmp = varindx-nlen
                    for t in range(0, ntmp):
                        if(type(val[0]) == type(2)):
                            val.append(0)
                        else:
                            val.append(0.0)
                #val[varindx-1] = value[0]
                n = len(value)
                val[varindx-1:varindx-1+n] = value[:]
                dict[varname] = val[:]

                dict["__sequence__"].remove(varname)
                dict["__sequence__"].append(varname)

            else:  # means that it is new variable
                val = []
                for t in range(0, varindx-1):
                    if(type(value[0]) == type(2)):
                        val.append(0)
                    else:
                        val.append(0.0)
                # val.append(value[0])
                for v in value:
                    val.append(v)
                dict[varname] = val[:]

                dict["__sequence__"].append(varname)

        else:  # if trivial variable or multi-dimension
            if (variable in varlist):
                val = dict[variable]
                if len(val) < len(value):
                    dict[variable] = value[:]
                else:
                    dict[variable][:len(value)] = value[:]

                dict["__sequence__"].remove(variable)
                dict["__sequence__"].append(variable)
                if "(" in variable:  # multi-dimension assignment
                    dict["__look__"].remove(variable)
                    dict["__look__"].append(variable)
            else:
                dict[variable] = value[:]

                dict["__sequence__"].append(variable)
                if "(" in variable:  # multi-dimension assignment
                    dict["__look__"].append(variable)

        return dict

    #####################################################################
    def write(self, fname, nmlname="", status="w", maxCol=72, indent=2, split=" "):
        """
        Write namelist dictionary to a given file. If 'nmlname' is given, 
        then it will print out given namelist block to file 'fname'. If not,
        it will print out all namelist blocks. 'maxCol' and 'indent' are
        optionally arguments for better formatting.

        INPUTS:
          fname      : file name for saving
          nmlname    : specific name of namelist block
          status     : file openning status. "w"(new), "a"(append) available
          maxCol     : maximum column number for fancy formatting
          indent     : indentation size for fancy formatting
          split      : split symbol between each values.
        """
        if not ((status == "w") or (status == "a")):
            print("[Error] in %s.write() : Wrong arguments'" % (__name__))
            return

        try:
            f = open(fname, status)
        except:
            print("[Error] in %s.write() : File cannot created" % (__name__))
            return

        lines = []

        if(nmlname == ""):  # All namelist blocks will be printed
            if(self.head != ""):
                lines.append(self.head[:])
            for k, v in self.namelist.items():
                lines.append("&"+k+"\n")
                lines += self.__namelist2str__(v, maxCol, indent, split)
                lines.append("/\n\n")
            if(self.tail != ""):
                lines.append(self.tail[:])

        else:  # One particular namelist block will be printed
            if self.case:
                if self.case.lower() == "upper":
                    nmlname = nmlname.upper()
                if self.case.lower() == "lower":
                    nmlname = nmlname.lower()
            try:
                nmls = self.namelist[nmlname]
            except:
                print("[Error] in %s.write() : Not defined namelist name" %
                      (__name__))

            lines.append("&"+nmlname+"\n")
            lines += self.__namelist2str__(nmls, maxCol, indent, split)
            lines.append("/\n\n")

        f.writelines(lines)
        f.close()

    #####################################################################
    def __namelist2str__(self, nml, maxCol=72, indent=3, split=" "):
        """
        Convert a namelist dictionary to string lists

        INPUTS:
          nml        : namelist dictionary. This must be one namelist block, 
                       so its keys are variable names and its values are real
                       data.
          maxCol     : maximum column number for fancy formatting
          indent     : indentation size for fancy formatting
          split      : split symbol between each values.
        """
        import re

        space = " "*indent  # indentation
        nmlStr = []
        for name, value in nml.items():
            data = value[:]
            line0 = space+name+" = "
            iempty = False
            while (not iempty):
                if (data == []):
                    nmlStr.append(line0+"\n")
                    iempty = True
                else:
                    n0 = len(line0)
                    n1 = len(str(data[0])+split)
                    if (n0+n1 > maxCol):
                        nmlStr.append(line0+split+"\n")
                        line0 = space*2
                    else:
                        if type(data[0]) == type(""):  # string type
                            line0 += "'" + str(data[0]) + "'" + split
                        elif type(data[0]) == type(True):  # Boolean
                            if data[0] == True:
                                line0 += ".true." + split
                            if data[0] == False:
                                line0 += ".false." + split
                        else:  # numeric type
                            line0 += str(data[0]) + split

                        if len(data) >= 2:
                            data = data[1:]
                        else:
                            data = []

        return nmlStr

class Data(object):
    def __init__(self):
        pass

def get_east_data(shot):
    turnfc = np.array((140, 140, 140, 140, 140, 140, 248, 248, 60, 60 ,32, 32))
    nfl = 35
    nbp = 38
    nfc = 12
    nip = 1
    mdsdata = Data()
    # fl
    mdsdata.fl = []
    for i in range(nfl):
        sig = 'PCFL%d'%(i+1)
        sig_data = getDataLocal.getDataTime (shot, sig)[0]
        mdsdata.fl.append(sig_data)
    # bp
    mdsdata.bp = []
    for i in range(nbp):
        if i < 30:
            sig = 'PCBPV%dT'%(i+1)
        else:
            sig = 'PCBPL%dT'%(i+1-30)
        sig_data = getDataLocal.getDataTime(shot, sig)[0]    
        mdsdata.bp.append(sig_data)
    # ifc that is PF
    mdsdata.ifc = []
    for i in range(nfc):
        if i<8:
            sig = 'PCPF%d'%(i+1)
        else:
            sig = 'PCPF%d'%(i+3)
        sig_data = getDataLocal.getDataTime(shot, sig)[0]
        # print('the mdsdat PF for i is {} on line 930 in file writek_k'.format(sig_data))
        mdsdata.ifc.append(sig_data * turnfc[i])   

    # IP
    ip_data_time = getDataLocal.getDataTime(shot, "PCRL01")
    mdsdata.ip = [ip_data_time[0]]
    mdsdata.tmds = ip_data_time[1]
    
    print('the mdsdata.ip for PCRL01 is {} on line 938 in file writek_k'.format(mdsdata.ip))
    print('the mdsdata.ip for time is {} and the len is {} on line 938 in file writek_k'.format(mdsdata.tmds,len(mdsdata.tmds)))
    
    # it
    it = getDataLocal.getDataTime(shot, "sysdrit")[0]
    ittime = getDataLocal.getDataTime(shot, "sysdrit")[1]
    # print('the mdsdata.it for sysdrit is {} on line 938 in file writek_k'.format(it))
    # print('the mdsdata.it for time is {} and the len is {} on line 938 in file writek_k'.format(ittime,len(ittime)))
    idx, = np.where(np.abs(it)>1000)
    if idx.size:
        # it == the mean for who >1000
        mdsdata.it = np.mean(it[idx])
    else:
        if shot > 96915:
            it = getDataLocal.getDataTime(shot, "TFP")[0]
        elif (shot > 65321 and shot < 75976):
            it = getDataLocal.getDataTime(shot, "FOCS4")[0]
            ittime = getDataLocal.getDataTime(shot, "FOCS4")[1]
            print('the mdsdata.it for FOCS4 is {} on line 938 in file writek_k'.format(it))
            print('the mdsdata.it for time is {} and the len is {} on line 938 in file writek_k'.format(ittime,len(ittime)))            
        else:
            it = getDataLocal.getDataTime(shot, "FOCS_IT")[0]
        idx, = np.where(np.abs(it)>1000)
        if idx.size:
            mdsdata.it = np.mean(it[idx])
        else:
            print('Waning: cannot get the IT current, set as 8 kA.')
            print('Though EFIT will be running, the results are incorrect.')
            mdsdata.it = 8000
    return mdsdata

def get_data4efit(shot, times,mdsdata):
    idxfc = np.array((1,3,5,7,9,11,2,4,6,8,10,12))
    mdspath = "/scratch/liuxj/01_work_2022/data/fytok_data/mdsplus"
    # mdsdata = get_east_data(shot)
    # for local:
    # mdsdata = get_eastdata_from_spdb(mdspath,shot)
    # #for remote:
    treename = "pcs_east"
    # mdsdata = get_eastdata_from_spdb_remote(treename,shot)
    print('the mdsdat flux_loop is {} on line 961'.format(mdsdata.fl))
    print('the mdsdat PF is {} on line 962'.format(mdsdata.ifc))
    print('the mdsdat IP is {} on line 964'.format(mdsdata.ip))
    print('the mdsdat IT is {} on line 965'.format(mdsdata.it))
    print('the mdsdat tmds is {} on line 984'.format(mdsdata.tmds))
    idxtemp = []
    for ts in times:
        tindex = np.argmin(np.abs(mdsdata.tmds-ts))
        idxtemp.append(tindex)
    print('the idxtemp  is {} on line 989'.format(idxtemp))
    # make small average to avoid the sample problem
    ndelta = 1
    efitdata = Data()
    efitdata.coils = []
    efitdata.expmp2 = []
    efitdata.plasma = []
    efitdata.brsp = []
    for k in range(times.size):
        t1 = idxtemp[k]-ndelta
        t2 = idxtemp[k]+ndelta
        fl = np.zeros(len(mdsdata.fl))
        for i in range(len(mdsdata.fl)):
            # 35
            fl[i] = np.mean(mdsdata.fl[i][t1:t2]) / (2.0 * np.pi)
        efitdata.coils.append(fl)
        bp = np.zeros(len(mdsdata.bp))
        for i in range(len(mdsdata.bp)):
            bp[i] = np.mean(mdsdata.bp[i][t1:t2])
        efitdata.expmp2.append(bp)
        ip = np.zeros(len(mdsdata.ip))
        for i in range(len(mdsdata.ip)):
            print('the len of mdsdat ip is {} on line 1011'.format(len(mdsdata.ip)))
            ip[i] = np.mean(mdsdata.ip[i][t1:t2])
            print('the mdsdat ip is {} on line 1012'.format(ip))
        print('the mdsdat ip is {} on line 1012'.format(ip))
        efitdata.plasma.append(ip)
        ifc = np.zeros(len(mdsdata.ifc))
        print('the len of ifc is {}'.format(len(ifc)))
        for i in range(len(mdsdata.ifc)):
            ifc[i] = np.mean(mdsdata.ifc[idxfc[i]-1][t1:t2])
        efitdata.brsp.append(ifc) # new order of pf coils used in EFIT
    efitdata.btor = mdsdata.it*1.7/(4086*1.85) # 1 tesla@r=1.7m with 4086A in IT coils
    print('the mdsdat coils is {} on line 965'.format(efitdata.coils))
    print('the mdsdat brsp is {} on line 965'.format(efitdata.brsp))
    print('the mdsdat plasma is {} on line 965'.format(efitdata.plasma))
    print('the mdsdat btor is {} on line 965'.format(efitdata.btor))
    return efitdata


def writek(
    shot:int, 
    times:np.array, 
    snap_file:Optional[str]=None,
    mdsdata:dict=None,
):
    """  Write tokamak k file for efit reconsturction.
    Args:
        shot (int): shot number of experiment
        times (List[float]): selected times
    """
    print('the shot is {} and the times is {} on line 1041'.format(shot,times))
    ntslice = times.size
    efitdata = get_data4efit(shot, times,mdsdata)
    
    s = Namelist(snap_file)
    print('the snap_file is {}'.format(snap_file))
    for i in range(ntslice):
        s['in1']['coils'] = efitdata.coils[i]
        s['in1']['expmp2'] = efitdata.expmp2[i]
        s['in1']['brsp'] = efitdata.brsp[i]
        s['in1']['plasma'] = efitdata.plasma[i]
        s['in1']['ishot'] = [shot]
        s['in1']['itime'] = [np.round(times[i]*1000)]
        s['in1']['btor'] = [efitdata.btor]
        #kfile = 'k%d.%d'%(shot, s['in1']['itime'][0])
        sshot = str(shot).zfill(6)
        stime = str(int(s['in1']['itime'][0])).zfill(5)
        kfile = 'k' + sshot + '.' + stime
        s.write(kfile)
    print('Done!')

def update_kfile(
    shot: int,
    old_kfile: str,
    update_data: dict,
    new_kfile: Optional[str] = None,
):
    """  update writek file by pred data dict.
    Args:
        shot (int)
    """
    snap_filepath = "/gpfs/scratch/chgwang/Papers/private_modules/EFIT_tools/snap_files/"
    if (shot <= 44326 and shot > 4774):
        snap_file = snap_filepath + "snap.nam_12"
    elif (shot > 44326 and shot <= 52804):
        snap_file = snap_filepath + "snap.nam_14"
    elif (shot > 52804 and shot <= 96915):
        snap_file = snap_filepath + "snap.nam_15"
    elif (shot > 96915):
        snap_file = snap_filepath + "snap.nam_21"
    else:
        print("no such shot")
        return
    old_kfile = str(old_kfile)
    s = Namelist(snap_file)
    s.read(filename=old_kfile)
    for k, v in update_data.items():
        s["in1"][k] = v
    if new_kfile == None:
        s.write(old_kfile)
    else:
        new_kfile = str(new_kfile)
        s.write(new_kfile)


if __name__ == "__main__":
    old_kfile = "/gpfs/scratch/chgwang/Papers/magneticRecon_efficient/2nd/DataBase/k067274.27400"
    shot = 67274
    update_dict = {}
    update_kfile(shot, old_kfile, update_dict)
