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
# from sys import argv
from time import time, gmtime, strftime
from os.path import dirname,basename

# Set Logging Status
logging_enabled = False

def run_command( command ):
  ps = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  output = ps.communicate()[0]
  return output

class AnalyzeGitCheckouts(object):
    """ AnalyzeGitCheckouts """

    def __init__(self):
        self.repos = []

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

          # Get latest commit
          most_recent_commit = run_command('git --git-dir="%s" --work-tree="%s"  log --pretty=format:"%%cd|[Commit: %%h] [Date: %%cd] [Commiter: %%cn] [Commiter Email: %%ce] [Message: %%s]" -1' % (repo_git_path, repo_path)).split("|", 1)

          commit_date = most_recent_commit[0]
          commit_details = most_recent_commit[1] 
           
          # Get remote
          remotes = run_command("git --git-dir=%s --work-tree=%s remote -v" % (repo_git_path, repo_path))

          # Append to master
          self.repos.append({
              "name": repo_name,
              "path": repo_path,
              "date": commit_date,
              "last_commit": commit_details,
              "remotes": remotes,
            })

        # Set Message
        self.message = "Found %d repositories" % len(self.repos)

        # If no issues, return 0
        self.status = 0

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_git_dirs()

        return json.JSONEncoder().encode({"status": self.status, "message": self.message,"response": self.repos})


if __name__ == "__main__":

    start = time()

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
    #if "--log" in argv[1:]:
    #  logging_enabled = True
    #  logging.basicConfig(format='%(message)s', level=logging.INFO)
    #  logging.info("Execution took %s seconds.", str(end - start))