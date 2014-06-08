#!/usr/bin/env python
"""
This is a Titan module

- Analyze Git Repositories is to let the administrators
  know what data is checked out on a device in the event
  of a compromise or the misplacement of a device
"""

import re
import json
import logging
import subprocess
from sys import argv
from os import chmod
from time import time, gmtime, strftime
from os.path import isfile,dirname,basename

# Set Logging Status
logging_enabled = False

def run_command( command ):
	ps = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	output = ps.communicate()[0]
	return output

class AnalyzeGitCheckouts(object):
    """ AnalyzeGitCheckouts """

    def __init__(self):
        self.repos = {}

    def check_git_dirs(self):
        """
        Log all loaded kernel extensions
        """
        repos = run_command('find /Users -type d -name ".git"').splitlines()
       	for repo in repos:

       		repo_path = dirname(repo)
       		repo_git_path = repo
       		repo_name = basename(dirname(repo))

       		if logging_enabled:
       			print "Found '%s' @ '%s'" % (repo_name, repo_path)       		

       		self.repos[repo_path] = { 
       			'name': repo_name, 
       			'git_path': repo_git_path, 
	       		'branches': {
	       			'remote': [], 
	       			'local': [] 
	       		},
       		}
       		
       		local_branches = run_command("git --git-dir=%s --work-tree=%s branch" % (repo_git_path, repo_path))
       		for branch in local_branches.splitlines():

       			self.repos[repo_path]['branches']['local'].append(branch.lstrip())

       		remote_branches = run_command("git --git-dir=%s --work-tree=%s branch -r" % (repo_git_path, repo_path))
       		for branch in remote_branches.splitlines():
	   			self.repos[repo_path]['branches']['remote'].append(branch.lstrip())

       		most_recent_commit = run_command("git --git-dir=%s --work-tree=%s log -1 --oneline" % (repo_git_path, repo_path))
       		self.repos[repo_path]['commit'] = most_recent_commit

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_git_dirs()
        return json.dumps(self.repos)


if __name__ == "__main__":

    start = time()

    # the "exec_date" is used as the "date" field in the datastore
    exec_date = strftime("%a, %d %b %Y %H:%M:%S", gmtime())

    ###########################################################################
    # Gather data
    ###########################################################################
    try:
        a = AnalyzeGitCheckouts()
        if a is not None:
            print a.analyze()

    except Exception, error:
        print error

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
    	logging_enabled = True
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Execution took %s seconds.", str(end - start))
