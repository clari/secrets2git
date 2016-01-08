import os

# secrets2git configuration

# Everything in this file is okay to check-in to source control...
# that's the point!

# The KMS and Fernet keys can be part of your dev environment setup.
# So you should be able to create them once and reuse them for all projects
# within your team. They do not grant access to anything without AWS
# credentials.

# List the files you want to encrypt. These should also be in .gitignore.
# FILES_TO_ENCRYPT = []

# Create an AWS KMS key and put its ARN here:
# KMS_KEY_ID = 'arn:aws:kms:us-east-1:012345678910:key/deadbeef-dead-beef-beef-deadbeafdead'

# Optional AWS region if nothing set in ~/.aws/config
# REGION_NAME = 'us-east-1'

# Optional AWS keys if nothing set in ~/.aws/credentials
# AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', None)
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
