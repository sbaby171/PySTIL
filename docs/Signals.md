


# 6.8 User-defined name characteristics 

"There are several categories of user-defined names in STIL; signal and group
references, WaveformChar references, WaveformTable references, variable references,
UserKeywords, labels, and domain names.

If a user-defined name contains STIL reserved characters or is identical to a STIL
reserved word, then that name shall be quoted in double quotes."


"User-defined names must be declared either unquoted or enclosed in double quotes. 
Once declared, all references to that names shall use the same convention to reference
that name; for instance, the name "Xyz" is always references as "Xyz" (with quotes 
present)."

"Names may not contain a double-quote character."

"Signal or Group names may contain square brackets, with integer values inside, 
at the end of the name string. (See 6.10 for more information)."

- This is so weird, signal or group names can contain square-brackets! 
- No wonder I havent seen much use of the condsense  (..) in STILs that
were going to end up on SmarTest; I dont think SmarTest allows 

## 6.10 Signal an group name characteristics: 

"A set of signals with a common name and numeric index may be expressed using 
a double-period ellipis (..) operator. To use the ellipsis operator, the 
signal names shall be appended with an index number in the square brackets. 
For example, the signals referenced by the statement data\[0..36\] would include 
the range of signals from data\[0\] through data\[36\]. If signal names are quoted (because of
characters used in the name), the quotes occur before the bracketed part of the name; for example,
“a&b”\[0..7\]. This defines signals “a&b”\[0\] through “a&b”\[7\]. The brackets, when present, become part of the name reference, and the values inside the bracket are interpreted as integer values only. For example, the signal data\[0\] is the same as the signal data\[00\], but is not the same as data00. The values may be defined in either ascending (\[0..7\]) or descending (\[7..0\]) order. The square-bracket operation is allowed any place a signal expression may occur. It is allowed as the name of a series of signals in a Signals block, but is not allowed as the name of a group in the SignalGroups block."