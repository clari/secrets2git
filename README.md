Managing secrets correctly is a giant pain to get right.
secrets2git attempts to fix that by making secure management of secrets easy.

How?
secrets2git simply encrypts secrets into source where they can be encrypted
and decrypted with git hooks.

KMS for encryption
secrets2git uses KMS to meet the most stringent compliance requirements and
ensure the master key is never stored or seen by anyone.

Setup
-----
1. Add this submodule to your repo:
   
   `git submodule add git@github.com:clariussystems/secrets2git.git`

2. Run
 
   `./setup.sh`

3. Copy Secrets2GitConf.sample.py to Secrets2GitConf.py in your root directory and set the values appropriately
4. Run `python secrets2git.py` to generate an encrypted key, then paste that key in your Secrets2GitConf.py
5. Optionally create a git hooks to automate encryption:
```bash
   # Make .git/hooks directory if it doesn't exist
   if [ ! -d ".git/hooks" ]; then
     mkdir .git/hooks
   fi
   echo python secrets2git.py decrypt >> .git/hooks/post-merge
   echo python secrets2git.py decrypt >> .git/hooks/post-rewrite
   echo python secrets2git.py encrypt >> .git/hooks/pre-push
```

Notes:
- Okay to require internet connection on git pull/push since git usually
  needs it anyway.
- Git submodule as a distribution mechanism, cuz it's Git!

