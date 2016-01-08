Managing secrets correctly is a giant pain to get right.
secrets2git attempts to fix this by making secure management of secrets easy.

How?
secrets2git simply encrypts secrets into source.
Plus it uses [KMS](https://aws.amazon.com/kms/), so there are no shared passwords.

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
   
6. Setup AWS keys if you haven't already

   a. Go to [Users](https://console.aws.amazon.com/iam/home#users) in AWS
   
   b. Choose your IAM user name (not the check box).
   
   c. Choose the Security Credentials tab and then choose Create Access Key.

   d. To see your access key, choose Show User Security Credentials. Your credentials will look something like this:
      ```
      Access Key ID: AKIAIOSFODNN7EXAMPLE
      Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
      ```
      
   e. Place these credentials in a file called ~/.aws/credentials with the following format
      ```
      [default]
      aws_access_key_id=your_downloaded_key_id
      aws_secret_access_key=your_downloaded_key
      ```

Deployment
----------
1. Call `git submodule update --init`
2. Run `python secrets2git.py decrypt`

