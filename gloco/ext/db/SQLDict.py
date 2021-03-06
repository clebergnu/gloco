"""
SQLDict: A helper class for the Python DB API.

This creates a database interface which works pretty much like a
Python dictionary (or shelve). It assumes the necessary tables already
exist.

First, open the underlying database, creating a connection object.
mxODBC is used here, but any SQL-89+ DB API-compliant one should work.
Then use that to create the SQLDict object:

>>> import ODBC
>>> from SQLDict import *
>>> subdb = ODBC.Solid.connect('TCP/IP localhost 1313', 'test', 'test')
>>> db = SQLDict(subdb)

Next, define the tables and columns of interest. Note that is not
necesary to define all columns of a particular table, only those
you need.

>>> db.People = db.Table('PEOPLE', [ 'Name', 'Address', 'City', 'State' ] )

This defines a new member People of db, which describes the table
PEOPLE as having the columns NAME, ADDRESS, CITY, and STATE.
Remember that SQL is case-insensitive and effectively converts all
names to UPPER CASE, unless you use a delimited name, in which case
you would want to specify the columns as ( '"Name"', '"Address"',
... ). The column specification must be a tuple or list. You can
define multiple members which refer to the same table using a
different combination of columns.

Now, define some useful indices for accessing your data.

>>> db.People.Name = Index(['Name'])

This defines an index member to People called Name, which allows
searching by Name. The second argument must be a tuple or list, so
it is possible to key off of several fields simultaneously.

Accessing your data is very similar to using dictionaries. To
retrieve information:

>>> db.People.Name['Bob Dobbs'].fetchone()
('Bob Dobbs', '42 Slack Ln', 'Cleveland', 'OH')

Note that the [] (__getitem__) operation returns a special cursor
with some extended properties; more on that latter.

>>> db.People.loc = db.Index(('City','State'))
>>> db.People.loc['Cleveland','OH'].fetchall()
[('Bob Dobbs', '42 Slack Ln', 'Cleveland', 'OH')
('Drew Carey', '13 Pig St', 'Cleveland', 'OH')]

Suppose you have some objects you'd like to directly load and store
into the database. Assuming a pre-defined Person object:

>>> db.People.dump = dump_person
>>> db.People.load = load_person
>>> db.People.loc['Cleveland','OH'].fetchall()
[<Person instance at 8080c0>, <Person instance at 8080f0>]

Now you have full shelve-type functionality for retreival, aside
from having to do the various fetch methods. The dump method must
accept a single argument (the object to dump) and return a tuple
containing the column data in the same order as when the Table was
defined. The load method must do the same thing in reverse. This
basically accomplishes the same thing as pickling. By default,
dump and load simply return what is passed to them.

Too lazy to write dump and load routines and define all that table
and index stuff? Me too:

>>> class Person(ObjectBuilder):
...     table = "People"
...     columns = ['Name', 'Address', 'City', 'State']
...     update_columns = columns
...     indices = [ ('Name', ['Name']), ('loc', ['City', 'State']) ]
...
>>> Person().register(db)
>>> db.People.loc['Cleveland','OH'].fetchall()
[Person(Name='Bob Dobbs',Address='42 Slack Ln',City='Cleveland',State='OH'),
Person(Name='Drew Carey',Address='13 Pig St',City='Cleveland',State='OH')]

This creates a new Person class with attributes Name, Address, City, and
State. The constructor takes assigns the arguments to the attributes in
the order in which they appear. It also accepts keyword arguments. The
register(db) method creates the table and index members in db. Of course,
you can add your own methods and such. If you need an __init__ method,
make sure you call apply(ObjectBuilder.__init__, (self,)+args, kwargs)
at some point.

To reset the attributes from a dictionary:

>>> p.set_keywords(dict=dict) # error if key not in columns
>>> p.set_keywords(skim=1, dict=dict) # ignores keys not in columns

Updating old information is easy:

>>> p = db.People.Name['Drew Carey']
>>> p.Address = '100 Hog Mountain Rd'
>>> db.People.Name['Drew Carey'] = p

Inserting new info is also easy, but slightly different than what
you might expect:

>>> p2 = Person('Elvis Presley','Graceland','Memphis','TN')
>>> db.People.insert(p2)

An index is unneccesary (and useless) for inserting new records.

Deleting stuff works like you'd think.

>>> del db.People.Name['Elvis Presley']

Note that none of these methods ever commit any data to the database,
so you will have to call db.commit() when appropriate, or otherwise
set the transaction mode.

Sub-queries: Suppose you want to do a sub-query, as in WHERE x IN (
select-statement ) or some other kind of special query conditions. You
can specify this with a WHERE parameter when creating the index. Note
that this string is simply appended onto the part of the clause
generated by the indices. The indices can be left blank for these
purposes. The SELECT member of an index can be useful for generating a
sub-query on another index. The select() and update() methods are also
available for doing weird things.

"""

