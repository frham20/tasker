# tasker

## Description
Python module to run various tasks

Mainly used to backup stuff on my computer periodically and learning a bit of Python 3.6

## Usage
How to install the package
```
python setup.py install
```

How to use from the command line:
```
python -m tasker MyConfig.json
```

Here's an example of a config file:
```json
{
    "tasks":[ 
        {
            "file-purge":{
                "path":"e:\\Documents\\_archive\\",
                "older_than":"P10D",
                "include":["Documents_.*\\.zip"]
            }
        },
        {
            "archive-create":{ 
                "archive_name":"Documents_${YYYY}_${MM}_${DD}", 
                "dst":"e:\\Documents\\_archive",
                "src":"e:\\Documents", 
                "exclude":[ "\\\\_archive\\\\"]
            }
        },
        { 
            "directory-mirror":{
                "src":"d:\\Documents",
                "dst":"e:\\Documents"
            }
        },        
        { 
            "directory-copy":{ 
                "src":"d:\\Pictures", 
                "dst":"e:\\Pictures"
            }
        }
    ]
}
```