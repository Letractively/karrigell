

# Introduction #

A dynamic web application presents data inside an HTML document. The best way to generate HTML is to use the HTMLTags module


# Basics #

HTMLTags defines a class for each valid HTML tag (including HTML5), in uppercase letters : for instance, there are classes <tt>HTML, HEAD, BODY, TABLE, B, I</tt>, etc.

These classes are initiated with a value, and optional keyword arguments :

```
DIV(content,key1=value1,key2=value2...)```

The `__str()__` method of these classes returns the HTML code matching the tag name and arguments. For HTML attributes without arguments, such as the MULTIPLE argument of SELECT tags, the constructor must be called with the value True :

```
SELECT(name="foo",multiple=True)```

# Nesting tags #

The content argument of a tag can be another instance of an HTMLTags class. For instance :

```
title = TITLE("FC Barcelona Home Page")
head = HEAD(title)
print(head)
>>> <HEAD><TITLE>FC Barcelona Home Page</TITLE></HEAD>
```

Tags support addition :

```
line = TD("email")+TD(INPUT(name="email"))
print(line)
>>> <TD>email</TD><TD><INPUT name="email"></TD>
```

and multiplication

```
line = TH("&nbsp;")*3
print(line)
>>> <TH>&nbsp;</TH><TH>&nbsp;</TH><TH>&nbsp;</TH>
```

The operator <= means "add child", you can use it to build complex HTML documents :

```
body = BODY()
body <= H2("Home page")
table = TABLE(Class="players")
table <= TR(TH("Name")+TH("Birth"))
for name,birth in [("Andres Iniesta","1984-05-11"),
    ("Lionel Messi","1987-06-24")]:
    table <= TR(TD(name)+TD(birth))
body <= table
```

# The SELECT tag #

This tag has additional methods to build it from a list, and to select  options

### from\_list(_items,`[`use\_content`]`_) ###
Builds the OPTION tags inside the SELECT tag, using the list _items_. Each option matches an element in the list. If _use`_`content_ is set to True, the option value for the n-th item is set to items`[n`] ; if set to False (default), it is set to n. The method returns the SELECT tag itself

### select(_value=v\_arg,content=c\_arg_) ###
Select the options with the specified value or content
If v\_arg is a list, select the options whose value is in the list. Same thing if content is a list

Examples
<table>
<tr>
<th>Python code</th>
<th>generates HTML code</th>
</tr>
<tr>
<td align='top'>
<pre><code>sel = SELECT(name="foo").from_list(["one","two"])<br>
sel.select(value=0)<br>
</code></pre>
</td>
<td align='top'>
<pre><code>&lt;SELECT name="foo"&gt;<br>
&lt;OPTION value="0" SELECTED&gt;one<br>
&lt;OPTION value="1"&gt;two<br>
&lt;/SELECT&gt;<br>
</code></pre>
</td>
</tr>
<tr>
<td>
<pre><code>sel = SELECT(name="foo").from_list(["one","two"])<br>
sel.select(content="two")<br>
</code></pre>
</td>
<td>
<pre><code>&lt;SELECT name="foo"&gt;<br>
&lt;OPTION value="0"&gt;one<br>
&lt;OPTION value="1" SELECTED&gt;two<br>
&lt;/SELECT&gt;<br>
</code></pre>
</td>
</tr>
</table>

# The RADIO and CHECKBOX classes #

These classes are provided for the HTML INPUT tags of types radio and checkbox

The constructor is

### RADIO(_items,`[`values,`[**`attrs`]]`_) ###

It builds a list of INPUT tags, one per item in the list **items**. Each INPUT tag has the attributes **attrs**

If **values** is specified, it must be a list of the same size as **items**. Each INPUT tag value is taken from **values**
If it is not specified, the value is the index in **items**

An instance of RADIO is an iterator on a list of tuples _(value,tag)_ where _value_ is the value in **items**, and _tag_ is the matching INPUT instance

Instances of RADIO and CHECKBOX support the method

### check(_value=arg_) _or_ check(_content=arg_) ###

If the key is **value**, arg is an index (or a list of indices), the method checks the tag(s) at the given index or indices in **items**

If key is **content**, arg is a string (or a list of strings), the method checks the tag(s) whose value is the given string, or in the list of strings

Examples
<table>
<tr>
<th>Python code</th>
<th>generates HTML code</th>
</tr>
<tr>
<td>
<pre><code>r = RADIO(["one","two"],name="foo")<br>
r.check(value=0)<br>
for v,tag in r:<br>
    print(v,tag)<br>
</code></pre>
</td>
<td>
<pre><code>one &lt;input Type="radio" name="foo" value="0" checked&gt;<br>
two &lt;input Type="radio" name="foo" value="1"&gt;<br>
</code></pre>
</td>
</tr>
<tr>
<td>
<pre><code>r = RADIO(["one","two"],[350,18],name="foo")<br>
r.check(content="two")<br>
for v,tag in r:<br>
    print(v,tag)<br>
</code></pre>
</td>
<td>
<pre><code>one &lt;input Type="radio" name="foo" value="350"&gt;<br>
two &lt;input Type="radio" name="foo" value="18" checked&gt;<br>
</code></pre>
</td>
</tr>
</table>

# Editing a tag #

A tag can be manipulated in the same way as a DOM element

It supports the dictionary interface to access the attributes. With the example above, you can add an attribute to the table :

```
table["width"] = "80%"
```

To get a specific tag inside the document tree, use the method

**get(_`*`tags,`**`attrs_)**

> Returns a list of all the tags in the tree below self. _tags_ are tag classes, and _attrs_ are key/values arguments. The method returns the tags of the specified classes that have the specified arguments

In the above example, to get all the TH elements :
```
ths = body.get(TH)
```

# Using HTMLTags in Karrigell scripts #

All the names defined by HTMLTags are present in the execution namespace of Karrigell scripts

Suppose you have a script with this function <tt>index()</tt> :

```
def index():
   return B("Hello world")
```

When a function is executed, the string representation of the return value is sent to the browser. Here, the return value is an instance of the HTMLTags class B ; its string representation is

```
<B>Hello world</B>
```