__version__ = "$Id: SQLDict.py,v 1.2 1999/03/16 05:24:23 adustman Exp $"

from string import join

class SQLDict:

    """SQLDict: An object class which implements something resembling
    a Python dictionary on top of an SQL DB-API database."""

    def __init__(self, db):

	"""Create a new SQLDict object.
	db: an SQL DB-API database connection object"""

	# Most database objects are native C, so they can't be subclassed.
	self.db = db

    def __del__(self):	self.close()

    def close(self):
	try: self.db.close()
	except: pass

    def __getattr__(self, attr):
	# Get any other interesting attributes from the base class.
	return getattr(self.db, attr)



    class _Table:

	"""Table handler for a SQLDict object. These should not be created
	directly by user code."""

	def __init__(self, db, table, columns, updatecolumns=[]):

	    """Construct a new table definition. Don't invoke this
	    directly. Use Table method of SQLDict instead."""

	    self.db = db
	    self.table = table
	    self.columns = columns
	    self.SELECT = "SELECT %s FROM %s " % \
			  (self._columns(columns),
			   self.table)
	    self.INSERT = "INSERT INTO %s (%s)\n    VALUES (%s) " % \
			  (self.table,
			   self._columns(columns),
			   self._values(columns))
	    self.Update(columns)
	    self.DELETE = "DELETE FROM %s " % self.table
	    self.Update(updatecolumns or columns)

	def _columns(self, columns): return join(columns, ', ')

	def _values(self, columns):	return join('?'*len(columns), ', ')

	def _set(self, columns):
	    return join(map(lambda c: "%s = ?" % c, columns), ', ')

	def Update(self, columns):
	    self.UPDATE = "UPDATE %s\n    SET %s " % \
			  (self.table,
			   self._set(columns))
	    self.updatecolumns = columns

	def select(self, i=(), WHERE=''):

	    """Execute a SELECT command based on this Table and Index. The
	    required argument i is a tuple containing the values to match
	    against the index columns. A string containing a WHERE clause
	    should be passed along, but this is technically optional. The
	    WHERE clause must have the same number of value placeholders
	    (?) as there are values in i. Returns a _Cursor object for the
	    matched rows.

	    Usually you don't need to call select() directly; this is done
	    by the indexing operations (Index.__getitem__)."""

	    c = self.cursor()
	    if i: c.execute(self.SELECT+WHERE, i)
	    else: c.execute(self.SELECT+WHERE)
	    return c

	def insert(self, v):

	    """Like select(), but performs an INSERT. Note that there is
	    no WHERE clause on an INSERT."""

	    from types import ListType
	    c = self.cursor()
	    if type(v) is ListType:
		d = map(self.dump, v)
	    else:
		d = self.dump(v)
	    c.execute(self.INSERT, d)
	    return c

	def update(self, v, i=(), WHERE=''):
	    """Like select(), only it does an UPDATE. It is not usually
	    necessary to call this method directly, as it is done by
	    the indexing operations (Index.__setitem__)."""
	    c = self.cursor()
	    v0 = self.updatedump(v)
	    c.execute(self.UPDATE+WHERE, v0+i)
	    return c

	def delete(self, i=(), WHERE=''):
	    """Like select(), only it does an DELETE. It is not usually
	    necessary to call this method directly, as it is done by
	    the indexing operations (Index.__delitem__)."""
	    c = self.cursor()
	    if i: c.execute(self.DELETE+WHERE, i)
	    else: c.execute(self.DELETE+WHERE)
	    return c

	def dump(self, v):
	    """Default method. May be overridden. Must take single value
	    argument, return a tuple compatible with the columns defined
	    for this table."""
	    return v

	def updatedump(self, v):
	    t = self.dump(v)
	    l = []
	    for i in range(len(self.columns)):
		if self.columns[i] in self.updatecolumns: l.append(t[i])
	    return tuple(l)

	def load(self, v):
	    """Default method. May be overridden. Must take a tuple
	    compatible with the columns defined for this table, return
	    something useful."""
	    return v


	class _Index:

	    """Index handler for a _Table object. These should not be created
	    directly by user code."""

	    def __init__(self, table, indices, WHERE):
		i = map(lambda i: "%s = ?" % i, indices)
		self.table = table
		self.WHERE =  "\n    WHERE "+ join(i, ' AND ') + WHERE

	    def __setitem__(self, i=(), v=None):
		"""Update the item in the database matching i
		with the value v."""
		from types import *
		if type(i) == ListType: i = tuple(i)
		elif type(i) != TupleType: i = (i,)
		self.table.update(v, i, WHERE=self.WHERE)

	    def __getitem__(self, i=()):
		"""Select items in the database matching i."""
		from types import *
		if type(i) == ListType: i = tuple(i)
		elif type(i) != TupleType: i = (i,)
		return self.table.select(i, WHERE=self.WHERE)

	    def __delitem__(self, i):
		"""Delete items in the database matching i."""
		from types import *
		if type(i) == ListType: i = tuple(i)
		elif type(i) != TupleType: i = (i,)
		return self.table.delete(i, WHERE=self.WHERE)

	def Index(self, indices=[], WHERE=''):

	    """Create an index definition for this table.

	    Usage: db.table.Index(indices)
	    Where: indices   = tuple or list of column names to key on
		   WHERE     = optional WHERE clause.

	    If the WHERE is specified, this is used in conjunction with
	    the other indices.  """

	    return self._Index(self, indices, WHERE)

	class _Cursor:

	    """A subclass (shadow class?) of a cursor object which knows how to
	    load the tuples returned from the database into a more interesting
	    object."""

	    def __init__(self, db, load):
		self.cursor = db.cursor()
		self.load = load

	    def fetchone(self):
		"""Fetch one object from current cursor context."""
		x = self.cursor.fetchone()
		if x: return self.load(x)
		else: return x # only load if we really got something

	    def fetchall(self):
		"""Fetch all objects from the current cursor context."""
		return map(self.load, self.cursor.fetchall())

	    def fetchmany(self, *size):
		"""Fetch many objects from the current cursor context.
		Can specify an optional size argument for number of rows."""
		return map(self.load, apply(self.cursor.fetchmany, size))

	    def __getattr__(self, attr):
		return getattr(self.cursor, attr)


	def cursor(self):
	    """Returns a new _Cursor object which is load-aware and
	    otherwise behaves normally."""
	    return self._Cursor(self.db, self.load)


    def Table(self, table, columns, updatecolumns=[]):

	"""Add a new Table member.

	Usage: db.Table(tablename, columns)
	Where: tablename  = name of table in database
               columns    = tuple containing names of columns of interest

	       """

	return self._Table(self.db, table, columns, updatecolumns)


