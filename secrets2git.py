# -*- coding: utf-8 -*-

import subprocess
import boto3
import os
from cryptography.fernet import Fernet

################################ CONFIG ########################################

# List the files you want to encrypt. These should also be in .gitignore.
FILES_TO_ENCRYPT = ['secrets.py']

FERNET_KEY_NAME = 'SECRETS2GIT_ENCRYPTED_FERNET_KEY_disabled'
KMS_KEY_ID_NAME = 'SECRETS2GIT_KMS_KEY_ID'

# Create an AWS KMS key and set it in your environment, i.e.;
# echo export SECRETS2GIT_KMS_KEY_ID=<YOUR-KMS-ARN> >> ~/.bash_profile
KMS_KEY_ID = os.environ.get(KMS_KEY_ID_NAME, None)

# Create a fernet key and set it in your environment, i.e.;
# Run this file without a key set
# echo export SECRETS2GIT_ENCRYPTED_FERNET_KEY=<YOUR-FERNET-KEY> >> ~/.bash_profile
FERNET_KEY = os.environ.get(FERNET_KEY_NAME, None)

# The KMS and Fernet keys can be part of your dev environment setup.
# So you should be able to create them once and reuse them for all projects
# within your team. They do not grant access to anything without AWS
# credentials.

# AWS region for KMS key
REGION_NAME = 'us-east-1'

# Make sure your AWS IAM credentials are set.
AWS_ACCESS_KEY_ID     = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

############################## END CONFIG ######################################

if FERNET_KEY is None:
    print(FERNET_KEY_NAME + ' is not set in your environment.')
    print('Do you want to create a new one?')
    answer = raw_input()
    if 'y' in answer:
        FERNET_KEY = Fernet.generate_key()
        set_key = '%s=%s' % (FERNET_KEY_NAME, FERNET_KEY)
        print('Add the following to your environment and rerun:')
        print('\t%s ' % set_key)
        print('i.e.')
        print('echo export %s >> ~/.bash_profile' % set_key)
    else:
        print('fail')
    exit(1)
elif KMS_KEY_ID_NAME is None:
    print(KMS_KEY_ID_NAME + ' is not set in your environment. '
        'You need to create an AWS KMS key for ultra-secure encryption.')
    exit(1)

client = boto3.client('kms', region_name=REGION_NAME,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

response = client.encrypt(
    KeyId=KMS_KEY_ID,
    Plaintext=FERNET_KEY)

for filename in FILES_TO_ENCRYPT:
    # TODO: Encrypt with fernet
    pass


# TODO: Get encryption key from KMS
# TODO: '' decrypts this file and stores it here on git pull - in dev and cloud
# TODO: '' encrypts this file and checks it in on git push
# TODO: Store encrypted_databag_secret in KMS.
# this file from mc ~/.dev-secrets/clarius_core/branch where branch defaults to master

# arn:aws:kms:us-east-1:374926383693:key/2382c5e6-c4b6-44da-bbc3-eb4e00e0578d
# arn:aws:kms:us-east-1:374926383693:key/2382c5e6-c4b6-44da-bbc3-eb4e00e0578d
# arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
