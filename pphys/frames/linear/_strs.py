import re

import numpy

class strs(numpy.ndarray):
    """It is a flat subclass of numpy.ndarray that includes null entries.
    If null is not defined or is None, zero length string is set as sentinel value."""

    def __new__(cls,vals,null=None):
        """
        vals    : flat list
        null    : null str, default is ""
        """

        null = "" if null is None else null

        vals = strs.adopt(vals,null)

        item = numpy.asarray(vals,dtype='str_').view(cls)

        item._null = str(null)

        return item

    def __array_finalize__(self,item):

        if item is None: return

        self._null = getattr(item,'_null',"")

    def __repr__(self):

        parent = super().__repr__()

        return parent.replace(f"'{self.null}'",'null')

    def __str__(self):

        parent = super().__str__()

        return parent.replace(f"'{self.null}'",'null')

    def __setitem__(self,key,value):

        vals = strs(value,null=self.null)

        super().__setitem__(key,vals)

    def __getitem__(self,key):

        vals = super().__getitem__(key)

        if isinstance(key,int):
            return strs(vals,null=self.null)
        else:
            return vals

    def maxchar(self):
        """It returns the maximum character count in the array."""

        charsize = numpy.dtype(f"{self.dtype.char}1").itemsize
        
        return int(self.dtype.itemsize/charsize)

    def maxcharstr(self):
        """It returns the string with maximum number of characters."""

        return max(self.tolist(),key=len)

    def replace(self,old=None,new=None,method="upper"):
        """It replaces old with new. If old is not defined, it replaces nones.
        If new is not defined, it uses upper or lower values to replace the olds."""

        if old is None:
            conds = self.isnull
        else:
            conds = self == old

        if new is None:

            if method=="upper":
                for index in range(self.size):
                    if conds[index]:
                        self[index] = self[index-1]
            elif method=="lower":
                for index in range(self.size):
                    if conds[index]:
                        self[index] = self[index+1]
        else:

            self[conds] = new

    def ptypes(self):

        return

    """ADVANCED METHODS"""

    def sort(self,reverse=False,return_indices=False):
        
        sort_index = numpy.argsort(self.vals)

        if reverse:
            sort_index = numpy.flip(sort_index)

        if return_indices:
            return sort_index
        else:
            return self[sort_index]

    def filter(self,keywords=None,regex=None,return_indices=False):
        
        if keywords is not None:
            match = [index for index,val in enumerate(self.vals) if val in keywords]
            # numpy way of doing the same thing:
            # kywrd = numpy.array(keywords).reshape((-1,1))
            # match = numpy.any(datacolumn.vals==kywrd,axis=0)
        elif regex is not None:
            pttrn = re.compile(regex)
            match = [index for index,val in enumerate(self.vals) if pttrn.match(val)]
            # numpy way of doing the same thing:
            # vectr = numpy.vectorize(lambda x: bool(re.compile(regex).match(x)))
            # match = vectr(datacolumn.vals)

        if return_indices:
            return match
        else:
            return self[match]

    def flip(self):

        datacolumn = copy.deepcopy(self)

        datacolumn.vals = numpy.flip(self.vals)

        return datacolumn
            
    def unique(self):

        datacolumn = copy.deepcopy(self)

        datacolumn.vals = numpy.unique(self.vals)

        return datacolumn
        
    def toints(self):

        # line = re.sub(r"[^\w]","",line) # cleans non-alphanumerics, keeps 0-9, A-Z, a-z, or underscore.

        func = numpy.vectorize(strs._str2int,otypes=[int],excluded=["none_str","none_int","regex"])

        # dnone = self.nones.todict("str","int")
        # regex = r"[-+]?\d+\b" if regex is None else regex
        # datacolumn.vals = str2int(datacolumn.vals,regex=regex,**dnone)

        return func(array)

    def tofloats(self):

        # dnone = self.nones.todict("str","float")
        # regex = r"[-+]?[0-9]*\.?[0-9]+" if regex is None else regex
        # datacolumn.vals = str2float(datacolumn.vals,regex=regex,**dnone)
        # datacolumn._valsunit()

        func = numpy.vectorize(strs._str2float,otypes=[float],excluded=["none_str","none_float","sep_decimal","sep_thousand","regex"])

        return func(self)

    def _tostrs(self):

        # dnone = self.nones.todict("str")
        # datacolumn.vals = str2str(datacolumn.vals,regex=regex,**dnone)

        func = numpy.vectorize(strs._str2str,otypes=[str],excluded=["none_str","regex","fstring"])

        return func(self)

    def tostrs(self,fstring=None,upper=False,lower=False,zfill=None):
        """It has more capabilities than str2str on the outputting part."""

        if fstring is None:
            fstring_inner = "{}"
            fstring_clean = "{}"
        else:
            fstring_inner = re.search(r"\{(.*?)\}",fstring).group()
            fstring_clean = re.sub(r"\{(.*?)\}","{}",fstring,count=1)

        vals_str = []

        for val,none_bool in zip(self.vals.tolist(),self.isnone):

            if none_bool:
                vals_str.append(self.nones.str)
                continue

            text = fstring_inner.format(val)

            if zfill is not None:
                text = text.zfill(zfill)

            if upper:
                text = text.upper()
            elif lower:
                text = text.lower()

            text = fstring_clean.format(text)

            vals_str.append(text)

        vals_str = numpy.array(vals_str,dtype="str")

        datacolumn = copy.deepcopy(self)

        datacolumn = datacolumn.astype("str")

        datacolumn.vals = vals_str

        return datacolumn

    def todates(self):

        func = numpy.vectorize(strs._str2datetime64,otypes=[numpy.datetime64],excluded=["none_str","none_datetime64","unit_code","regex"])

        return func(self)

    def todatetimes(self):

        dnone = self.nones.todict("str","datetime64")
        datacolumn.vals = str2datetime64(datacolumn.vals,regex=regex,**dnone)

    def __add__(self,other):
        """Implementing '+' operator."""

        if isinstance(other,str):
            other = [other]

        if not isinstance(other,strs):
            other = strs(other)

        return strs(numpy.char.add(self,other))

    def __radd__(self,other):
        """Implementing right '+' operator."""

        if isinstance(other,str):
            other = [other]

        if not isinstance(other,strs):
            other = strs(other)

        return strs(numpy.char.add(self,other))

    def replace(self,new=None,old=None,method="upper"):
        """It replaces old with new. If old is not defined, it replaces nones.
        If new is not defined, it uses upper or lower values to replace the olds."""

        if old is None:
            conds = self.isnone
        else:
            conds = self.vals == old

        if new is None:

            if method=="upper":
                for index in range(self.vals.size):
                    if conds[index]:
                        self.vals[index] = self.vals[index-1]
            elif method=="lower":
                for index in range(self.vals.size):
                    if conds[index]:
                        self.vals[index] = self.vals[index+1]
        else:
            self.vals[conds] = new

    def split(self,delimiter=None,maxsplit=None):

        if maxsplit is None:
            maxsplit = numpy.char.count(self,delimiter).max()

        rows = []

        for index,value in enumerate(self):

            row = value.tolist().split(delimiter,maxsplit=maxsplit)

            if maxsplit+1>len(row):
                [row.append(datacolumn.nones.str) for _ in range(maxsplit+1-len(row))]

            rows.append(row)

        return [strs(values,null=self.null) for values in numpy.array(rows,dtype=str).T]

    def min(self):

        return min(self.vals[~self.isnone],key=len)

    def max(self):

        return max(self.vals[~self.isnone],key=len)

    def unique(self):

        datacolumn = copy.deepcopy(self)

        datacolumn.vals = numpy.unique(self.vals)

        return datacolumn

    def append(self,other):

        if not isinstance(other,column):
            other = column(other)

        if self.dtype.type is numpy.dtype('int').type:
            if not other.dtype.type is numpy.dtype('int').type:
                other = other.astype('int')
        elif self.dtype.type is numpy.dtype('float').type:
            if not other.dtype.type is numpy.dtype('float').type:
                other = other.astype('float')
            other = other.convert(self.unit)
        elif self.dtype.type is numpy.dtype('str').type:
            if not other.dtype.type is numpy.dtype('str').type:
                other = other.astype('str')
        elif self.dtype.type is numpy.dtype('datetime64').type:
            if not other.dtype.type is numpy.dtype('datetime64').type:
                other = other.astype('datetime64')
                
        dataarray = numpy.append(self.vals,other.vals)
        
        super().__setattr__("vals",dataarray)

    @property
    def null(self):

        return self._null

    @property
    def isnull(self):
        """It return numpy bool array, True for null and False for integer."""
        return numpy.equal(self.view(numpy.ndarray),self.null)

    @property
    def issorted(self):

        return numpy.all(self.vals[:-1]<self.vals[1:])

    @staticmethod
    def adopt(vals,null):
        """
        vals    : flat list
        null    : null str
        """

        null = str(null)

        for index,value in enumerate(vals):

            if isinstance(value,str):
                continue

            vals[index] = null if value is None else str(value)

        return vals

    @staticmethod
    def arange(*args,start='A',stop=None,step=1,size=None,dtype=None):

        kwargs = setargs(*args,**kwargs)

        if start is not None:
            if len(start)>5:
                raise TypeError(f'tried excel like letters and failed because of size of start {len(start)}!')
            elif not all([char in string.ascii_letters for char in start]):
                raise TypeError(f'tried excel like letters and failed because of {start=}!')
            start = start.upper()

        if stop is not None:
            if len(stop)>5:
                raise TypeError(f'tried excel like letters and failed because of size of stop {len(stop)}!')  
            elif not all([char in string.ascii_letters for char in stop]):
                raise TypeError(f'tried excel like letters and failed because of {stop=}!!')
            stop = stop.upper()

        if size is not None:
            if size>1000_000:
                raise TypeError(f'tried excel like letters and failed because of {size=}!')

        if isinstance(dtype,str):
            dtype = numpy.dtype(str)

        def excel_column_headers():
            n = 1
            while True:
                yield from (
                    ''.join(group) for group in itertools.product(
                        string.ascii_uppercase,repeat=n
                        )
                    )
                n += 1

        for start_index,combo in enumerate(excel_column_headers()):
            if start==combo:
                break

        if size is None:
            if stop is None:
                raise ValueError("stop value must be provided!")
            for stop_index,combo in enumerate(excel_column_headers(),start=1):
                if stop==combo:
                    break
            _array = numpy.array(list(itertools.islice(excel_column_headers(),stop_index)))[start_index:stop_index]
            _array = _array[::step]
        else:
            _array = numpy.array(list(itertools.islice(excel_column_headers(),start_index+size*step)))[start_index:]
            _array = _array[::step]

        if dtype is not None:
            return _array.astype(dtype)
        else:
            return _array

    @staticmethod
    def build(*args,phrases=None,repeats=None,size=None,dtype=None):

        if isinstance(dtype,str):
            dtype = numpy.dtype(dtype)

        if len(args)==0:
            if phrases is None:
                phrases = " "
            if repeats is None:
                repeats = 1

            iterator = _any2column.toiterator(phrases,repeats,size=size)

            _array = numpy.array(["".join([name]*num) for name,num in iterator])

        elif len(args)==1:
            _array = array1d(args[0],size)
        else:
            raise TypeError("Number of arguments can not be larger than 1!")

        if dtype is None:
            return _array
        else:
            return _array.astype(dtype)

