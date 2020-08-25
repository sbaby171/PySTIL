# PySTIL
(The module is still in beta stage)
An open source python module for reading an writing STIL files. 

It has two processing modes; one for scripting and another for command line interaction. 

The module supplies users with the ability to extact blocks or statements, from a given STIL via a standard processing and API. 

The modules processing is based on the IEEE Std. 1450-1999 and its subsequent extensions. 

**Note**: the term 'parse' here is to be used as in its technical form. That is to say, it is describe the process after lexical analysis and semantic analysis. It is the stage transform the information from the STIL file into the PySTIL object's instances. 

## Design notes: 

* The default processing is to find the start and stop character indexes for all the top-level statements or blocks. Then based on the user's query, the file will be looked up  along with the blocks start/end locations, and parsed. This is done to save memory requirements, especially for the possible usages of Include statements.  

* It is possible to parse the entire STIL from the beginning as well. 

* If multiple variables are defined within a single Spec/Category block, the 
first definition is kept and all other are ignored. 







## Testing: 
The unit tests are implemented using pythons `unittest` module. 

**How to run testing**: 
``` bash
> python -m unittest discover .\tests\unit\ -v
```



