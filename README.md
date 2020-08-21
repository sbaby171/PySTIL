# PySTIL
A module to read and write STIL files.


## Design notes: 

* If multiple variables are defined within a single Spec/Category block, the 
first definition is kept and all other are ignored. 







## Testing: 
The unit tests are implemented using pythons `unittest` module. 

**How to run testing**: 
``` bash
> python -m unittest discover .\tests\unit\ -v
```


## TODOs: 
* Establish to two variation of parsing: track char-index, and full tokenization. 