class ObjectBuilder:

    """This class lets you build objects for use with SQLDict, and
    for other purposes. To use, define a new class, subclassing
    ObjectBuilder. Define the following items:

    table: Name of table in SQL database.
    columns: List of columns in table.
    updatecolumns: List of columns in table that are updateable.
        Usually it is necessary to define this to avoid referencial
	integrity problems, i.e. avoid updating columns which are
	used as foreign keys.
    special_types: A dictionary where the key is a column name and
        the value is a dbi type. Useful when working with date data.
    indices: A list of tuples. The first part of the tuple is the name
        of the index. The second part is a list of column names.
    """

    table = None
    columns = []
    updatecolumns = []
    special_types = {}
    indices = []

    def __init__(self, *args, **kw):
	"""
	Constructor: Accepts an argument list of values, which are assigned in
        the order specified in columns. Also accepts keyword arguments,
	where the keys are from columns.
	"""

	for k in self.columns: setattr(self, k, None)
	for i in range(len(args)):
	    setattr(self, self.columns[i], args[i])
	self.set_keywords(dict=kw)

    def set_keywords(self, skim=0, dict={}):
	"""
	Assign attributes using keyword arguments. If skim=0 (default),
	keywords not present in columns raises AttributeError. Otherwise,
	the keyword is ignored.
	"""
	for k, v in dict.items():
	    if k in self.columns: setattr(self, k, v)
	    elif not skim: raise AttributeError, k

    def __setattr__(self, key, value):
	try:
	    getattr(self, '_set_'+key)(value)
	except AttributeError:
	    self.__dict__[key] = value

    def __str__(self):
	from string import join
	l0 = "%s(" % self.__class__.__name__
	l = []
	for k in self.columns:
	    l.append("%s=%s" % (k, repr(getattr(self, k))))
	return join([l0, join(l, ','), ')'],'')

    def __repr__(self):
	from string import join
	l0 = "%s(" % self.__class__.__name__
	l = []
	for k in self.columns:
	    l.append("%s" % repr(getattr(self, k)))
	return join([l0, join(l, ','), ')'],'')

    def dump(self):
	l = []
	for k in self.columns:
	    if self.special_types.has_key(k):
		v = self.special_types[k](getattr(self, k))
	    else:
		v = getattr(self,k)
	    l.append(v)
	return tuple(l)

    def register(self, db):
	"""Register into database."""
	t = db.Table(self.table, self.columns, self.updatecolumns)
	loader = lambda t, s=self.__class__: apply(s, t)
	setattr(t, 'dump', self.__class__.dump)
	setattr(t, 'load', loader)
	for indexname, columns in self.indices:
	    setattr(t, indexname, t.Index(columns))
	return t


class MySQLDict(SQLDict):
    
    class _Table(SQLDict._Table):
        
       	def _values(self, columns): return join(["%s"]*len(columns), ', ')

	def _set(self, columns):
	    return join(map(lambda c: "%s = %%s" % c, columns), ', ')

	class _Index(SQLDict._Table._Index):

	    def __init__(self, table, indices, WHERE):
		i = map(lambda i: "%s = %%s" % i, indices)
		self.table = table
		self.WHERE =  "\n    WHERE "+ join(i, ' AND ') + WHERE