def ptype(string:str):

    for attempt in (float,parser.parse):

        try:
            typedstring = attempt(string)
        except:
            continue

        return type(typedstring)

    return str

def toint(string:str,none_str:str="",none_int:int=-99_999,regex:str=None) -> int:
    """It returns integer converted from string."""

    # common expression for int type is r"[-+]?\d+\b"

    if string==none_str:
        return none_int

    if regex is None:
        return int(string)

    match = re.search(regex,string)

    if match is None:
        return none_int

    string = match.group()
            
    return int(string)

def tofloat(string:str,none_str:str="",none_float:float=numpy.nan,sep_decimal:str=".",sep_thousand:str=",",regex:str=None) -> float:
    """It returns float after removing thousand separator and setting decimal separator as full stop."""

    # common regular expression for float type is f"[-+]?(?:\\d*\\{sep_thousand}*\\d*\\{sep_decimal}\\d+|\\d+)"

    if string.count(sep_decimal)>1:
        raise ValueError(f"String contains more than one {sep_decimal=}, {string}")

    if string.count(sep_thousand)>0:
        string = string.replace(sep_thousand,"")

    if sep_decimal!=".":
        string = string.replace(sep_decimal,".")

    if string==none_str:
        return none_float

    if regex is None:
        return float(string)

    match = re.search(regex,string)

    if match is None:
        return none_float

    string = match.group()
    
    return float(string)

