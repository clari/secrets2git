Managing secrets correctly is a giant pain to get right.
secrets2git attempts to fix this by making secure management of secrets easy.

How?
secrets2git simply encrypts secrets into source.
Plus it uses [KMS](https://aws.amazon.com/kms/), so there are no shared passwords.

Setup
-----
1. Setup AWS keys if you haven't already

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
2. Add this submodule to your repo:
   
   `git submodule add git@github.com:clariussystems/secrets2git.git`

3. Run
 
   `./secrets2git/setup.sh`

4. `cp secrets2git/Secrets2GitConf.sample.py Secrets2GitConf.py` and set the values in `Secrets2GitConf.py` appropriately
5. Run `python secrets2git/secrets2git.py encrypt` to generate your encrypted files. Now you can add and commit
    the `*.encrypted` files (making sure to .gitignore the decrypted ones of course)!
6. Optionally create git hooks to automate decryption:

   ```bash
   # Make .git/hooks directory if it doesn't exist
   if [ ! -d ".git/hooks" ]; then
     mkdir .git/hooks
   fi
   echo python secrets2git/secrets2git.py decrypt >> .git/hooks/post-merge
   echo python secrets2git/secrets2git.py decrypt >> .git/hooks/post-rewrite
   ```

Encrypting new secrets
---------------------------------
`python secrets2git/secrets2git.py encrypt`


Deployment
----------
1. `git submodule update --init`
2. `python secrets2git.py decrypt`


**Deployment on with Docker and/or Kubernetes**
You don't actually need git to encrypt or decrypt. Just run the following in your `CMD` docker entrypoint with your AWS creds available:

`python secrets2git.py decrypt`

Seeing this you might ask if the project should be called `secrets2source` or something. I agree!

https://github.com/clari/secrets2git/issues/1


