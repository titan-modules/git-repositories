#!/usr/bin/env python
"""
This is the table definition 
for the git-repositories mod
"""

tables = {
	"git_repos" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "path" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "last_commit" : {
            "type" : "text",
            "default" : "NULL",
        },
        "remotes" : {
        	"type" : "text",
        	"default" : "NULL",
        }
    }
}