def tostr(string:str,none_str:str="",regex:str=None,fstring:str=None) -> str:

    fstring = "{:s}" if fstring is None else fstring

    if regex is None:
        if string==none_str:
            return fstring.format(none_str)
        else:
            return fstring.format(string)

    else:
        match = re.search(regex,string)

        if match is None:
            return fstring.format(none_str)
        else:
            return fstring.format(match.group())

def todates(string:str,null_str:str="",null_date:numpy.datetime64=numpy.datetime64('NaT'),unit_code:str="D",regex:str=None) -> numpy.datetime64:

    return

def todatetimes(string:str,null_str:str="",null_datetime:numpy.datetime64=numpy.datetime64('NaT'),unit_code:str="D",regex:str=None) -> numpy.datetime64:

    if regex is not None:
        match = re.search(regex,string)

        if match is None:
            return null_datetime

        string = match.group()

    if string==null_str:
        return null_datetime

    elif string=="now":
        now = numpy.datetime64(datetime.datetime.now(),unit_code)
        return now

    elif string=="today":
        today = numpy.datetime64(datetime.datetime.today(),unit_code)
        return today

    elif string=="yesterday":
        today = numpy.datetime64(datetime.datetime.today(),unit_code)
        return today-numpy.timedelta64(1,'D')

    elif string=="tomorrow":
        today = numpy.datetime64(datetime.datetime.today(),unit_code)
        return today+numpy.timedelta64(1,'D')

    try:
        return numpy.datetime64(parser.parse(string),unit_code)

    except parser.ParserError:
        return null_datetime

if __name__ == "__main__":

    firsts = strs(["cavid","aydan","mehru"])
    
    lasts = strs(["shiriyev","shiriyeva","shiriyeva"])

    # print(strs(["    "]))

    # firsts = firsts + " is my name"
    # firsts = firsts + " "

    print(firsts+" "+lasts)
    # print(" "+firsts)

    # print(firsts+" "+lasts)