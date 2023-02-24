# Aggregator
Aggregator for automatic scan results

## Concepts
**In order for this tooling to be useful to you, you need to integrate it with your scan tooling**  
*(See AggregatorNet for .Net bindings)*

The Aggregator is aware of several components.
* Tools
* Scans
* Subjects
* ScanResults (hereafter results)

### Tools
A tool that wants to submit results to the Aggregator must first register itself through the API.
This allows scans, subjects and results to be linked to which tool submitted them

### Scans
When a tool starts a scan it needs to create a new scan in the api and submit all results in that new scan
At the end of the scan the scan should be marked as ended through the api.
Results from the scan will be grouped into the scan.

### Subjects
A subject is any object that the scanning tool operates on.
This could be a specific file, a specific URL or specific host.

Subjects contain hard and soft hashes for matching.
If a subject being submitted is a duplicate, as identified by the hard hash, it won't be added again and the API will return the existing  
subjects id.
If a subject being submitted is a match, as identified by the soft hash, it will be added as a new subject, but will be correlated to all other  
subjects with the same soft hash.

### Results
A scan result is an individual data point that a scanning tool has generated for a subject.
It belongs to a subject, a scan and a tool.

Results contain hard and soft hashes for matching.
If a result being submitted is a duplicate, as identified by the hard hash, it will be added to the scan only as a duplicate result.
If a result being submitted is a match, as identified by the soft hash, it will be added as a separate result, but will be automatically correlated  
to existing results.
The GUI allows to transfer all assessments of soft matches to all results of a scan.

### Hard hashes
When a subject or result is submitted, it MUST be submitted with a hash that should (except for collisions)  
determine if two subjects or results are identical.

These hashes are referred to as hard hashes throughout the tool, because they provide a hard criterion for correlating two subjects or results.

### Soft hashes
When a subject or results is submitted, it MUST be sumitted with a hash that should (except for collisions)  
determine that two subjects or two results are similiar in some way.

These hashes are referred to as soft hashes throughout the tool, because they provide a soft criterion for correlating two subjects or results.

## Setup
* Set up database with dedicated user, set connection string in `credential_export`
* Change secret in `credential_export`
* create virtualenv and install requirements.
* Run db_init.sh
* Run launch.sh
* Open localhost:5000 in your browser and create admin user account

## Deploy
If you plan to use this in a production environment please follow best practices for how to deploy a flask app properly.