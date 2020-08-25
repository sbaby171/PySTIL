# PySTIL
*(The module is still in beta stage)*
* An open source python module for reading an writing STIL files. 

* It has two processing modes; one for scripting and another for command line interaction. 

* The module provides users with the ability to extact block and statement information from a given STIL via a standard processing and API. 

* Processing is based on the IEEE Std. 1450-1999 and its subsequent extensions. 

**Note**: the term 'parse' here is to be used as in its technical form. That is to say, it describes the completion lexical and semantic analysis. *It is the stage that transforms the information from the STIL file into the PySTIL object's instances*. 

## Design notes: 

* The default processing is to find the start and stop character locations for all the top-level statements or blocks. Then based on the user's query, this along with the file locations will be looked up and parsed. This is mainly done to save runtime  memory requirements, especially for the possible usages of Include statements.  

* It is possible to parse the entire STIL from the beginning as well. 

* Processing and environment considerations of the following topics shall be made: 
  -  OS platform: Windows and Linux
  - Text processing & Gzip Processing
  - Read and Write of STIL files
  - Usage of `Includes`

* If multiple variables are defined within a single Spec/Category block, the 
first definition is kept and all other are ignored. 







## Testing: 
The unit tests are implemented using pythons `unittest` module. 

**How to run testing**: 
``` bash
> python -m unittest discover .\tests\unit\ -v
```



