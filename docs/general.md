# Aggregator
Aggregator for automatic scan results

## Concepts
**In order for this tooling to be useful to you, you need to integrate it with your scan tooling**  

The Aggregator is aware of several components.
* Tools
* Scans
* Subjects
* Properties
* ScanResults (hereafter results)
* Tags

The most relevant ones to understand are **Subjects** and **Results**

### Tools
A tool that wants to submit results to the Aggregator must first register itself through the API.
This allows scans, subjects and results to be linked to which tool submitted them

### Scans
When a tool starts a scan it needs to create a new scan in the api and submit all results in that new scan
At the end of the scan the scan should be marked as ended through the api.
Results from the scan will be grouped into the scan.

### Subjects
A **subject** is any object that the scanning tool operates on.
This could be a **specific file**, a **specific directory** or **specific host**.

Subjects contain properties which are used as a basis to correlate `results` and identify similar or duplicate ones.
Subjects can **optionally** define a `parent` subject allowing tree-like dependencies to be modeled.

### Properties
A `property` is a value that describes a property of a `subject` or `result`.
Each property has a `value` and a `kind` that describes what kind of property it is/what the value means.
*If you've used an earlier version of this tool, think of properties as more fine grained soft hashes.*

Examples would be `the path to a file subject`, `the name of a function`, `the signature of a function`, `the code or a hash of the code of the function`.
These `properties` are used to group together `results` and remove duplicates.

### Results
A `scan result` is an individual **data point** or **finding** that a scanning tool has generated for a `subject`.  
It belongs to a **subject**, a scan and a tool.  

Results contain hard and soft hashes for matching.
If a result being submitted is a duplicate, as identified by the hard hash, it will be added to the scan only as a duplicate result.
If a result being submitted is a match, as identified by the soft hash, it will be added as a separate result, but will be automatically correlated  
to existing results.
The GUI allows to transfer all assessments of soft matches to all results of a scan.

### Tags
A `tag` is a named marker that can be attached to `subject`s and `result`s.  
They are meant to enable easily recognizable classification of both `subject`s and `result`s.

A `tag` has a `color` and a `short name`, and optionally a `long name` and a `description`.